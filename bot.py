import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- APNI DETAILS YAHAN BHAREIN ---
API_ID = 34950638  # Apna API ID dalein
API_HASH = "7546172bfc41310f1db2e793992afe72"    # Apna API Hash dalein
BOT_TOKEN = "8710999606:AAFeZz2P5OSjeqwxnHjsCVAYVWmf8DJYuW4"  # BotFather wala Token dalein
# ---------------------------------

app = Client("video_dl_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "**Bhai, welcome to All Video Downloader!** 😎\n\n"
        "Mujhe kisi bhi video ka link bhejo (YT, Insta, FB, TeraBox), "
        "main use highest quality mein download karke bhej dunga."
    )

@app.on_message(filters.text & filters.private)
async def handle_download(client, message):
    url = message.text
    if not url.startswith("http"):
        return await message.reply_text("Bhai, sahi link toh bhejo!")

    status = await message.reply_text("🔎 **Link check kar raha hoon...**")

    # yt-dlp configuration
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        # TeraBox aur baki sites ke liye headers zaroori hain
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        await status.edit("📥 **Server par download ho raha hai...**")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # Agar file high quality mein merge hui hai toh extension check
            if not file_path.endswith('.mp4'):
                base = os.path.splitext(file_path)[0]
                if os.path.exists(base + ".mp4"):
                    file_path = base + ".mp4"

        await status.edit("⬆️ **Telegram par upload ho raha hai...**")
        
        await client.send_video(
            chat_id=message.chat.id,
            video=file_path,
            caption=f"✅ **Title:** {info.get('title')}\n\nDownloaded via @{client.me.username}",
            supports_streaming=True
        )
        
        # Cleaning up
        os.remove(file_path)
        await status.delete()

    except Exception as e:
        await status.edit(f"❌ **Error:** {str(e)}")

print("Bot is running... Link ka intezar hai!")
app.run()
