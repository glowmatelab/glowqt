import asyncio
import json
import os
import random
import re
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ChatMembersFilter, ParseMode
from pyrogram.errors import FloodWait
from datetime import datetime
from flask import Flask
from threading import Thread

# --- FLASK (Render alive rakhne ke liye) ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "QTTAGbot is alive! 🎀"

def run_flask():
    flask_app.run(host='0.0.0.0', port=8080)

Thread(target=run_flask, daemon=True).start()

# --- CONFIG (Environment Variables) ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID"))

app = Client("QTTAGbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- UNIFIED ACTIVE CHATS ---
active_chats = {}   # chat_id -> tag type string

# ============================================================
# --- DATABASE LOGIC ---
# ============================================================
DB_FILE = "qttag_data.json"

def load_data():
    if not os.path.exists(DB_FILE):
        return {
            "groups": [],
            "users": [],
            "custom_messages": {},
            "settings": {},
            "afk_users": {},
            "daily_couples": {}
        }
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            for key in ["groups", "users", "custom_messages", "settings", "afk_users", "daily_couples"]:
                if key not in data:
                    data[key] = [] if key in ["groups", "users"] else {}
            return data
    except:
        return {
            "groups": [],
            "users": [],
            "custom_messages": {},
            "settings": {},
            "afk_users": {},
            "daily_couples": {}
        }

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ============================================================
# --- CHATBOT RESPONSES ---
# ============================================================
exact_responses = {
    "hello": ["Hii babe! 💕 Kya haal?", "Helloooo! 🌸", "Hey sweetie! 💫"],
    "hi": ["Yoooo! 🎀 Wassup?", "Hii there! ✨", "Hiiii babyyy! 💌"],
    "hey": ["Heyyy! 💕 Kaisa hai?", "Hey gorgeous! 🌸", "Yooo! ✨"],
    "qt": ["Haan! 🎀 Main sun rahi hoon! 💕 Bol na!", "Hanji! ✨ Kya batt hai?", "Haan babe! 💫"],
    "bye": ["Bye bye! 👋💕 Jaldi aio!", "Take care! 🌸✨", "See you soon! 💫🎀"],
}

# ============================================================
# --- GM / GA / GN MESSAGES ---
# ============================================================
GM_MESSAGES = [
    "🌞 <b>Gᴏᴏᴅ Mᴏʀɴɪɴɢ</b> 🌼\n\n{mention}",
    "☕ <b>Rise and Shine!</b>\n\n{mention}",
    "🌄 <b>Sᴜʀᴀᴊ Nɪᴋʜʀᴀ, Tᴜᴍʜᴀʀᴀ Dɪɴ Sᴜʙʜ Hᴏ</b>\n\n{mention}",
    "🌻 <b>Nᴇᴇᴛʜ Kʜᴀᴛᴀᴍ, Aʙ Kᴀᴀᴍ Sʜᴜʀᴜ</b>\n\n{mention}",
    "💫 <b>Jᴀɢᴏ Mᴇʀᴇ Sʜᴇʀᴏ!</b>\n\n{mention}",
    "🕊️ <b>Sᴜᴋʜ Sᴀʙʜᴀ Gᴏᴏᴅ Mᴏʀɴɪɴɢ</b>\n\n{mention}",
    "🌅 <b>Nᴀʏɪ Sᴜʙᴀʜ, Nᴀʏᴇ Sᴀᴘɴᴇ</b>\n\n{mention}",
    "🌸 <b>Pʜᴜᴀʟᴏɴ Sᴇ Bʜᴀʀᴀ Yᴇʜ Sᴜʙᴀʜ</b>\n\n{mention}",
    "⭐ <b>Uᴛʜᴏ Mᴇʀᴇ Sɪᴛᴀʀᴏ, Dɪɴ Sᴜʜᴀᴠᴀɴᴀ Hᴏ</b>\n\n{mention}",
    "🌺 <b>Kʜᴜsʜɪʏᴏɴ Sᴇ Bʜᴀʀᴀ Hᴏ Yᴇʜ Dɪɴ</b>\n\n{mention}",
    "🦋 <b>Tɪᴛʟɪʏᴏɴ Kɪ Tᴀʀᴀʜ Uᴅᴏ Aᴀᴊ</b>\n\n{mention}",
    "🌈 <b>Rᴀɴɢ Bʜᴀʀᴀ Hᴏ Yᴇʜ Dɪɴ Tᴜᴍʜᴀʀᴀ</b>\n\n{mention}",
    "🎵 <b>Pᴀᴋsʜɪʏᴏɴ Kᴀ Gᴀᴀɴᴀ Sᴜɴᴋᴇ Uᴛʜᴏ</b>\n\n{mention}",
    "🌤️ <b>Dʜᴜᴀɴ Kᴀ Gɪʟᴀᴀs Aᴜʀ Tᴜᴍʜᴀʀɪ Hᴀɴsɪ</b>\n\n{mention}",
    "🌟 <b>Cʜᴀᴀɴᴅ Sɪᴛᴀʀᴇ Bᴏʟᴇ - Gᴏᴏᴅ Mᴏʀɴɪɴɢ</b>\n\n{mention}",
    "💐 <b>Hᴀʀ Kᴀᴀᴍ Mᴇɪɴ Kᴀᴀᴍʏᴀʙɪ Mɪʟᴇ</b>\n\n{mention}"
]

GA_MESSAGES = [
    "🌞 <b>Gᴏᴏᴅ Aғᴛᴇʀɴᴏᴏɴ</b> ☀️\n\n{mention}",
    "🍵 <b>Cʜᴀɪ Pɪ Lᴏ, Aғᴛᴇʀɴᴏᴏɴ Hᴏ Gᴀʏɪ</b>\n\n{mention}",
    "🌤️ <b>Hᴀʟᴋɪ Dᴏᴘʜᴀʀ, Aᴜʀ Tᴜᴍʜᴀʀᴀ Nᴀᴀᴍ</b> 💌\n\n{mention}",
    "😴 <b>Sᴏɴᴀ Mᴀᴛ, Kᴀᴀᴍ Kᴀʀᴏ</b> 😜\n\n{mention}",
    "📢 <b>Hᴇʏ Gᴏᴏᴅ Aғᴛᴇʀɴᴏᴏɴ!</b>\n\n{mention}",
    "🌅 <b>Dᴏᴘʜᴀʀ Kᴀ Sᴜʀᴀᴊ Tᴇᴢ Hᴀɪ</b>\n\n{mention}",
    "🥗 <b>Kʜᴀᴀɴᴀ Kʜᴀʏᴀ Kᴇ Nᴀʜɪ?</b>\n\n{mention}",
    "☀️ <b>Tᴇᴢ Dʜᴜᴀᴘ Mᴇɪɴ Tʜᴀɴᴅᴀ Pᴀᴀɴɪ Pɪʏᴏ</b>\n\n{mention}",
    "🌻 <b>Dᴏᴘʜᴀʀ Kᴀ Aʀᴀᴀᴍ Kᴀʀᴏ</b>\n\n{mention}",
    "🍃 <b>Pᴀᴘᴇᴅ Kᴇ Nᴇᴇᴄʜᴇ Bᴀɪᴛʜᴋᴇ Bᴀᴀᴛᴇɪɴ</b>\n\n{mention}",
    "🌸 <b>Lᴜɴᴄʜ Kᴀ Tɪᴍᴇ Hᴏ Gᴀʏᴀ</b>\n\n{mention}",
    "🦋 <b>Dᴏᴘʜᴀʀ Kɪ Mᴀsᴛɪ Kᴀʀᴏ</b>\n\n{mention}",
    "🍉 <b>Tᴀʀʙᴜᴊ Kʜᴀᴀᴋᴇ Tʜᴀɴᴅᴀ Hᴏ Jᴀᴏ</b>\n\n{mention}",
    "🌺 <b>Aᴀsᴍᴀɴ Bʜɪ Sᴀᴀғ Hᴀɪ Aᴀᴊ</b>\n\n{mention}",
    "🎵 <b>Gᴜɴɢᴜɴᴀᴛᴇ Hᴜᴇ Kᴀᴀᴍ Kᴀʀᴏ</b>\n\n{mention}",
    "🌈 <b>Rᴀɴɢ Bɪʀᴀɴɢᴀ Dᴏᴘʜᴀʀ</b>\n\n{mention}"
]

GN_MESSAGES = [
    "🌙 <b>Gᴏᴏᴅ Nɪɢʜᴛ</b>\n\n{mention}",
    "💤 <b>Sᴏɴᴇ Cʜᴀʟᴏ, Kʜᴀᴡᴀʙᴏɴ Mᴇɪɴ Mɪʟᴛᴇ Hᴀɪɴ</b> 😴\n\n{mention}",
    "🌌 <b>Aᴀsᴍᴀɴ Bʜɪ Sᴏ Gᴀʏᴀ, Aʙ Tᴜᴍʜɪ Bʜɪ Sᴏ Jᴀᴏ!</b>\n\n{mention}",
    "✨ <b>Rᴀᴀᴛ Kᴀ Sᴀᴋᴏᴏɴ Tᴜᴍʜᴇɪ Mɪʟᴇ</b>\n\n{mention}",
    "🌃 <b>Gᴏᴏᴅ Nɪɢʜᴛ & Sᴡᴇᴇᴛ Dʀᴇᴀᴍs</b>\n\n{mention}",
    "🌟 <b>Sɪᴛᴀʀᴏɴ Kᴇ Sᴀᴀᴛʜ Sᴏɴᴀ</b>\n\n{mention}",
    "🕊️ <b>Cᴀᴀɴᴅ Kɪ Rᴏsʜɴɪ Mᴇɪɴ Aᴀʀᴀᴀᴍ</b>\n\n{mention}",
    "🎭 <b>Sᴀᴘɴᴏɴ Kᴀ Rᴀᴀᴊᴀ Bᴀɴᴋᴇ Sᴏɴᴀ</b>\n\n{mention}",
    "🌺 <b>Rᴀᴀᴛ Kᴇ Pʜᴜᴀʟᴏɴ Sᴇ Mɪʟᴏ</b>\n\n{mention}",
    "💫 <b>Cʜᴀᴀɴᴅ Mᴀᴀᴍᴀ Kʜᴀᴀɴɪ Sᴜɴᴀᴛᴇ Hᴀɪɴ</b>\n\n{mention}",
    "🎵 <b>Lᴏʀɪ Kᴇ Sᴀᴀᴛʜ Sᴏɴᴀ</b>\n\n{mention}",
    "🌸 <b>Sᴀᴀʀᴇ Gᴀᴍ Bʜᴜᴀʟᴀᴋᴇ Sᴏɴᴀ</b>\n\n{mention}",
    "🦋 <b>Tɪᴛʟɪʏᴏɴ Kᴇ Sᴀᴀᴛʜ Sᴀᴘɴᴇ</b>\n\n{mention}",
    "🌈 <b>Rᴀɴɢ Bɪʀᴀɴɢᴇ Kʜᴀᴀʙ Dᴇᴋʜɴᴀ</b>\n\n{mention}",
    "🕯️ <b>Dɪʏᴇ Kɪ Rᴏsʜɴɪ Mᴇɪɴ Sᴏɴᴀ</b>\n\n{mention}",
    "🌅 <b>Kᴀʟ Pʜɪʀ Mɪʟᴇɴɢᴇ Sᴜʙᴀʜ</b>\n\n{mention}"
]

# ============================================================
# --- EMOJI SETS ---
# ============================================================
EMOJI = [
    "🦋🦋🦋🦋🦋",
    "🧚🌸🧋🍬🫖",
    "🥀🌷🌹🌺💐",
    "🌸🌿💮🌱🌵",
    "❤️💚💙💜🖤",
    "💓💕💞💗💖",
    "🌸💐🌺🌹🦋",
    "🍔🦪🍛🍲🥗",
    "🍎🍓🍒🍑🌶️",
    "🧋🥤🧋🥛🍷",
    "🍬🍭🧁🎂🍡",
    "🍨🧉🍺☕🍻",
    "🥪🥧🍦🍥🍚",
    "🫖☕🍹🍷🥛",
    "☕🧃🍩🍦🍙",
    "🍁🌾💮🍂🌿",
    "🌨️🌥️⛈️🌩️🌧️",
    "🌷🏵️🌸🌺💐",
    "💮🌼🌻🍀🍁",
    "🧟🦸🦹🧙👸",
    "🧅🍠🥕🌽🥦",
    "🐷🐹🐭🐨🐻‍❄️",
    "🦋🐇🐀🐈🐈‍⬛",
    "🌼🌳🌲🌴🌵",
    "🥩🍋🍐🍈🍇",
    "🍴🍽️🔪🍶🥃",
    "🕌🏰🏩⛩️🏩",
    "🎉🎊🎈🎂🎀",
    "🪴🌵🌴🌳🌲",
    "🎄🎋🎍🎑🎎",
    "🦅🦜🕊️🦤🦢",
    "🦤🦩🦚🦃🦆",
    "🐬🦭🦈🐋🐳",
    "🐔🐟🐠🐡🦐",
    "🦩🦀🦑🐙🦪",
    "🐦🦂🕷️🕸️🐚",
    "🥪🍰🥧🍨🍨",
    "🥬🍉🧁🧇🔮",
]

# ============================================================
# --- HELPER FUNCTIONS ---
# ============================================================
def clean_text(text):
    if not text:
        return ""
    return re.sub(r'([_*()~`>#+-=|{}.!])', r'\\\1', text)

async def is_admin(chat_id, user_id):
    admin_ids = [
        admin.user.id
        async for admin in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)
    ]
    return user_id in admin_ids

# ============================================================
# --- CORE EMOJI TAG ENGINE ---
# ============================================================
async def process_members(chat_id, members, text=None, replied=None):
    tagged_members = 0
    usernum = 0
    usertxt = ""
    emoji_sequence = random.choice(EMOJI)
    emoji_index = 0

    for member in members:
        if chat_id not in active_chats:
            break

        user = member.user if hasattr(member, 'user') else member
        if user.is_deleted or user.is_bot:
            continue

        tagged_members += 1
        usernum += 1

        emoji = emoji_sequence[emoji_index % len(emoji_sequence)]
        usertxt += f"[{emoji}](tg://user?id={user.id}) "
        emoji_index += 1

        if usernum == 5:
            try:
                if replied:
                    await replied.reply_text(usertxt, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
                else:
                    await app.send_message(chat_id, f"{text}\n{usertxt}", disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
                await asyncio.sleep(2)
                usernum = 0
                usertxt = ""
                emoji_sequence = random.choice(EMOJI)
                emoji_index = 0
            except FloodWait as e:
                await asyncio.sleep(e.value + 2)
            except Exception as e:
                await app.send_message(chat_id, f"⚠️ Error: {str(e)}")
                continue

    if usernum > 0 and chat_id in active_chats:
        try:
            if replied:
                await replied.reply_text(usertxt, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
            else:
                await app.send_message(chat_id, f"{text}\n\n{usertxt}", disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await app.send_message(chat_id, f"⚠️ Final batch error: {str(e)}")

    return tagged_members

# ============================================================
# --- GM/GA/GN ENGINE ---
# ============================================================
async def tag_users_greeting(chat_id, messages, tag_type):
    users = []
    async for member in app.get_chat_members(chat_id):
        if member.user.is_bot or member.user.is_deleted:
            continue
        users.append(member.user)

    for user in users:
        if chat_id not in active_chats:
            break
        mention = f"<b><a href='tg://user?id={user.id}'>{user.first_name}</a></b>"
        msg = random.choice(messages).format(mention=mention)
        await app.send_message(chat_id, msg, disable_web_page_preview=True)
        await asyncio.sleep(3)

    active_chats.pop(chat_id, None)
    await app.send_message(chat_id, f"✅ <b>{tag_type} Tᴀɢɢɪɴɢ Dᴏɴᴇ!</b>")

# ============================================================
# --- 1. GLOBAL TRACKING ---
# ============================================================
@app.on_message(group=-1)
async def track_everything(client, message):
    if not message.from_user:
        return
    data = load_data()
    changed = False
    if message.from_user.id not in data["users"]:
        data["users"].append(message.from_user.id)
        changed = True
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        if message.chat.id not in data["groups"]:
            data["groups"].append(message.chat.id)
            changed = True
    if changed:
        save_data(data)

# ============================================================
# --- 2. BASIC COMMANDS ---
# ============================================================
@app.on_message(filters.command("start"))
async def start(client, message):
    text = (
        "╔══════════════════════════════╗\n"
        "║            🎀 QTTAGbot v2.0  🎀   \n"
        "╚══════════════════════════════╝\n\n"
        "✨ **WELCOME USER!**\n"
        "Main hoon aapki stylish tagging assistant.\n\n"
        "🚀 **CORE FEATURES:**\n"
        "┣ ⚡ High-Speed Mentions\n"
        "┣ 🔥 Active Member Finder\n"
        "┣ 👑 Admin Power Tools\n"
        "┣ 🌙 AFK Status System\n"
        "┣ 🌅 GM/GA/GN Tagging\n"
        "┗ 💕 Couple Matcher (/couple)\n\n"
        "**Niche button se mujhe add karein!**"
    )
    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("➕ ADD TO YOUR GROUP ➕", url=f"https://t.me/{app.me.username}?startgroup=true")
    ]])
    await message.reply(text, reply_markup=buttons, parse_mode=enums.ParseMode.MARKDOWN)

@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    help_text = (
        "╔══════════════════════════════╗\n"
        "║        🎀 QTTAGbot HelpMsg 🎀  \n"
        "╚══════════════════════════════╝\n\n"
        "📂 **TAGGING ENGINE**\n"
        "┣ `/etag` → Emoji Tag (Clean) 🎨\n"
        "┣ `/mtag` → Mention Tag (Standard)\n"
        "┣ `/atag` → Admin Tag (Staff)\n"
        "┣ `/vtag` → Active Tag (Online)\n"
        "┣ `/all` → Tag All with Emoji\n"
        "┣ `/admintag` → Tag Admins with Emoji\n"
        "┗ `/stoptag` → Stop All Processes 🛑\n\n"
        "🌅 **GREETING TAGS**\n"
        "┣ `/gmtag` → Good Morning Tag ☀️\n"
        "┣ `/gatag` → Good Afternoon Tag 🌤️\n"
        "┣ `/gntag` → Good Night Tag 🌙\n"
        "┗ `/stopall` → Stop Greeting Tag 🛑\n\n"
        "🎭 **SOCIAL & FUN**\n"
        "┣ `/couple` → Match Maker 💞\n"
        "┣ `/afk [reason]` → Away Status 🌙\n"
        "┗ `/back` → Back from AFK 💌\n\n"
        "⚙️ **SYSTEM ADMIN**\n"
        "┣ `/stats` → Check Growth 📊\n"
        "┗ `/broadcast` → Global Broadcast 📢\n\n"
        "**Note:** Tagging commands ke liye Admin hona zaroori hai! ✨"
    )
    await message.reply(help_text, parse_mode=enums.ParseMode.MARKDOWN)

# ============================================================
# --- 3. AFK SYSTEM ---
# ============================================================
@app.on_message(filters.command("afk") & filters.group)
async def afk_set(client, message):
    user_id = str(message.from_user.id)
    data = load_data()
    reason = " ".join(message.command[1:]) or "AFK"
    data["afk_users"][user_id] = {
        "reason": reason,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "name": message.from_user.first_name
    }
    save_data(data)
    await message.reply(f"🌙 **{message.from_user.first_name}** AFK set!\n💬 Status: {reason}")

@app.on_message(filters.command("back") & filters.group)
async def afk_remove(client, message):
    user_id = str(message.from_user.id)
    data = load_data()
    if user_id in data["afk_users"]:
        del data["afk_users"][user_id]
        save_data(data)
        await message.reply(f"✅ **{message.from_user.first_name}** wapas aa gaya! 🎉")
    else:
        await message.reply(f"❌ {message.from_user.first_name} AFK tha hi nahi! 😏")

@app.on_message(filters.text & filters.group, group=1)
async def check_afk(client, message):
    data = load_data()
    user_id = str(message.from_user.id)

    if user_id in data["afk_users"] and not message.text.startswith("/afk"):
        afk_info = data["afk_users"][user_id]
        del data["afk_users"][user_id]
        save_data(data)
        await message.reply(
            f"✅ **{message.from_user.first_name}** wapas aa gaya! 🎉\n"
            f"⏰ AFK time: {afk_info['time']}"
        )

    if message.reply_to_message and message.reply_to_message.from_user:
        reply_user_id = str(message.reply_to_message.from_user.id)
        if reply_user_id in data["afk_users"]:
            afk_info = data["afk_users"][reply_user_id]
            await message.reply(
                f"🌙 **{afk_info['name']}** AFK hai!\n"
                f"💬 Status: {afk_info['reason']}\n"
                f"⏰ Since: {afk_info['time']}"
            )

# ============================================================
# --- 4. TAGGING ENGINES (etag/mtag/atag/vtag) ---
# ============================================================
@app.on_message(filters.command(["etag", "mtag", "atag", "vtag"]) & filters.group)
async def unified_tagger(client, message):
    chat_id = message.chat.id
    if chat_id in active_chats:
        return await message.reply("❌ Ek tag pehle se chal raha hai! `/stoptag` karo. 🎀")

    cmd = message.command[0]
    data = load_data()
    tag_msg = " ".join(message.command[1:]) or data["custom_messages"].get(str(chat_id), "Hello Everyone!")

    active_chats[chat_id] = cmd
    progress = await message.reply("⏳ Members fetch kar rahi hoon... 🎀")
    members = []

    try:
        if cmd == "atag":
            async for m in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                if not m.user.is_bot:
                    members.append(m.user)
        else:
            async for m in client.get_chat_members(chat_id):
                if not m.user.is_bot and not m.user.is_deleted:
                    if cmd == "vtag":
                        if m.user.status in [enums.UserStatus.ONLINE, enums.UserStatus.RECENTLY]:
                            members.append(m.user)
                    else:
                        members.append(m.user)
    except Exception as e:
        active_chats.pop(chat_id, None)
        return await progress.edit_text(f"❌ Error: {e}")

    if not members:
        active_chats.pop(chat_id, None)
        return await progress.edit_text("❌ Koi members nahi mile! 🎀")

    random.shuffle(members)
    total = len(members)

    if cmd == "etag":
        class FakeMember:
            def __init__(self, user): self.user = user
        fake_members = [FakeMember(u) for u in members]
        tagged = await process_members(chat_id, fake_members, text=tag_msg)
    else:
        for i in range(0, total, 5):
            if chat_id not in active_chats:
                break
            batch = members[i:i+5]
            mentions = ", ".join([f"[{u.first_name}](tg://user?id={u.id})" for u in batch])
            await client.send_message(chat_id, f"**{tag_msg}**\n\n{mentions}", parse_mode=enums.ParseMode.MARKDOWN)
            await asyncio.sleep(2)

    active_chats.pop(chat_id, None)
    await progress.edit_text(f"✅ Tagging Complete! 🎀\n📊 Total: {total}")

# ============================================================
# --- 5. ALL / ADMINTAG COMMANDS ---
# ============================================================
@app.on_message(filters.command(["all", "allmention", "mentionall", "tagall"]) & filters.group)
async def tag_all_users(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❌ Only admins can use this command.")

    chat_id = message.chat.id
    if chat_id in active_chats:
        return await message.reply_text("⚠️ Tagging already running. Use /stoptag to stop.")

    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        return await message.reply_text("Give some text: `/all Hi Friends`")

    members = []
    async for m in app.get_chat_members(chat_id):
        members.append(m)

    total_members = len(members)
    active_chats[chat_id] = "all"

    text = None
    if not replied:
        text = clean_text(message.text.split(None, 1)[1])

    tagged = await process_members(chat_id, members, text=text, replied=replied)
    active_chats.pop(chat_id, None)

    await app.send_message(chat_id, f"✅ Tagging completed!\n👥 Total: {total_members}\n✅ Tagged: {tagged}")

@app.on_message(filters.command(["admintag", "adminmention", "admins", "report"]) & filters.group)
async def tag_all_admins(client, message):
    if not message.from_user:
        return
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❌ Only admins can use this command.")

    chat_id = message.chat.id
    if chat_id in active_chats:
        return await message.reply_text("⚠️ Tagging already running. Use /stoptag to stop.")

    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        return await message.reply_text("Give some text: `/admintag Hi Admins`")

    members = []
    async for m in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        members.append(m)

    total_admins = len(members)
    active_chats[chat_id] = "admintag"

    text = None
    if not replied:
        text = clean_text(message.text.split(None, 1)[1])

    tagged = await process_members(chat_id, members, text=text, replied=replied)
    active_chats.pop(chat_id, None)

    await app.send_message(chat_id, f"✅ Admin tagging completed!\n👑 Total: {total_admins}\n✅ Tagged: {tagged}")

# ============================================================
# --- 6. GREETING TAGS (GM / GA / GN) ---
# ============================================================
@app.on_message(filters.command("gmtag") & filters.group)
async def gmtag(client, message):
    chat_id = message.chat.id
    if chat_id in active_chats:
        return await message.reply("⚠️ <b>Gᴏᴏᴅ Mᴏʀɴɪɴɢ Tᴀɢɢɪɴɢ Aʟʀᴇᴀᴅʏ Rᴜɴɴɪɴɢ.</b>")
    active_chats[chat_id] = "gmtag"
    await message.reply("☀️ <b>Gᴏᴏᴅ Mᴏʀɴɪɴɢ Tᴀɢɢɪɴɢ Sᴛᴀʀᴛᴇᴅ...</b>")
    asyncio.create_task(tag_users_greeting(chat_id, GM_MESSAGES, "Gᴏᴏᴅ Mᴏʀɴɪɴɢ"))

@app.on_message(filters.command("gatag") & filters.group)
async def gatag(client, message):
    chat_id = message.chat.id
    if chat_id in active_chats:
        return await message.reply("⚠️ <b>Aғᴛᴇʀɴᴏᴏɴ Tᴀɢɢɪɴɢ Aʟʀᴇᴀᴅʏ Oɴ.</b>")
    active_chats[chat_id] = "gatag"
    await message.reply("☀️ <b>Aғᴛᴇʀɴᴏᴏɴ Tᴀɢɢɪɴɢ Sᴛᴀʀᴛᴇᴅ...</b>")
    asyncio.create_task(tag_users_greeting(chat_id, GA_MESSAGES, "Aғᴛᴇʀɴᴏᴏɴ"))

@app.on_message(filters.command("gntag") & filters.group)
async def gntag(client, message):
    chat_id = message.chat.id
    if chat_id in active_chats:
        return await message.reply("⚠️ <b>Nɪɢʜᴛ Tᴀɢɢɪɴɢ Aʟʀᴇᴀᴅʏ Oɴ.</b>")
    active_chats[chat_id] = "gntag"
    await message.reply("🌙 <b>Nɪɢʜᴛ Tᴀɢɢɪɴɢ Sᴛᴀʀᴛᴇᴅ...</b>")
    asyncio.create_task(tag_users_greeting(chat_id, GN_MESSAGES, "Gᴏᴏᴅ Nɪɢʜᴛ"))

# ============================================================
# --- 7. STOP COMMANDS ---
# ============================================================
@app.on_message(filters.command(["stoptag", "stopall", "cancel", "stopmention", "cancelall"]) & filters.group)
async def stop_all(client, message):
    chat_id = message.chat.id
    if chat_id in active_chats:
        tag_type = active_chats.pop(chat_id)
        await message.reply(f"🛑 **{tag_type}** stopped! ✨")
    else:
        await message.reply("❌ Koi bhi tagging nahi chal rahi abhi!")

# ============================================================
# --- 8. COUPLE COMMAND ---
# ============================================================
@app.on_message(filters.command("couple") & filters.group)
async def couple_cmd(client, message):
    chat_id = str(message.chat.id)
    today = datetime.now().strftime("%Y-%m-%d")
    data = load_data()

    if chat_id in data["daily_couples"] and data["daily_couples"][chat_id].get("date") == today:
        saved = data["daily_couples"][chat_id]
        couple_msg = (
            "╔═══════════════════════════╗\n"
            "║       💝 TODAY'S COUPLE 💝      ║\n"
            "╚═══════════════════════════╝\n\n"
            f"👫 **{saved['couple1_name']}** ❤️ **{saved['couple2_name']}**\n\n"
            f"💖 Compatibility: **{saved['compatibility']}%**\n"
            f"🎀 Status: {get_couple_status(saved['compatibility'])}\n"
            f"✨ Matched on: {today}\n\n"
            f"💕 *Ye aaj ki special jodi hai!* 🌸"
        )
        return await message.reply(couple_msg)

    progress = await message.reply("💕 Aaj ki jodi dhundh rahi hoon... 🎀")
    members = []
    async for m in client.get_chat_members(message.chat.id):
        if not m.user.is_bot and not m.user.is_deleted:
            members.append(m.user)

    if len(members) < 2:
        return await progress.edit_text("❌ Kam se kam 2 active members chahiye! 🎀")

    c1, c2 = random.sample(members, 2)
    compatibility = random.randint(60, 100)

    data["daily_couples"][chat_id] = {
        "date": today,
        "couple1_id": c1.id,
        "couple1_name": c1.first_name,
        "couple2_id": c2.id,
        "couple2_name": c2.first_name,
        "compatibility": compatibility
    }
    save_data(data)

    couple_msg = (
        "╔══════════════════════╗\n"
        "║       💝 TODAY'S COUPLE 💝  \n"
        "╚══════════════════════╝\n\n"
        f"👫 {c1.mention} ❤️ {c2.mention}\n\n"
        f"💖 Compatibility: **{compatibility}%**\n"
        f"🎀 Status: {get_couple_status(compatibility)}\n"
        f"✨ Matched on: {today}\n\n"
        f"💕 *{get_couple_message(compatibility)}* 🌸"
    )
    await progress.edit_text(couple_msg)

def get_couple_status(compatibility):
    if compatibility >= 90: return "Perfect Match! 💯"
    elif compatibility >= 80: return "Soulmates! 💕"
    elif compatibility >= 70: return "Great Chemistry! ✨"
    else: return "Good Vibes! 🌸"

def get_couple_message(compatibility):
    messages = {
        90: ["Ye jodi toh jannat mein bani hai! 💫", "Made for each other! 👼", "Isse perfect aur kya! 🎯"],
        80: ["Chemistry toh dekho inki! 🔥", "Pyaar ho jayega pakka! 💘", "Couple goals! 🎀"],
        70: ["Sweet couple alert! 🍭", "Cute jodi ban gayi! 🌸", "Love is in the air! 💕"],
        60: ["Ek baar try toh karo! 💭", "Kuch special ho sakta hai! ✨", "Pyaar ka chance hai! 💌"]
    }
    for threshold in [90, 80, 70, 60]:
        if compatibility >= threshold:
            return random.choice(messages[threshold])
    return "Dekho kya hota hai! 🎲"

# ============================================================
# --- 9. ADMIN / OWNER COMMANDS ---
# ============================================================
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message):
    data = load_data()
    await message.reply(
        f"📊 **QTTAGbot Stats**\n\n"
        f"🏘️ Groups: `{len(data['groups'])}`\n"
        f"👤 Users: `{len(data['users'])}`\n"
        f"🌙 AFK Users: `{len(data['afk_users'])}`\n"
        f"💕 Daily Couples: `{len(data['daily_couples'])}`\n"
        f"🏷️ Active Tagging Chats: `{len(active_chats)}`"
    )

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a message to broadcast!")
    data = load_data()
    sent = 0
    msg = await message.reply(f"📢 Broadcasting to {len(data['groups'])} groups...")
    for gid in data["groups"]:
        try:
            await message.reply_to_message.copy(gid)
            sent += 1
            await asyncio.sleep(0.3)
        except:
            continue
    await msg.edit_text(f"✅ Broadcast Done!\n🚀 Sent to: {sent} groups.")

# ============================================================
# --- 10. CHATBOT (lowest priority) ---
# ============================================================
@app.on_message(filters.text & filters.group, group=3)
async def chatbot_reply(client, message):
    if message.text.startswith("/"):
        return
    msg = message.text.lower().strip()
    if msg in exact_responses:
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        await message.reply(f"{random.choice(exact_responses[msg])} {message.from_user.first_name}! 💕")

# ============================================================
# --- BOOT ---
# ============================================================
print("🌸 QTTAGbot LOADED! (Rank system removed - lightweight version) 🎀")
app.run()
