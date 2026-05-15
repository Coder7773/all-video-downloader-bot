import os
import yt_dlp
import asyncio
from pyrogram import Client, filters
from threading import Thread
from flask import Flask

# --- RENDER FREE TIER FIX: WEBSERVER ---
# Ye Render ko dhoka dene ke liye hai taaki wo bot ko free mein chalne de
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    # Render hamesha PORT naam ka environment variable deta hai
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)
# ----------------------------------------

# --- APNI DETAILS YAHAN BHAREIN ---
API_ID = 34950638  
API_HASH = "7546172bfc41310f1db2e793992afe72"    
BOT_TOKEN = "8710999606:AAFeZz2P5OSjeqwxnHjsCVAYVWmf8DJYuW4"  
# ---------------------------------

app = Client("video_dl_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "**Bhai, welcome to All Video Downloader!** 😎\n\n"
        "Mujhe kisi bhi video ka link bhejo, main download karke bhej dunga."
    )

@app.on_message(filters.text & filters.private)
async def handle_download(client, message):
    url = message.text
    if not url.startswith("http"):
        return await message.reply_text("Bhai, sahi link toh bhejo!")

    status = await message.reply_text("🔎 **Link check kar raha hoon...**")
    unique_name = f"video_{message.from_user.id}_{message.id}"

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'downloads/{unique_name}.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        },
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }

    try:
        await status.edit("📥 **Server par download ho raha hai...**")
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))
        
        if not info:
            return await status.edit("❌ **Error:** Video info nahi nikal payi.")
            
        file_path = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)
        
        if not os.path.exists(file_path):
            base = os.path.splitext(file_path)[0]
            if os.path.exists(base + ".mp4"):
                file_path = base + ".mp4"
            else:
                for f in os.listdir("downloads"):
                    if f.startswith(unique_name):
                        file_path = os.path.join("downloads", f)
                        break

        await status.edit("⬆️ **Telegram par upload ho raha hai...**")
        await client.send_video(
            chat_id=message.chat.id,
            video=file_path,
            caption=f"✅ **Title:** {info.get('title', 'Downloaded Video')}\n\nDownloaded via @{client.me.username}",
            supports_streaming=True
        )
        if os.path.exists(file_path):
            os.remove(file_path)
        await status.delete()

    except Exception as e:
        await status.edit(f"❌ **Error:** {str(e)}")

# GitHub par requirements.txt mein flask bhi daal dena
if __name__ == "__main__":
    # Flask webserver ko alag thread mein chalu karenge
    Thread(target=run_flask).start()
    print("Bot is running... Link ka intezar hai!")
    app.run()
