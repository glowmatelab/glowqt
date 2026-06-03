import random
import re
import asyncio
from datetime import datetime
from pyrogram import enums

BOT_NAME_TRIGGERS = ["qt", "qttag", "qtbot", "qt bot"]

USER_COOLDOWN = 15
MSG_TRIGGER_COUNT = 10
CLEANUP_INTERVAL = 1800
REPLY_CHANCE = 0.30

# Memory Storage
user_last_reply = {}
group_msg_counter = {}
group_last_activity = {}  # Tracks when a group last sent a message
last_cleanup = 0.0

REPLY_EMOJIS = [
    "😂", "🥺", "💕", "🔥", "😭", "✨", "🎀", "😏", "💀", "🌸",
    "😍", "🤣", "👀", "💯", "🥰", "😤", "🤩", "😳", "💫", "🌚",
    "😈", "🤭", "😎", "🫡", "🥲", "😬", "🤡", "💅", "🙈", "🫶",
    "❤️", "💔", "🖤", "💚", "💜", "🧡", "💛", "🤍", "🤎", "❤️‍🔥",
    "👁️", "👄", "🫠", "🤌", "🫣", "🫢", "😶‍🌫️", "🥹", "😵‍💫", "🤯",
]

# Note: Added {name} placeholder handling seamlessly inside responses dynamically
GREETINGS = {
    "triggers": ["hi", "hello", "hey", "hii", "hiii", "hiiii", "helo", "helloo", "heyy", "heyyy", "yo", "yoo", "sup", "wassup", "whatsup"],
    "responses": [
        "Hiii! 💕 Kya haal chal raha hai?",
        "Heyyy! 🎀 Aagaye aakhir!",
        "Yooo! ✨ Kaisa hai",
        "Hiii babyyy! 💌 Bahut time baad aaye!",
        "Helloooo! 🌸 Tujhe hi dhundh rahi thi!",
        "Aye aye! 😏 Aa gaye Mr/Ms Busy!",
        "Heyyy gorgeous! 💫 Kaafi wait karaya tune!",
    ]
}
# ... (Keep your other dictionaries GN_CHAT, GM_CHAT, etc. as they are)

FALLBACK = [
    "Hmm interesting! 🤔💕 Aur bolo!",
    "Ohhh! 🎀 Ye toh mujhe pata hi nahi tha!",
    "Acha acha! ✨ Group waalon ko bhi batao ye!",
    "Waah yaar! 💕 Kya baat hai!",
]

ACTIVITY_BOOSTERS = [
    "Aye group waalon! 🎀 Kaun kaun active hai abhi? Bolo bolo! 💕",
    "Itna sannata kyun hai? 😏 Koi toh kuch bolo! ✨",
    "Chal ek game khelein! 🎮 Apna ek funny fact batao sab log! 😂",
]

ALL_PATTERNS = [GREETINGS, FIXED_FALLBACK]  # Include all your pattern dicts here


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
    
    # Precise cleanup
    expired_users = [u for u, t in user_last_reply.items() if now - t > USER_COOLDOWN]
    for u in expired_users:
        del user_last_reply[u]
        
    # Drop stale group counters if inactive for over 2 hours to avoid unbounded dict growth
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

    try:
        sticker_set = await client.get_sticker_set(message.sticker.set_name)
        all_stickers = sticker_set.stickers
        if not all_stickers:
            return

        choices = [s for s in all_stickers if s.file_id != message.sticker.file_id]
        if not choices:
            choices = all_stickers

        await asyncio.sleep(random.uniform(0.5, 1.5))
        set_cooldown(user_id)
        await message.reply_sticker(random.choice(choices).file_id)
    except Exception as e:
        print(f"[Sticker handler error]: {e}")


async def handle_chat(client, message, active_chats):
    if not message.from_user or not message.text or message.text.startswith("/"):
        return

    try:
        me = await client.get_me()
        bot_id, bot_username = me.id, me.username or ""
    except Exception:
        bot_id, bot_username = None, ""

    if bot_id and message.from_user.id == bot_id:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.strip()

    if chat_id in active_chats:
        return

    _cleanup_memory()
    now = datetime.now().timestamp()
    group_last_activity[chat_id] = now  # Record activity update

    # Verify if it's a direct reply to the bot
    is_reply_to_bot = (
        message.reply_to_message and 
        message.reply_to_message.from_user and 
        bot_id and 
        message.reply_to_message.from_user.id == bot_id
    )

    triggered = is_reply_to_bot or should_respond(text, bot_username)

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

    # --- Case 1: Emoji only message ---
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

    # --- Case 2: Normal text message ---
    response = find_response(text) or random.choice(FALLBACK)

    # Context-aware structural string updates for user's name
    name = message.from_user.first_name or "yaar"
    if name.lower() not in response.lower() and random.random() > 0.4:
        # Prepend cleanly instead of breaking emoji chains at the end
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


# Centralized single background task loop for activity boosting
async def global_activity_booster(client, registered_chats: list, active_chats: set, interval_minutes: int = 5):
    """
    Pass your collection of group chat IDs to `registered_chats`.
    This single loop scales cleanly without spinning up tasks dynamically per group chat.
    """
    while True:
        await asyncio.sleep(interval_minutes * 60)
        for chat_id in registered_chats:
            if chat_id in active_chats:
                continue
            try:
                msg = random.choice(ACTIVITY_BOOSTERS)
                await client.send_message(chat_id, msg)
                await asyncio.sleep(0.5)  # Slight buffer delay to dodge Telegram flood-waits
            except Exception as e:
                print(f"[Activity booster error] chat {chat_id}: {e}")
