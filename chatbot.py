import random
import re
import asyncio
from datetime import datetime
from pyrogram import enums

# ============================================================
# --- CHATBOT CONFIG ---
# ============================================================
BOT_NAME_TRIGGERS = ["qt", "qttag", "qtbot", "qt bot"]

USER_COOLDOWN = 15
user_last_reply = {}  # user_id -> timestamp

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
        "Good Morning! ☀️ Aaj ka din tujhara hi hai!",
        "GM!! 🌸 Uth gaye finally? Socha so hi jaoge aaj 😜",
        "Ohhh rise and shine! ☀️💕 Chai pi li?",
        "Good Morning! 🌼 Aaj kuch mast karte hain group mein!",
        "GM bhai/behen! ✨ Neend poori hui ya raat bhar phone chala? 😏",
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
        "GA! ☀️ Aaj lunch mein kya tha? Mujhe bhi batao 🥺",
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

# --- SHORT SLANG / TG FAMOUS WORDS ---
SHORT_SLANG = {
    "triggers": [
        # death/reactions
        "dead", "💀", "ded", "im dead", "i'm dead", "died", "rip",
        # telegram short
        "tg", "lol", "lmao", "lmfao", "rofl", "omg", "omfg", "wtf", "wth",
        "ngl", "imo", "tbh", "irl", "idk", "idc", "fyi", "btw", "brb", "afk",
        "gg", "glhf", "ez", "noob", "npc", "ratio", "l", "w", "based",
        # hindi short
        "kyu", "kyun", "kyo", "nah", "nope", "yep", "yup", "ikr",
        "smh", "fr", "frfr", "no cap", "cap", "slay", "vibe", "vibes",
        # ban/kick related
        "ban", "banned", "kick", "kicked", "report", "spam",
        # why
        "why", "y tho", "why tho", "kaise", "kab",
        # all / n
        "n", "all", "everyone", "sab",
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
        "Ratio? Nahi hoga mujhe! 😤💕",
        "TG pe aisa hi hota hai yaar 😂🎀",
        "Kyu? Kyunki main hun na! 😏💕",
        "Ban? Kick? Yahan sab dost hain! 🌸",
        "Why tho 🤔 Main samjha nahi/samjhi nahi!",
        "IKR!! 😭💕 Bilkul mere dil ki baat!",
        "Smh 😤 Ye log bhi na...",
        "NPC behavior detected 🤖😂",
        "Sab ko W milega aaj! 🏆✨",
    ]
}

# --- ACTIVITY BOOSTERS ---
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

# --- FALLBACK ---
FALLBACK = [
    "Hmm interesting! 🤔💕 Aur bolo!",
    "Ohhh! 🎀 Ye toh mujhe pata hi nahi tha!",
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
# --- EMOJI ONLY MESSAGE DETECTOR ---
# ============================================================
def is_emoji_only(text: str) -> bool:
    """Check karo message sirf emoji hai ya nahi"""
    import unicodedata
    cleaned = text.strip()
    if not cleaned:
        return False
    for char in cleaned:
        cat = unicodedata.category(char)
        # So = Other Symbol (emoji category), Cf = Format chars (ZWJ etc)
        if cat not in ('So', 'Cf', 'Mn', 'Sk') and char not in (' ', '\u200d', '\ufe0f', '\u20e3'):
            return False
    return True

# ============================================================
# --- CORE MATCH FUNCTION ---
# ============================================================
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
    last = user_last_reply.get(user_id, 0)
    return (now - last) < USER_COOLDOWN

def set_cooldown(user_id: int):
    user_last_reply[user_id] = datetime.now().timestamp()

# ============================================================
# --- STICKER HANDLER ---
# ============================================================
async def handle_sticker(client, message):
    """
    Sticker aaye toh same pack se random sticker bhejo.
    main.py mein add karo:

        from chatbot import handle_sticker

        @app.on_message(filters.sticker & filters.group, group=3)
        async def sticker_reply(client, message):
            await handle_sticker(client, message)
    """
    if not message.sticker:
        return

    sticker = message.sticker
    set_name = sticker.set_name

    if not set_name:
        return

    # Cooldown check
    user_id = message.from_user.id if message.from_user else 0
    if is_on_cooldown(user_id):
        return

    try:
        # Same pack ke saare stickers fetch karo
        sticker_set = await client.get_sticker_set(set_name)
        all_stickers = sticker_set.stickers

        if not all_stickers:
            return

        # Random sticker choose karo (same sticker exclude karna optional)
        choices = [s for s in all_stickers if s.file_id != sticker.file_id]
        if not choices:
            choices = all_stickers

        chosen = random.choice(choices)

        # Typing jaisi feel ke liye thoda wait
        await asyncio.sleep(random.uniform(0.5, 1.5))

        set_cooldown(user_id)
        await message.reply_sticker(chosen.file_id)

    except Exception as e:
        print(f"[Sticker handler error]: {e}")


# ============================================================
# --- MAIN TEXT HANDLER ---
# ============================================================
async def handle_chat(client, message):
    """
    Main chatbot handler.

    main.py mein replace karo purana chatbot_reply:

        from chatbot import handle_chat, handle_sticker

        @app.on_message(filters.text & filters.group, group=3)
        async def chatbot_reply(client, message):
            await handle_chat(client, message)

        @app.on_message(filters.sticker & filters.group, group=3)
        async def sticker_reply(client, message):
            await handle_sticker(client, message)
    """
    if not message.from_user:
        return
    if not message.text:
        return
    if message.text.startswith("/"):
        return

    user_id = message.from_user.id
    text = message.text.strip()

    # Bot username
    try:
        me = await client.get_me()
        bot_username = me.username or ""
        bot_id = me.id
    except Exception:
        bot_username = ""
        bot_id = None

    # Reply to bot check
    is_reply_to_bot = False
    if message.reply_to_message and message.reply_to_message.from_user:
        if bot_id and message.reply_to_message.from_user.id == bot_id:
            is_reply_to_bot = True

    triggered = is_reply_to_bot or should_respond(text, bot_username)
    if not triggered:
        return

    # Cooldown
    if is_on_cooldown(user_id):
        return

    set_cooldown(user_id)

    # --- EMOJI ONLY MESSAGE ---
    if is_emoji_only(text):
        try:
            await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
            await asyncio.sleep(random.uniform(0.5, 1.2))
            reply_emoji = random.choice(REPLY_EMOJIS)
            await message.reply(reply_emoji)
        except Exception as e:
            print(f"[Emoji reply error]: {e}")
        return

    # --- NORMAL TEXT RESPONSE ---
    response = find_response(text)
    if not response:
        response = random.choice(FALLBACK)

    # Typing action
    try:
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        await asyncio.sleep(random.uniform(0.8, 2.0))
    except Exception:
        pass

    name = message.from_user.first_name or "yaar"
    # Name add karo agar response mein nahi hai
    if name.lower() not in response.lower() and random.random() > 0.4:
        final_response = f"{response} {name}! 💕"
    else:
        final_response = response

    try:
        await message.reply(final_response)
    except Exception as e:
        print(f"[Chatbot reply error]: {e}")


# ============================================================
# --- ACTIVITY BOOSTER (optional) ---
# ============================================================
async def activity_booster(client, chat_id: int, interval_minutes: int = 60):
    """
    Optional: Har X minute mein group mein ek random message bhejo.

    Usage in main.py:
        asyncio.create_task(activity_booster(app, YOUR_CHAT_ID, interval_minutes=60))
    """
    while True:
        await asyncio.sleep(interval_minutes * 60)
        try:
            msg = random.choice(ACTIVITY_BOOSTERS)
            await client.send_message(chat_id, msg)
        except Exception as e:
            print(f"[Activity booster error]: {e}")
