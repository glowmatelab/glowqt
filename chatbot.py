import random
import re
import asyncio
import json
from datetime import datetime
from pyrogram import enums

with open("responses.json", "r", encoding="utf-8") as f:
    data = json.load(f)

BOT_NAME_TRIGGERS = data["bot_name_triggers"]
REPLY_EMOJIS = data["reply_emojis"]
FALLBACK = data["fallback"]
ACTIVITY_BOOSTERS = data["activity_boosters"]
ALL_PATTERNS = list(data["patterns"].values())

USER_COOLDOWN = 15
MSG_TRIGGER_COUNT = 10
CLEANUP_INTERVAL = 1800
REPLY_CHANCE = 0.30

FILE_PHRASES = ["wah kya file hai", "mast cheez bheji hai bhai", "sahi hai, save kar leta hu", "ye file toh kaam ki lag rahi hai"]
AUDIO_PHRASES = ["kya mast audio he", "waah kya awaaz hai", "bhai maza aa gaya sunkar", "suno sab, kya mast audio hai"]
GIF_PHRASES = ["kya mast gif hai", "haha, sahi gif dhundha hai", "ye gif badhiya tha", "mast chal raha hai ye toh"]

user_last_reply = {}
group_msg_counter = {}
group_last_activity = {}
last_cleanup = 0.0

# ✅ Global bot info cache - sirf ek baar API call hoga
_bot_id = None
_bot_username = None

async def _get_bot_info(client):
    global _bot_id, _bot_username
    if _bot_id is None:
        me = await client.get_me()
        _bot_id = me.id
        _bot_username = me.username or ""
    return _bot_id, _bot_username


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
        if name in text_lower:
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

    last_cleanup = now


async def handle_sticker(client, message, active_chats):
    if not message.sticker or not message.sticker.set_name:
        return
    if message.chat.id in active_chats:
        return

    user_id = message.from_user.id if message.from_user else 0
    if is_on_cooldown(user_id):
        return

    # ✅ 40% chance reply, 60% ignore
    if random.random() > 0.40:
        return

    try:
        from pyrogram.raw.functions.messages import GetStickerSet
        from pyrogram.raw.types import InputStickerSetShortName
        from pyrogram.file_id import FileId, FileType, PHOTO_TYPES
        import base64

        raw_sticker_set = await client.invoke(
            GetStickerSet(
                stickerset=InputStickerSetShortName(
                    short_name=message.sticker.set_name
                ),
                hash=0
            )
        )

        all_stickers = raw_sticker_set.documents
        if not all_stickers:
            return

        choices = [s for s in all_stickers
                   if s.id != message.sticker.file_id]
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

        await message.reply_sticker(file_id)

    except Exception as e:
        print(f"[Sticker handler error]: {e}")

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
        try:
            await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
            await asyncio.sleep(random.uniform(0.8, 1.8))
            await message.reply(media_response)
        except Exception as e:
            print(f"[Media reply error]: {e}")
        return

    if not text:
        return

    # Emoji only check
    if is_emoji_only(text):
        try:
            await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
            await asyncio.sleep(random.uniform(0.5, 1.2))
            emoji_response = random.choice(REPLY_EMOJIS)
            if random.random() < REPLY_CHANCE:
                await message.reply(emoji_response)
            else:
                await client.send_message(chat_id, emoji_response)
        except Exception as e:
            print(f"[Emoji reply error]: {e}")
        return

    # Normal text response
    response = find_response(text) or random.choice(FALLBACK)

    name = message.from_user.first_name or "yaar"
    if name.lower() not in response.lower() and random.random() > 0.4:
        final_response = f"{name}, {response}"
    else:
        final_response = response

    try:
        await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
        await asyncio.sleep(random.uniform(0.8, 2.0))
        if random.random() < REPLY_CHANCE:
            await message.reply(final_response)
        else:
            await client.send_message(chat_id, final_response)
    except Exception as e:
        print(f"[Chatbot reply error]: {e}")


async def global_activity_booster(client, registered_chats: list, active_chats: dict, interval_minutes: int = 5):
    while True:
        await asyncio.sleep(interval_minutes * 60)
        for chat_id in registered_chats:
            if chat_id in active_chats:
                continue
            try:
                msg = random.choice(ACTIVITY_BOOSTERS)
                await client.send_message(chat_id, msg)
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"[Activity booster error] chat {chat_id}: {e}")
