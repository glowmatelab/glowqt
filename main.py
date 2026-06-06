import asyncio
import json
import os
import random
import re
import sys
import httpx
from datetime import datetime
from threading import Thread
from flask import Flask
# Custom Modules

from chatbot import handle_chat, handle_sticker, simple_welcome
from messages import GM_MESSAGES, GA_MESSAGES, GN_MESSAGES, EMOJI
# Pyrogram Main Imports
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait


async def bot_api(method, **kwargs):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/{method}",
            json=kwargs
        )
        return resp.json()
# ============================================================
# --- FLASK ---
# ============================================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "QTTAGbot is alive! 🎀"

def run_flask():
    try:
        flask_app.run(host='0.0.0.0', port=8080)
    except Exception as e:
        print(f"[Flask Error]: {e}")

Thread(target=run_flask, daemon=True).start()

# ============================================================
# --- CONFIG ---
# ============================================================
API_ID    = int(os.environ.get("API_ID"))
API_HASH  = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID  = int(os.environ.get("OWNER_ID"))

app = Client(
    "QTTAGbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    sleep_threshold=60,
    max_concurrent_transmissions=2,
)

# ============================================================
# --- UNIFIED ACTIVE CHATS ---
# ============================================================
active_chats = {}

# ============================================================
# --- DATABASE LOGIC ---
# ============================================================
DB_FILE   = "qttag_data.json"
data_lock = asyncio.Lock()

def _default_data():
    return {
        "groups": [],
        "users": [],
        "custom_messages": {},
        "settings": {},
        "afk_users": {},
    }

def load_data():
    if not os.path.exists(DB_FILE):
        return _default_data()
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
        for key, default in _default_data().items():
            if key not in data:
                data[key] = default
        return data
    except Exception as e:
        print(f"[DB load error]: {e}")
        return _default_data()

def save_data(data):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[DB save error]: {e}")

async def load_data_safe():
    async with data_lock:
        return load_data()

async def save_data_safe(data):
    async with data_lock:
        save_data(data)

# ============================================================
# --- HELPER FUNCTIONS ---
# ============================================================
def clean_text(text):
    if not text:
        return ""
    return re.sub(r'([_*()~`>#+=|{}.!])', r'\\\1', text)

async def is_admin(chat_id, user_id):
    try:
        admin_ids = [
            admin.user.id
            async for admin in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)
        ]
        return user_id in admin_ids
    except Exception as e:
        print(f"[is_admin error]: {e}")
        return False

# ============================================================
# --- SAFE SEND HELPER ---
# ============================================================
async def safe_send(chat_id, text, replied=None, retries=3):
    for attempt in range(retries):
        try:
            if replied:
                await replied.reply_text(
                    text,
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.MARKDOWN,
                )
            else:
                await app.send_message(
                    chat_id,
                    text,
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.MARKDOWN,
                )
            return True

        except FloodWait as e:
            wait = e.value + 2
            print(f"[FloodWait] {wait}s — chat {chat_id}")
            await asyncio.sleep(wait)

        except (PyroConnectionError, OSError, ConnectionResetError, BrokenPipeError) as e:
            wait = 5 * (attempt + 1)
            print(f"[Network Error] Attempt {attempt+1}/{retries}: {e} — waiting {wait}s")
            await asyncio.sleep(wait)

        except Exception as e:
            print(f"[safe_send unknown error]: {e}")
            await asyncio.sleep(2)
            return False

    print(f"[safe_send] All {retries} attempts failed for chat {chat_id}")
    return False

# ============================================================
# --- CORE EMOJI TAG ENGINE (5 batch) ---
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
            payload = usertxt
            if not replied and text:
                payload = f"{text}\n{usertxt}"

            success = await safe_send(chat_id, payload, replied=replied)
            if not success:
                active_chats.pop(chat_id, None)
                try:
                    await app.send_message(chat_id, "⚠️ Network error aayi, tagging rok di.")
                except Exception:
                    pass
                return tagged_members

            usernum = 0
            usertxt = ""
            emoji_sequence = random.choice(EMOJI)
            emoji_index = 0
            await asyncio.sleep(2)

    if usernum > 0 and chat_id in active_chats:
        payload = usertxt
        if not replied and text:
            payload = f"{text}\n\n{usertxt}"
        await safe_send(chat_id, payload, replied=replied)

    return tagged_members

# ============================================================
# --- SINGLE TAG ENGINE (human style) ---
# ============================================================
async def process_members_single(chat_id, members, text=None, replied=None):
    tagged_members = 0

    for member in members:
        if chat_id not in active_chats:
            break

        user = member.user if hasattr(member, 'user') else member
        if user.is_deleted or user.is_bot:
            continue

        tagged_members += 1
        emoji = random.choice(random.choice(EMOJI))
        mention = f"[{emoji} {user.first_name}](tg://user?id={user.id})"

        try:
            await app.send_chat_action(chat_id, enums.ChatAction.TYPING)
        except Exception:
            pass

        await asyncio.sleep(random.uniform(1.0, 2.5))

        payload = mention
        if text and tagged_members == 1:
            payload = f"{text}\n{mention}"

        success = await safe_send(
            chat_id,
            payload,
            replied=replied if tagged_members == 1 else None
        )

        if not success:
            active_chats.pop(chat_id, None)
            try:
                await app.send_message(chat_id, "⚠️ Network error, tagging rok di.")
            except Exception:
                pass
            return tagged_members

        await asyncio.sleep(random.uniform(2.0, 4.0))

    return tagged_members

# ============================================================
# --- GM/GA/GN ENGINE ---
# ============================================================
async def tag_users_greeting(chat_id, messages, tag_type):
    users = []
    try:
        async for member in app.get_chat_members(chat_id):
            if member.user.is_bot or member.user.is_deleted:
                continue
            users.append(member.user)
    except Exception as e:
        print(f"[tag_users_greeting fetch error]: {e}")
        active_chats.pop(chat_id, None)
        return

    for user in users:
        if chat_id not in active_chats:
            break
        try:
            mention = f"<b><a href='tg://user?id={user.id}'>{user.first_name}</a></b>"
            msg = random.choice(messages).format(mention=mention)
            await app.send_message(chat_id, msg, disable_web_page_preview=True)
            await asyncio.sleep(3)

        except FloodWait as e:
            await asyncio.sleep(e.value + 2)

        except (PyroConnectionError, OSError, ConnectionResetError, BrokenPipeError) as e:
            print(f"[Greeting network error]: {e}")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"[Greeting unknown error]: {e}")
            await asyncio.sleep(2)

    active_chats.pop(chat_id, None)
    try:
        await app.send_message(chat_id, f"✅ <b>{tag_type} Tᴀɢɢɪɴɢ Dᴏɴᴇ!</b>")
    except Exception:
        pass

async def safe_task(coro, chat_id, tag_type):
    try:
        await coro
    except Exception as e:
        print(f"[Task crashed] {tag_type} in {chat_id}: {e}")
        active_chats.pop(chat_id, None)
        try:
            await app.send_message(chat_id, f"⚠️ {tag_type} tagging crash ho gayi.")
        except Exception:
            pass

# ============================================================
# --- 1. GLOBAL TRACKING ---
# ============================================================
@app.on_message(group=-1)
async def track_everything(client, message):
    if not message.from_user:
        return
    try:
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
    except Exception as e:
        print(f"[track_everything error]: {e}")

# ============================================================
# --- 2. BASIC COMMANDS ---
# ============================================================
@app.on_message(filters.command("start"))
async def start(client, message):
    from messages import START_TEXT
    IMAGE_URL = "https://drive.google.com/uc?id=1kwp3goeP34VFNq89Ew0PAsVqG8MJEBsj"
    me = await client.get_me()
    await bot_api(
        "sendPhoto",
        chat_id=message.chat.id,
        photo=IMAGE_URL,
        caption=START_TEXT,
        parse_mode="HTML",
        reply_markup={
            "inline_keyboard": [[
                {"text": "➕ ADD TO YOUR GROUP ➕", "url": f"https://t.me/{me.username}?startgroup=true"}
            ]]
        }
    )

@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    from messages import HELP_TEXT
    me = await client.get_me()
    await bot_api(
        "sendMessage",
        chat_id=message.chat.id,
        text=HELP_TEXT,
        parse_mode="HTML",
        reply_markup={
            "inline_keyboard": [
                [
                    {"text": "➕ ADD TO GROUP", "url": f"https://t.me/{me.username}?startgroup=true"},
                    {"text": "💬 SUPPORT", "url": "https://t.me/galaxysupportteam"}
                ],
                [
                    {"text": "📢 BOT CHANNEL", "url": "https://t.me/galaxy_bots_update"}
                ]
            ]
        }
    )

# ============================================================
# --- 3. AFK SYSTEM ---
# ============================================================
@app.on_message(filters.command("afk") & filters.group)
async def afk_set(client, message):
    user_id = str(message.from_user.id)
    data = await load_data_safe()
    reason = " ".join(message.command[1:]) or "AFK"
    data["afk_users"][user_id] = {
        "reason": reason,
        "time":   datetime.now().strftime("%Y-%m-%d %H:%M"),
        "name":   message.from_user.first_name,
    }
    await save_data_safe(data)
    await message.reply(f"🌙 **{message.from_user.first_name}** AFK set!\n💬 Status: {reason}")

@app.on_message(filters.command("back") & filters.group)
async def afk_remove(client, message):
    user_id = str(message.from_user.id)
    data = await load_data_safe()
    if user_id in data["afk_users"]:
        del data["afk_users"][user_id]
        await save_data_safe(data)
        await message.reply(f"✅ **{message.from_user.first_name}** wapas aa gaya! 🎉")
    else:
        await message.reply(f"❌ {message.from_user.first_name} AFK tha hi nahi! 😏")

@app.on_message(filters.text & filters.group, group=1)
async def check_afk(client, message):
    if not message.from_user:
        return
    data = await load_data_safe()
    user_id = str(message.from_user.id)

    if user_id in data["afk_users"] and not message.text.startswith("/afk"):
        afk_info = data["afk_users"].pop(user_id)
        await save_data_safe(data)
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
# --- 4. TAGGING ENGINES ---
# ============================================================
@app.on_message(filters.command(["etag", "mtag", "atag", "vtag"]) & filters.group)
async def unified_tagger(client, message):
    chat_id = message.chat.id

    if not await is_admin(chat_id, message.from_user.id):
        return await message.reply("❌ Only admins can use tagging commands! 👑")

    if chat_id in active_chats:
        return await message.reply("❌ Ek tag pehle se chal raha hai! `/stoptag` karo. 🎀")

    cmd     = message.command[0]
    data    = load_data()
    tag_msg = " ".join(message.command[1:]) or data["custom_messages"].get(str(chat_id), "Hello Everyone!")

    active_chats[chat_id] = cmd
    progress = await message.reply("⏳ Members fetch kar rahi hoon... 🎀")
    members  = []

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
        return await progress.edit_text(f"❌ Members fetch error: {e}")

    if not members:
        active_chats.pop(chat_id, None)
        return await progress.edit_text("❌ Koi members nahi mile! 🎀")

    random.shuffle(members)
    total = len(members)

    if cmd == "etag":
        class FakeMember:
            def __init__(self, u): self.user = u
        tagged = await process_members(chat_id, [FakeMember(u) for u in members], text=tag_msg)
    else:
        tagged = 0
        for i in range(0, total, 5):
            if chat_id not in active_chats:
                break
            batch    = members[i:i+5]
            mentions = ", ".join([f"[{u.first_name}](tg://user?id={u.id})" for u in batch])
            success  = await safe_send(chat_id, f"**{tag_msg}**\n\n{mentions}")
            if not success:
                active_chats.pop(chat_id, None)
                await progress.edit_text("⚠️ Network error — tagging rok di.")
                return
            tagged += len(batch)
            await asyncio.sleep(2)

    active_chats.pop(chat_id, None)
    try:
        await progress.edit_text(f"✅ Tagging Complete! 🎀\n📊 Total: {total}")
    except Exception:
        pass

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
        if not m.user.is_bot and not m.user.is_deleted:
            members.append(m)

    total = len(members)
    active_chats[chat_id] = "all"
    text = None if replied else clean_text(message.text.split(None, 1)[1])

    tagged = await process_members(chat_id, members, text=text, replied=replied)
    active_chats.pop(chat_id, None)

    try:
        await app.send_message(
            chat_id,
            f"✅ Tagging completed!\n👥 Total: {total}\n✅ Tagged: {tagged}"
        )
    except Exception:
        pass

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

    total = len(members)
    active_chats[chat_id] = "admintag"
    text = None if replied else clean_text(message.text.split(None, 1)[1])

    tagged = await process_members(chat_id, members, text=text, replied=replied)
    active_chats.pop(chat_id, None)

    try:
        await app.send_message(
            chat_id,
            f"✅ Admin tagging completed!\n👑 Total: {total}\n✅ Tagged: {tagged}"
        )
    except Exception:
        pass

# ============================================================
# --- 6. SLOW TAG (/stag) ---
# ============================================================
@app.on_message(filters.command(["stag", "slowtag", "humantag"]) & filters.group)
async def slow_tag(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ Only admins can use this command.")

    chat_id = message.chat.id
    if chat_id in active_chats:
        return await message.reply("⚠️ Tagging already running. Use /stoptag to stop.")

    replied = message.reply_to_message
    members = []
    async for m in app.get_chat_members(chat_id):
        members.append(m)

    total = len(members)
    active_chats[chat_id] = "stag"
    text = None
    if len(message.command) > 1:
        text = clean_text(message.text.split(None, 1)[1])

    await message.reply(f"🐢 Human-style tagging shuru... {total} members")
    tagged = await process_members_single(chat_id, members, text=text, replied=replied)
    active_chats.pop(chat_id, None)

    try:
        await app.send_message(chat_id, f"✅ Done!\n👥 Total: {total}\n✅ Tagged: {tagged}")
    except Exception:
        pass

# ============================================================
# --- 7. GREETING TAGS ---
# ============================================================
@app.on_message(filters.command("gmtag") & filters.group)
async def gmtag(client, message):
    chat_id = message.chat.id
    if chat_id in active_chats:
        return await message.reply("⚠️ <b>Good Morning Tagging Already Running.</b>")
    active_chats[chat_id] = "gmtag"
    await message.reply("☀️ <b>Gᴏᴏᴅ Mᴏʀɴɪɴɢ Tᴀɢɢɪɴɢ Sᴛᴀʀᴛᴇᴅ...</b>")
    asyncio.create_task(
        safe_task(tag_users_greeting(chat_id, GM_MESSAGES, "Gᴏᴏᴅ Mᴏʀɴɪɴɢ"), chat_id, "gmtag")
    )

@app.on_message(filters.command("gatag") & filters.group)
async def gatag(client, message):
    chat_id = message.chat.id
    if chat_id in active_chats:
        return await message.reply("⚠️ <b>Afternoon Tagging Already On.</b>")
    active_chats[chat_id] = "gatag"
    await message.reply("☀️ <b>Aғᴛᴇʀɴᴏᴏɴ Tᴀɢɢɪɴɢ Sᴛᴀʀᴛᴇᴅ...</b>")
    asyncio.create_task(
        safe_task(tag_users_greeting(chat_id, GA_MESSAGES, "Aғᴛᴇʀɴᴏᴏɴ"), chat_id, "gatag")
    )

@app.on_message(filters.command("gntag") & filters.group)
async def gntag(client, message):
    chat_id = message.chat.id
    if chat_id in active_chats:
        return await message.reply("⚠️ <b>Night Tagging Already On.</b>")
    active_chats[chat_id] = "gntag"
    await message.reply("🌙 <b>Nɪɢʜᴛ Tᴀɢɢɪɴɢ Sᴛᴀʀᴛᴇᴅ...</b>")
    asyncio.create_task(
        safe_task(tag_users_greeting(chat_id, GN_MESSAGES, "Gᴏᴏᴅ Nɪɢʜᴛ"), chat_id, "gntag")
    )

# ============================================================
# --- 8. STOP COMMANDS ---
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
        f"🏷️ Active Tagging Chats: `{len(active_chats)}`"
    )

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a message to broadcast!")
    data = load_data()
    sent = 0
    msg  = await message.reply(f"📢 Broadcasting to {len(data['groups'])} groups...")
    for gid in data["groups"]:
        try:
            await message.reply_to_message.copy(gid)
            sent += 1
            await asyncio.sleep(0.5)
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
        except Exception:
            continue
    await msg.edit_text(f"✅ Broadcast Done!\n🚀 Sent to: {sent} groups.")

@app.on_message(filters.command("restart") & filters.user(OWNER_ID))
async def restart_cmd(client, message):
    active_chats.clear()
    msg = await message.reply("🔄 **Restarting QTTAGbot...**\n\n⏳ Ek second ruko... 🎀")
    await asyncio.sleep(1)
    await msg.edit_text("✅ **Bot Restart Ho Raha Hai!**\n\n🌸 Thodi der mein wapas aa jaayega!")
    os.execv(sys.executable, [sys.executable] + sys.argv)

# ============================================================
# --- 10. CHATBOT ---
# ============================================================
@app.on_message(filters.group & filters.new_chat_members)
async def welcome_response_handler(client, message):
    await simple_welcome(client, message)

@app.on_message(filters.sticker & filters.group, group=2)
async def sticker_response_handler(client, message):
    await handle_sticker(client, message, active_chats)

@app.on_message((filters.text | filters.media) & filters.group, group=3)
async def general_chat_handler(client, message):
    if message.text and message.text.startswith("/"):
        return
    await handle_chat(client, message, active_chats)
# ============================================================
# --- BOOT ---
# ============================================================
print("🌸 QTTAGbot LOADED! messages.py se import ho raha hai. 🎀")
app.run()
