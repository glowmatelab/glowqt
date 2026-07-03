# messages.py

START_TEXT = (
    "<b>✨ QTTAGbot v2.0 • Premium Assistant</b>\n\n"
    "<blockquote>👋 <b>Welcome User!</b>\n"
    "Main aapki high-performance aur elegant group management assistant "
    "aur ek <b>Smart Chatbot</b> hoon.</blockquote>\n\n"
    "<b>⚡ Key Capabilities:</b>\n"
    " 🤖 <b>AI Chatbot:</b> Group engagement aur automated replies.\n"
    " 🚀 <b>Fast Mentions:</b> High-speed emoji aur text tagging modes.\n"
    " 📡 <b>Active Radar:</b> Online aur active members ko target karne ke liye.\n"
    " 🛡️ <b>Admin Tools:</b> Group operations ke liye strong controls.\n"
    " 🎭 <b>Social Suite:</b> Advanced AFK system aur dynamic greetings.\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "👉 <i>Niche diye gaye button se mujhe apne group mein add karein!</i>"
)
HELP_TEXT = (
    "<b>📖 QTTAGbot • Command Reference</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "<blockquote expandable>"
    "🤖 <b>AI CHATBOT ENGINE</b>\n"
    " ├ <code>/chatbot</code> ➔ Check chatbot status in group\n"
    " ├ <code>/chatbot on</code> ➔ Enable chatbot (bot replies to messages)\n"
    " └ <code>/chatbot off</code> ➔ Disable chatbot (mute the bot) 🤐\n\n"
    "📊 <b>TAGGING COMMANDS</b>\n"
    " ├ <code>/etag</code> ➔ Fast Emoji Tag (5 members/batch)\n"
    " ├ <code>/mtag</code> ➔ Standard Mention Tag\n"
    " ├ <code>/atag</code> ➔ Staff / Admin Only Tag\n"
    " ├ <code>/vtag</code> ➔ Active Radar (Only Online Members)\n"
    " ├ <code>/all</code>  ➔ Tag everyone with custom emoji sets\n"
    " ├ <code>/admintag</code> ➔ Fast tag for all group admins\n"
    " ├ <code>/stag</code>  ➔ Human Simulation (1-by-1 with typing)\n"
    " └ <code>/stoptag</code> ➔ Force stop current tagging\n\n"
    "🌤️ <b>DYNAMIC GREETINGS</b>\n"
    " ├ <code>/gmtag</code> ➔ Good Morning mass tagging\n"
    " ├ <code>/gatag</code> ➔ Good Afternoon mass tagging\n"
    " ├ <code>/gntag</code> ➔ Good Night mass tagging\n"
    " └ <code>/stopall</code> ➔ Stop ongoing greeting routines\n\n"
    "🎭 <b>SOCIAL & AFK SYSTEM</b>\n"
    " ├ <code>/afk [reason]</code> ➔ Set your away status\n"
    " └ <code>/back</code> ➔ Return from AFK mode\n\n"
    "🛡️ <b>SYSTEM ADMINISTRATION</b>\n"
    " ├ <code>/stats</code> ➔ View bot growth and analytics\n"
    " ├ <code>/broadcast</code> ➔ Send alert to all groups\n"
    " └ <code>/eval [code]</code> ➔ Execute Python code directly (Owner Only) 💻\n\n"
    "⚠️ <b>Note:</b> Sabhi tagging operations ke liye Admin hona mandatory hai."
    "</blockquote>"
)
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
    "💐 <b>Hᴀʀ Kᴀᴀᴍ Mᴇɪɴ Kᴀᴀᴍʏᴀʙɪ Mɪʟᴇ</b>\n\n{mention}",
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
    "🌈 <b>Rᴀɴɢ Bɪʀᴀɴɢᴀ Dᴏᴘʜᴀʀ</b>\n\n{mention}",
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
    "🌅 <b>Kᴀʟ Pʜɪʀ Mɪʟᴇɴɢᴇ Sᴜʙᴀʜ</b>\n\n{mention}",
]

EMOJI = [
    "🦋🦋🦋🦋🦋", "🧚🌸🧋🍬🫖", "🥀🌷🌹🌺💐",
    "🌸🌿💮🌱🌵", "❤️💚💙💜🖤", "💓💕💞💗💖",
    "🌸💐🌺🌹🦋", "🍔🦪🍛🍲🥗", "🍎🍓🍒🍑🌶️",
    "🧋🥤🧋🥛🍷", "🍬🍭🧁🎂🍡", "🍨🧉🍺☕🍻",
    "🥪🥧🍦🍥🍚", "🫖☕🍹🍷🥛", "☕🧃🍩🍦🍙",
    "🍁🌾💮🍂🌿", "🌨️🌥️⛈️🌩️🌧️", "🌷🏵️🌸🌺💐",
    "💮🌼🌻🍀🍁", "🧟🦸🦹🧙👸", "🧅🍠🥕🌽🥦",
    "🐷🐹🐭🐨🐻‍❄️", "🦋🐇🐀🐈🐈‍⬛", "🌼🌳🌲🌴🌵",
    "🥩🍋🍐🍈🍇", "🍴🍽️🔪🍶🥃", "🕌🏰🏩⛩️🏩",
    "🎉🎊🎈🎂🎀", "🪴🌵🌴🌳🌲", "🎄🎋🎍🎑🎎",
    "🦅🦜🕊️🦤🦢", "🦤🦩🦚🦃🦆", "🐬🦭🦈🐋🐳",
    "🐔🐟🐠🐡🦐", "🦩🦀🦑🐙🦪", "🐦🦂🕷️🕸️🐚",
    "🥪🍰🥧🍨🍨", "🥬🍉🧁🧇🔮",
]
