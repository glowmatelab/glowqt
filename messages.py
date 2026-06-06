# messages.py

START_TEXT = (
    "╔══════════════════════════════╗\n"
    "║       🎀 QTTAGbot v2.0  🎀     \n"
    "╚══════════════════════════════╝\n\n"
    "✨ **WELCOME USER!**\n"
    "Main hoon aapki stylish tagging assistant.\n\n"
    "🚀 **CORE FEATURES:**\n"
    "┣ ⚡ High-Speed Mentions\n"
    "┣ 🔥 Active Member Finder\n"
    "┣ 👑 Admin Power Tools\n"
    "┣ 🌙 AFK Status System\n"
    "┣ 🌅 GM/GA/GN Tagging\n"
    "┗ 🐢 Human-style Single Tag\n\n"
    "**Niche button se mujhe add karein!**"
)

HELP_TEXT = (
    "╔══════════════════════════════╗\n"
    "║       🎀 QTTAGbot HelpMsg 🎀   \n"
    "╚══════════════════════════════╝\n\n"
    "📂 **TAGGING ENGINE**\n"
    "┣ `/etag` → Emoji Tag (5 batch, fast) 🎨\n"
    "┣ `/mtag` → Mention Tag (Standard)\n"
    "┣ `/atag` → Admin Tag (Staff)\n"
    "┣ `/vtag` → Active Tag (Online)\n"
    "┣ `/all` → Tag All with Emoji\n"
    "┣ `/admintag` → Tag Admins with Emoji\n"
    "┣ `/stag` → Human Tag (1 by 1, typing) 🐢\n"
    "┗ `/stoptag` → Stop All Processes 🛑\n\n"
    "🌅 **GREETING TAGS**\n"
    "┣ `/gmtag` → Good Morning Tag ☀️\n"
    "┣ `/gatag` → Good Afternoon Tag 🌤️\n"
    "┣ `/gntag` → Good Night Tag 🌙\n"
    "┗ `/stopall` → Stop Greeting Tag 🛑\n\n"
    "🎭 **SOCIAL**\n"
    "┣ `/afk [reason]` → Away Status 🌙\n"
    "┗ `/back` → Back from AFK 💌\n\n"
    "⚙️ **SYSTEM ADMIN**\n"
    "┣ `/stats` → Check Growth 📊\n"
    "┗ `/broadcast` → Global Broadcast 📢\n\n"
    "**Note:** Tagging commands ke liye Admin hona zaroori hai! ✨"
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
