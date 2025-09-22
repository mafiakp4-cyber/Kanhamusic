import os
import threading
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from flask import Flask

# 🔑 Config (तेरे values set कर दिए)
API_ID = 21302239
API_HASH = "1560930c983fbca6a1fcc8eab760d40d"
BOT_TOKEN = "8040887080:AAGrOVmImlAQDJi9VhuL0o_yvaKUTdo2hnU"  # Render में डालना होगा

app = Client(
    "MusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Dummy Flask app (Render port binding)
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Music Bot is running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# 🎵 Start command
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    await message.reply_text(
        "👋 Welcome to **Music Downloader Bot**!\n\n"
        "बस मुझे गाने का नाम भेजो 🎶\n\n"
        "Example: `Tum Hi Ho Arijit Singh`\n\n"
        "और मैं तुरंत mp3 भेज दूँगा 🚀"
    )

# 🎵 Text = Song Name
@app.on_message(filters.text & filters.private)
async def song_downloader(client, message: Message):
    query = message.text.strip()
    if not query:
        return

    status = await message.reply_text(f"🔎 Searching for **{query}** ...")

    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "%(title)s.%(ext)s",
            "noplaylist": True,
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            file_path = ydl.prepare_filename(info['entries'][0])
            title = info['entries'][0]['title']

        await message.reply_audio(audio=file_path, title=title, caption=f"🎶 {title}")

        os.remove(file_path)
        await status.delete()

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("🚀 Music Bot started...")
    app.run()
