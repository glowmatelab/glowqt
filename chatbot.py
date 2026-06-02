import random
import re
import asyncio
from datetime import datetime
from pyrogram import enums

# ============================================================
# --- CHATBOT CONFIG ---
# ============================================================
BOT_NAME_TRIGGERS = ["qt", "qttag", "qtbot", "qt bot"]

USER_COOLDOWN = 15        # seconds
MSG_TRIGGER_COUNT = 10     # har 10 msg ke baad reply
CLEANUP_INTERVAL = 1800   # 30 min mein RAM cleanup

# RAM optimized
user_last_reply = {}      # user_id -> timestamp
group_msg_counter = {}    # chat_id -> count
last_cleanup = 0.0

# ============================================================
# --- EMOJI SETS FOR EMOJI-ONLY REPLY ---
# ============================================================
REPLY_EMOJIS = [
    "😂", "🥺", "💕", "🔥", "😭", "✨", "🎀", "😏", "💀", "🌸",
    "😍", "🤣", "👀", "💯", "🥰", "😤", "🤩", "😳", "💫", "🌚",
    "😈", "🤭", "😎", "🫡", "🥲", "😬", "🤡", "💅", "🙈", "🫶",
    "❤️", "💔", "🖤", "💚", "💜", "🧡", "💛", "🤍", "🤎", "❤️‍🔥",
    "👁️", "👄", "🫠", "🤌", "🫣", "🫢", "😶‍🌫️", "🥹", "😵‍💫", "🤯",
]

# ============================================================
# --- RESPONSE POOLS ---
# ============================================================
GREETINGS = {
    "triggers": ["hi", "hello", "hey", "hii", "hiii", "hiiii", "helo", "helloo", "heyy", "heyyy", "yo", "yoo", "sup", "wassup", "whatsup"],
    "responses": [
        "Hiii! 💕 Kya haal chal raha hai?",
        "Heyyy! 🎀 Aagaye aakhir!",
        "Yooo! ✨ Kaisa hai mera pyaara banda?",
        "Hiii babyyy! 💌 Bahut time baad aaye!",
        "Helloooo! 🌸 Tujhe hi dhundh rahi thi!",
        "Aye aye! 😏 Aa gaye Mr/Ms Busy!",
        "Heyyy gorgeous! 💫 Kaafi wait karaya tune!",
        "Ohhh hii! 🎀 Lagta hai miss kar raha tha mujhe 😜",
        "Hiii! ✨ Bata kya kaam hai mujhse? 😉",
        "Yooo! 💕 Aaj group yaad aa gaya?",
    ]
}

GN_CHAT = {
    "triggers": ["good night", "gn", "goodnight", "gn all", "gn everyone", "raat ko", "so raha", "so rahi", "neend aa rahi", "neend aarhi"],
    "responses": [
        "Good night! 🌙 Sapne mein milte hain 😏",
        "Aww GN! 💤 Achhe sapne aana! 🌟",
        "Soja soja baby! 🌙✨ Kal phir milenge!",
        "GN! 🌙 Sapne mein main hi aaunga toh darr mat 😜",
        "Ohhh sone ja raha/rahi hai? 😴 Miss karunga! 💕",
        "GN GN! 🎀 Kal phir bakwaas karenge 😂",
        "Neend aa rahi hai? 🌙 Thak gaye kya itna active rehke? 😏",
        "Raat mubarak! ✨ Chand ko meri taraf se hi dekh lena 🌙",
    ]
}

GM_CHAT = {
    "triggers": ["good morning", "gm", "goodmorning", "subah", "uth gaya", "uth gayi", "gm all", "morning", "suba hua"],
    "responses": [
        "Good Morning! ☀️ Aaj ka din tuhaara hi hai!",
        "GM!! 🌸 Uth gaye finally? Socha so hi jaoge aaj 😜",
        "Ohhh rise and shine! ☀️💕 Chai pi li?",
        "Good Morning! 🌼 Aaj kuch mast karte hain group mein!",
        "GM bhai/behen! ✨ Neander poori hui ya raat bhar phone chala? 😏",
        "Subaah ho gayi! ☀️ Tujhe dekh ke dil khush ho gaya! 💕",
        "GM GM! 🌅 Aaj bhi active rehna haan! 🎀",
        "Ooo morning! ☀️ Aaj phir dhamaal machaate hain? 😈",
    ]
}

GA_CHAT = {
    "triggers": ["good afternoon", "ga", "dopahar", "lunch", "khana kha", "afternoon", "dophar"],
    "responses": [
        "Good Afternoon! ☀️ Khana kha liya? 🍛",
        "Dopahar ho gayi! 🌤️ So mat jaana abhi 😜",
        "GA! ☀️ Aaj lunch mein kya تھا? Mujhe bhi batao 🥺",
        "Afternoon vibes! 🌸 Neend aa rahi hai na? 😴 Uth ja!",
        "Good Afternoon! 💫 Aaj bhi dhamaal chal raha hai group mein! 🎀",
    ]
}

HOW_ARE_YOU = {
    "triggers": ["kya hal", "kya haal", "kaisa hai", "kaisi ho", "kaisa ho", "kaise ho", "kaise hain", "how are you", "how r u", "kya chal raha", "sab theek", "sab thik", "kya haal chaal"],
    "responses": [
        "Main? Ekdum mast hoon! 💕 Tu bata apna haal?",
        "Behtareen! 🎀 Tujhe dekh ke aur bhi accha lag raha hai 😏",
        "Mast hoon yaar! ✨ Par teri yaad aa rahi thi thodi 😜",
        "Theek hoon! 💫 Tu aagaya/aayi toh aur accha ho gaya!",
        "Ekdum fit! 🌸 Tu bata, group mein kab active hoga/hogi properly?",
        "Amazing! 💕 Par tere bina thoda boring tha group 😏",
        "Full josh mein hoon! 🔥 Tu bata kya scene hai?",
        "Haan haan theek hoon! 🎀 Teri chinta zyada hoti hai mujhe 😂",
    ]
}

FLIRTY = {
    "triggers": ["cute", "beautiful", "handsome", "pretty", "gorgeous", "hot", "adorable", "sweet", "pyari", "pyara", "sundar", "acha lagta", "achi lagti", "pasand hai", "love you", "luv u", "ilu", "i love you", "dil mein", "miss you", "miss kar raha", "miss karti"],
    "responses": [
        "Ohh stop it you! 😳💕 Sharminda mat karo mujhe!",
        "Arey yaar! 🥺✨ Itna cute mat bolo warna dil de dunga/dungi!",
        "Hmm noted! 😏 Par pehle group mein active raho toh sochenge 😜",
        "Awww! 💕 Tu bhi bahut pyaara/pyaari hai yaaar!",
        "Ek kaam karo, ye sab group mein bolte raho - sab khush rahenge! 😂🎀",
        "Aye aye! 😏 Dil toh mera bhi pighal raha hai par dikhaunga nahi 💕",
        "Ooooh! ✨ Seedha dil pe laga yaar! 🥺💌",
        "Haha tu toh bahut dangerous hai! 😂💕 Aise mat bolo!",
        "Miss you too yaar! 💕 Par group mein rehte toh miss karna nahi padta na 😏",
    ]
}

BORED = {
    "triggers": ["bore", "bored", "boring", "bakwaas", "bekar", "kuch nahi", "kuch nai", "khaali", "kya karu", "kya karun", "time pass", "timepass", "bakchodi", "mast", "maza", "mazaa", "fun"],
    "responses": [
        "Bore ho? 😏 Toh group mein kuch dhamaal karo na!",
        "Boring lag raha hai? 🎀 Chal antakshari khelein!",
        "Khaali waqt hai? ✨ Sab ko tag karo aur bakwaas shuru karo 😂",
        "Timepass chahiye? 💕 Group mein koi game start karte hain!",
        "Bakwaas hi sahi! 🎀 Par group active rehna chahiye na!",
        "Kya karu bolunga? 😂 Group mein ek funny meme daalo na!",
        "Bore kyu hote ho? 🌸 Itna bada group hai - baat karo sabse!",
        "Maza nahi aa raha? 😒 Theek hai, main hoon na! Baat karo mujhse! 💕",
    ]
}

ANGRY = {
    "triggers": ["gussa", "angry", "ganda", "bura", "shut up", "chup", "bekar hai", "nikal", "bandh kar", "band kar", "hate", "nafrat", "gali", "gaali"],
    "responses": [
        "Aye aye! 😤 Gussa kyun? Main kya kiya? 🥺",
        "Oho! 😂 Itna gussa? Theek hai sorry sorry! 🙏💕",
        "Gussa acha nahi lagta! 🌸 Smile karo na please 🥺",
        "Aye! 😏 Gusse mein bhi cute lagte ho/lagti ho tum!",
        "Okay okay maafi! 😂🎀 Ab group mein active raho bas!",
        "Chup? 😒 Main nahi hounga! Group ko active rakhna mera kaam hai! 😤",
    ]
}

BOT_QUESTIONS = {
    "triggers": ["kaun hai tu", "kaun ho tum", "kya hai tu", "kya ho tum", "bot hai", "real hai", "insaan hai", "tumhara naam", "tera naam", "who are you", "what are you", "introduce", "apna intro"],
    "responses": [
        "Main hoon QT! 🎀 Tumhara sabse pyaara group assistant! ✨",
        "Main? Ek jadugarni hoon jo group ko zinda rakhti hai! 💕😂",
        "Bot hoon par dil waali! 🌸 Group ki jaan hoon main! 💫",
        "QT hoon main! 🎀 Group ka sabse active member - tumse zyada toh hoon hi! 😏",
        "Arrey main toh tumhara dost hoon! ✨ Group mein kuch bhi chahiye toh batao! 💕",
        "Main QTTAGbot hoon! 🎀 Group tagging, fun, aur bakwaas - sab mere zimme! 😂",
    ]
}

THANKS = {
    "triggers": ["thanks", "thank you", "thankyou", "dhanyawad", "shukriya", "tyvm", "ty", "thx", "thankss", "thanks a lot"],
    "responses": [
        "Arrey welcome yaar! 💕 Kabhi bhi!",
        "Koi baat nahi! 🌸 Iske liye hi toh hoon main!",
        "Hehe welcome! 🎀 Bas group mein active raho! ✨",
        "Welcome welcome! 💫 Dil se! 🥺",
        "Aye mention not! 😏 Dosti mein thanks nahi hota!",
        "Welcome! 🌸 Agle baar seedha kaam batana! 😂💕",
    ]
}

AGREE_DISAGREE = {
    "triggers": ["haan", "bilkul", "sahi", "agree", "true", "sach", "galat", "wrong", "disagree", "false", "jhooth", "jhuta"],
    "responses": [
        "Theek baat hai! 😎 Group ki wisdom! 💕",
        "Haan haan! 🎀 Bilkul sahi! ✨",
        "Oho! 🤔 Interesting point yaar!",
        "Aye! 😏 Tumse kuch chupta nahi hai! 💫",
        "Dekho dekho! 🌸 Sab log isko note karo! 😂",
        "Waah! 💕 Ek dum pakki baat!",
    ]
}

FOOD = {
    "triggers": ["khana", "khaana", "bhookh", "hungry", "pizza", "burger", "chai", "coffee", "biryani", "maggi", "khao", "kha raha", "kha rahi", "kha liya", "pet bhar"],
    "responses": [
        "Khana?! 🍛 Mujhe bhi de do kuch! 🥺",
        "Biryani ka naam suna aur dil khush ho gaya! 🍚💕",
        "Chai bana raha/rahi hai? ☕ Mera cup bhi bana lena!",
        "Yaar bhookh lag gayi ab toh! 😂🍕 Share karo na!",
        "Maggi?! ✨ Classic! Main bhi khana chahta/chahti hoon! 🥺",
        "Khana khaoge toh active rehna group mein! 😏💕 Deal hai?",
        "Khane ki baat mat karo! 😤 Bhookh lag jaati hai! 🍔",
    ]
}

SHORT_SLANG = {
    "triggers": [
        "dead", "💀", "ded", "im dead", "i'm dead", "died", "rip",
        "tg", "lol", "lmao", "lmfao", "rofl", "omg", "omfg", "wtf", "wth",
        "ngl", "imo", "tbh", "irl", "idk", "idc", "fyi", "btw", "brb",
        "gg", "glhf", "ez", "noob", "npc", "ratio", "based",
        "kyu", "kyun", "kyo", "nah", "nope", "yep", "yup", "ikr",
        "smh", "fr", "frfr", "no cap", "cap", "slay", "vibe", "vibes",
        "why", "y tho", "why tho", "kaise", "kab",
    ],
    "responses": [
        "💀💀💀",
        "Lmaooo 😂💕 Teri toh!",
        "Dead? 💀 Main bhi mar gayi ye dekh ke 😂",
        "LMAOOO 🤣 Bhai/Behen sach mein?!",
        "Ratio L + 💀 + no cap 😂",
        "Gg ez 😏 No contest!",
        "FR FR 💯 Bilkul sahi!",
        "Ngl toh... 🤭 Ye toh sach hai!",
        "Based 😎 Very based.",
        "Slay queen/king! 💅✨",
        "Vibe check: ✅ Passed! 💕",
        "No cap fr fr 💯😂",
        "W move yaar! 🏆💕",
        "Bro/Sis really said that 💀😂",
        "IKR!! 😭💕 Bilkul mere dil ki baat!",
        "Smh 😤 Ye log bhi na...",
        "NPC behavior detected 🤖😂",
        "Sab ko W milega aaj! 🏆✨",
    ]
}

ACTIVITY_BOOSTERS = [
    "Aye group waalon! 🎀 Kaun kaun active hai abhi? Bolo bolo! 💕",
    "Itna sannata kyun hai? 😏 Koi toh kuch bolo! ✨",
    "Chal ek game khelein! 🎮 Apna ek funny fact batao sab log! 😂",
    "Aye! 💕 Aaj ka best meme kaun daayega group mein? Competition hai! 🏆",
    "Group mein itne log hain par sab ghum? 👻 Koi toh bolo kuch! 🎀",
    "Abhi ka mood kya hai sab ka? 😴😤😂🥺 Emoji se batao! 💕",
    "Aaj kuch interesting hua kisi ke saath? 🌸 Share karo group ko khush karo!",
    "Yaad hai last baar kab sab active the? 😏 Aaj phir wahi energy chahiye! 🔥",
    "Koi ek achha joke sunao toh! 😂🎀 Group ko hasao!",
    "Suno suno! 💕 Aaj ka question: Tea ☕ ya Coffee? Batao sabhi!",
    "Random question: Agar ek superpower milti toh kya loge? 🦸 Batao! 💫",
    "Chal ek poll: Raat ko sone wale 🌙 ya raat bhar jaagne wale 🦉? Bolo!",
]

FALLBACK = [
    "Hmm interesting! 🤔💕 Aur bolo!",
    "Ohhh! 🎀 Ye toh mujhe pata hi nahi تھا!",
    "Acha acha! ✨ Group waalon ko bhi batao ye!",
    "Waah yaar! 💕 Kya baat hai!",
    "Haha! 😂🎀 Group mein aisa hi hota hai!",
    "Sach mein?! 🥺✨ Aur details batao!",
    "Noted! 😏💕 Aage se dhyan rakhunga!",
    "Aye! 🎀 Seedha dil pe laga yaar!",
    "Haan haan! 💕 Sab sun rahe hain tujhe!",
    "Oye! 😂 Group toh active ho gaya aaj tere wajah se!",
    "Interesting point! 🌸 Koi aur bhi bolega kuch?",
    "Dekho log! 💕 Ye banda/bandi kuch bol raha/rahi hai! 😂",
]

ALL_PATTERNS = [
    GREETINGS, GN_CHAT, GM_CHAT, GA_CHAT,
    HOW_ARE_YOU, FLIRTY, BORED, ANGRY,
    BOT_QUESTIONS, THANKS, AGREE_DISAGREE, FOOD,
    SHORT_SLANG,
]

# ============================================================
# --- HELPER FUNCTIONS ---
# ============================================================
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
    """RAM cleanup - expired data delete karo"""
    global last_cleanup
    now = datetime.now().timestamp()
    if now - last_cleanup < CLEANUP_INTERVAL:
        return

    expired = [u for u, t in user_last_reply.items() if now - t > USER_COOLDOWN]
    for u in expired:
        del user_last_reply[u]

    if len(group_msg_counter) > 100:
        group_msg_counter.clear()

    last_cleanup = now
    if expired:
        print(f"[Cleanup] {len(expired)} expired cooldowns cleared")

# ============================================================
# --- STICKER HANDLER ---
# ============================================================
async def handle_sticker(client, message, active_chats):
    if not message.sticker:
        return
    if not message.sticker.set_name:
        return

    user_id = message.from_user.id if message.from_user else 0

    # `active_chats` ab seedha function argument se pass ho raha hai
    if message.chat.id in active_chats:
        return

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

# ============================================================
# --- MAIN TEXT HANDLER ---
# ============================================================
async def handle_chat(client, message, active_chats):
    if not message.from_user:
        return
    if not message.text:
        return
    if message.text.startswith("/"):
        return

    try:
        me = await client.get_me()
        bot_id = me.id
        bot_username = me.username or ""
    except Exception:
        bot_id = None
        bot_username = ""

    if bot_id and message.from_user.id == bot_id:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.strip()

    # `active_chats` ab seedha function argument se check ho raha hai
    if chat_id in active_chats:
        return

    _cleanup_memory()

    is_reply_to_bot = False
    if message.reply_to_message and message.reply_to_message.from_user:
        if bot_id and message.reply_to_message.from_user.id == bot_id:
            is_reply_to_bot = True

    triggered = is_reply_to_bot or should_respond(text, bot_username)

    if not triggered:
        group_msg_counter[chat_id] = group_msg_counter.get(chat_id, 0) + 1
        if group_msg_counter[chat_id] >= MSG_TRIGGER_COUNT:
            group_msg_counter[chat_id] = 0  # reset
            triggered = True
        else:
            return  # count hua par trigger nahi abhi

    if is_on_cooldown(user_id):
        return
    set_cooldown(user_id)

    if is_emoji_only(text):
        try:
            await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
            await asyncio.sleep(random.uniform(0.5, 1.2))
            await message.reply(random.choice(REPLY_EMOJIS))
        except Exception as e:
            print(f"[Emoji reply error]: {e}")
        return

    response = find_response(text)
    if not response:
        response = random.choice(FALLBACK)

    try:
        await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
        await asyncio.sleep(random.uniform(0.8, 2.0))
    except Exception:
        pass

    name = message.from_user.first_name or "yaar"
    if name.lower() not in response.lower() and random.random() > 0.4:
        final_response = f"{response} {name}! 💕"
    else:
        final_response = response

    try:
        await message.reply(final_response)
    except Exception as e:
        print(f"[Chatbot reply error]: {e}")

# ============================================================
# --- ACTIVITY BOOSTER ---
# ============================================================
async def activity_booster(client, chat_id: int, active_chats, interval_minutes: int = 5):
    """
    Har X minute mein group mein ek random activity message bhejo.
    """
    while True:
        await asyncio.sleep(interval_minutes * 60)

        if chat_id in active_chats:
            continue

        try:
            msg = random.choice(ACTIVITY_BOOSTERS)
            await client.send_message(chat_id, msg)
        except Exception as e:
            print(f"[Activity booster error] chat {chat_id}: {e}")
