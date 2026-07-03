import random
import re
import asyncio
import json
import logging
import time
from datetime import datetime
from pyrogram import enums
from pyrogram.errors import FloodWait

# ---------------------------------------------------------------------------
# Logging setup (replaces print statements)
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("chatbot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("chatbot")

# ---------------------------------------------------------------------------
# Load static response data
# ---------------------------------------------------------------------------
with open("responses.json", "r", encoding="utf-8") as f:
    data = json.load(f)

BOT_NAME_TRIGGERS = data["bot_name_triggers"]
REPLY_EMOJIS = data["reply_emojis"]
FALLBACK = data["fallback"]
ACTIVITY_BOOSTERS = data["activity_boosters"]
ALL_PATTERNS = list(data["patterns"].values())

# ---------------------------------------------------------------------------
# Load config (all tunable numbers live here now)
# ---------------------------------------------------------------------------
with open("config.json", "r", encoding="utf-8") as f:
    CFG = json.load(f)

USER_COOLDOWN = CFG["user_cooldown_seconds"]
MSG_TRIGGER_COUNT = CFG["msg_trigger_count"]
CLEANUP_INTERVAL = CFG["cleanup_interval_seconds"]
REPLY_CHANCE = CFG["text_reply_chance"]
STICKER_REPLY_CHANCE = CFG["sticker_reply_chance"]
MEDIA_REPLY_CHANCE = CFG["media_reply_chance"]
STICKER_CACHE_TTL = CFG["sticker_set_cache_ttl_seconds"]
QUIET_HOURS_ENABLED = CFG["quiet_hours_enabled"]
QUIET_HOURS_START = CFG["quiet_hours_start"]
QUIET_HOURS_END = CFG["quiet_hours_end"]

FILE_PHRASES = ["wah kya file hai", "mast cheez bheji hai bhai", "sahi hai, save kar leta hu", "ye file toh kaam ki lag rahi hai"]
AUDIO_PHRASES = ["kya mast audio he", "waah kya awaaz hai", "bhai maza aa gaya sunkar", "suno sab, kya mast audio hai"]
GIF_PHRASES = ["kya mast gif hai", "haha, sahi gif dhundha hai", "ye gif badhiya tha", "mast chal raha hai ye toh"]

user_last_reply = {}
group_msg_counter = {}
group_last_activity = {}
last_cleanup = 0.0

# ✅ Per-chat on/off toggle (in-memory). Wire a /chatbot on|off command to these.
disabled_chats = set()

def is_chatbot_enabled(chat_id: int) -> bool:
    return chat_id not in disabled_chats

def set_chatbot_enabled(chat_id: int, enabled: bool):
    if enabled:
        disabled_chats.discard(chat_id)
    else:
        disabled_chats.add(chat_id)

# ✅ Global bot info cache - sirf ek baar API call hoga
_bot_id = None
_bot_username = None

# ✅ Sticker set cache - {set_name: (documents, fetched_at_timestamp)}
_sticker_set_cache = {}


async def _get_bot_info(client):
    global _bot_id, _bot_username
    if _bot_id is None:
        me = await client.get_me()
        _bot_id = me.id
        _bot_username = me.username or ""
    return _bot_id, _bot_username


def _is_quiet_hours() -> bool:
    if not QUIET_HOURS_ENABLED:
        return False
    hour = datetime.now().hour
    if QUIET_HOURS_START <= QUIET_HOURS_END:
        return QUIET_HOURS_START <= hour < QUIET_HOURS_END
    # handles ranges that cross midnight, e.g. 23 -> 6
    return hour >= QUIET_HOURS_START or hour < QUIET_HOURS_END


def is_emoji_only(text: str) -> bool:
    import unicodedata
    cleaned = text.strip()
    if not cleaned:
        return False
    for char in cleaned:
        cat = unicodedata.category(char)
        if cat not in ('So', 'Cf', 'Mn', 'Sk') and char not in (' ', '\u200d', '\ufe0f', '\u20e3'):
            return False
    return True


def find_response(text: str):
    text_lower = text.lower().strip()
    clean = re.sub(r'[^\w\s]', '', text_lower)
    for pattern in ALL_PATTERNS:
        for trigger in pattern["triggers"]:
            if trigger in clean or trigger in text_lower:
                return random.choice(pattern["responses"])
    return None


def should_respond(text: str, bot_username: str) -> bool:
    text_lower = text.lower()
    for name in BOT_NAME_TRIGGERS:
        # ✅ word-boundary match instead of plain substring,
        # avoids false triggers like "moon" matching inside "moonlight"
        if re.search(rf'\b{re.escape(name.lower())}\b', text_lower):
            return True
    if bot_username and f"@{bot_username.lower()}" in text_lower:
        return True
    return False


def is_on_cooldown(user_id: int) -> bool:
    now = datetime.now().timestamp()
    return (now - user_last_reply.get(user_id, 0)) < USER_COOLDOWN


def set_cooldown(user_id: int):
    user_last_reply[user_id] = datetime.now().timestamp()


def _cleanup_memory():
    global last_cleanup
    now = datetime.now().timestamp()
    if now - last_cleanup < CLEANUP_INTERVAL:
        return

    expired_users = [u for u, t in user_last_reply.items() if now - t > USER_COOLDOWN]
    for u in expired_users:
        del user_last_reply[u]

    stale_groups = [g for g, t in group_last_activity.items() if now - t > 7200]
    for g in stale_groups:
        group_msg_counter.pop(g, None)
        group_last_activity.pop(g, None)

    # also trim stale sticker-set cache entries
    stale_sets = [s for s, (_, ts) in _sticker_set_cache.items() if now - ts > STICKER_CACHE_TTL]
    for s in stale_sets:
        _sticker_set_cache.pop(s, None)

    last_cleanup = now


async def _safe_call(coro_factory, *, retries: int = 2):
    """
    Runs an API call and automatically waits out FloodWait errors instead
    of just failing. coro_factory is a zero-arg function returning a fresh
    coroutine each time (since a coroutine can't be awaited twice).
    """
    for attempt in range(retries + 1):
        try:
            return await coro_factory()
        except FloodWait as e:
            wait_for = e.value + 1
            logger.warning(f"FloodWait hit, sleeping {wait_for}s (attempt {attempt + 1}/{retries + 1})")
            await asyncio.sleep(wait_for)
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return None
    logger.error("API call failed after retries (repeated FloodWait)")
    return None


async def handle_sticker(client, message, active_chats):
    if not message.sticker or not message.sticker.set_name:
        return
    if message.chat.id in active_chats:
        return
    if not is_chatbot_enabled(message.chat.id):
        return
    if _is_quiet_hours():
        return

    user_id = message.from_user.id if message.from_user else 0
    if is_on_cooldown(user_id):
        return

    # ✅ configurable chance (default 1% reply, 99% ignore)
    if random.random() > STICKER_REPLY_CHANCE:
        return

    try:
        from pyrogram.raw.functions.messages import GetStickerSet
        from pyrogram.raw.types import InputStickerSetShortName
        from pyrogram.file_id import FileId, FileType

        set_name = message.sticker.set_name
        now = time.time()

        # ✅ use cached sticker set if fetched recently, avoids repeat API calls
        cached = _sticker_set_cache.get(set_name)
        if cached and (now - cached[1]) < STICKER_CACHE_TTL:
            all_stickers = cached[0]
        else:
            raw_sticker_set = await _safe_call(
                lambda: client.invoke(
                    GetStickerSet(
                        stickerset=InputStickerSetShortName(short_name=set_name),
                        hash=0
                    )
                )
            )
            if raw_sticker_set is None:
                return
            all_stickers = raw_sticker_set.documents
            _sticker_set_cache[set_name] = (all_stickers, now)

        if not all_stickers:
            return

        choices = [s for s in all_stickers if s.id != message.sticker.file_id]
        if not choices:
            choices = all_stickers

        random_doc = random.choice(choices)

        await asyncio.sleep(random.uniform(0.5, 1.5))
        set_cooldown(user_id)

        file_id = FileId(
            file_type=FileType.STICKER,
            dc_id=random_doc.dc_id,
            media_id=random_doc.id,
            access_hash=random_doc.access_hash,
            file_reference=random_doc.file_reference,
        ).encode()

        await _safe_call(lambda: message.reply_sticker(file_id))

    except Exception as e:
        logger.error(f"Sticker handler error: {e}")


async def handle_chat(client, message, active_chats):
    if not message.from_user:
        return

    if message.text and message.text.startswith("/"):
        return

    # ✅ Cached - flood wait nahi aayega
    bot_id, bot_username = await _get_bot_info(client)

    if message.from_user.id == bot_id:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id in active_chats:
        return
    if not is_chatbot_enabled(chat_id):
        return

    _cleanup_memory()
    now = datetime.now().timestamp()
    group_last_activity[chat_id] = now

    is_media = message.document or message.audio or message.voice or message.animation

    is_reply_to_bot = (
        message.reply_to_message and
        message.reply_to_message.from_user and
        bot_id and
        message.reply_to_message.from_user.id == bot_id
    )

    text = message.text.strip() if message.text else ""
    triggered = is_reply_to_bot or (text and should_respond(text, bot_username)) or is_media

    if not triggered:
        group_msg_counter[chat_id] = group_msg_counter.get(chat_id, 0) + 1
        if group_msg_counter[chat_id] >= MSG_TRIGGER_COUNT:
            group_msg_counter[chat_id] = 0
            triggered = True
        else:
            return

    if _is_quiet_hours():
        return

    if is_on_cooldown(user_id):
        return
    set_cooldown(user_id)

    # Media handling
    media_response = None
    if message.document:
        media_response = random.choice(FILE_PHRASES)
    elif message.audio or message.voice:
        media_response = random.choice(AUDIO_PHRASES)
    elif message.animation:
        media_response = random.choice(GIF_PHRASES)

    if media_response:
        # ✅ media replies now respect a probability too, not guaranteed every time
        if random.random() > MEDIA_REPLY_CHANCE:
            return
        try:
            await _safe_call(lambda: client.send_chat_action(chat_id, enums.ChatAction.TYPING))
            await asyncio.sleep(random.uniform(0.8, 1.8))
            await _safe_call(lambda: message.reply(media_response))
        except Exception as e:
            logger.error(f"Media reply error: {e}")
        return

    if not text:
        return

    # Emoji only check
    if is_emoji_only(text):
        try:
            await _safe_call(lambda: client.send_chat_action(chat_id, enums.ChatAction.TYPING))
            await asyncio.sleep(random.uniform(0.5, 1.2))
            emoji_response = random.choice(REPLY_EMOJIS)
            if random.random() < REPLY_CHANCE:
                await _safe_call(lambda: message.reply(emoji_response))
            else:
                await _safe_call(lambda: client.send_message(chat_id, emoji_response))
        except Exception as e:
            logger.error(f"Emoji reply error: {e}")
        return

    # Normal text response
    response = find_response(text) or random.choice(FALLBACK)

    name = message.from_user.first_name or "yaar"
    if name.lower() not in response.lower() and random.random() > 0.4:
        final_response = f"{name}, {response}"
    else:
        final_response = response

    try:
        await _safe_call(lambda: client.send_chat_action(chat_id, enums.ChatAction.TYPING))
        await asyncio.sleep(random.uniform(0.8, 2.0))
        if random.random() < REPLY_CHANCE:
            await _safe_call(lambda: message.reply(final_response))
        else:
            await _safe_call(lambda: client.send_message(chat_id, final_response))
    except Exception as e:
        logger.error(f"Chatbot reply error: {e}")


async def simple_welcome(client, message):
    bot_id, _ = await _get_bot_info(client)
    for member in message.new_chat_members:
        if member.id == bot_id:
            try:
                await _safe_call(lambda: client.send_message(
                    message.chat.id,
                    "Shukriya group me add karne ke liye! Main Apki group active rakhungi. by tagging people 😎"
                ))
            except Exception as e:
                logger.error(f"Bot welcome error: {e}")
            continue
        user_mention = f"<a href='tg://user?id={member.id}'>{member.first_name}</a>"
        try:
            await _safe_call(lambda: client.send_message(
                message.chat.id,
                f"Welcome ji {user_mention} 🎉",
                parse_mode=enums.ParseMode.HTML
            ))
        except Exception as e:
            logger.error(f"Welcome error: {e}")


async def global_activity_booster(client, registered_chats: list, active_chats: dict, interval_minutes: int = 5):
    while True:
        await asyncio.sleep(interval_minutes * 60)
        if _is_quiet_hours():
            continue
        for chat_id in registered_chats:
            if chat_id in active_chats:
                continue
            if not is_chatbot_enabled(chat_id):
                continue
            try:
                msg = random.choice(ACTIVITY_BOOSTERS)
                await _safe_call(lambda: client.send_message(chat_id, msg))
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Activity booster error chat {chat_id}: {e}")
