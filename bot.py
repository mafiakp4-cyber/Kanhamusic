import os
import threading
import requests
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from flask import Flask

# 🔑 Config
API_ID = int(os.environ.get("API_ID", "21302239"))
API_HASH = os.environ.get("API_HASH", "1560930c983fbca6a1fcc8eab760d40d")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8398875779:AAHmI2PpYASV6P0lKaiNOCugBm7ZYUxIqe4")

# Initialize Bot
app = Client("MusicProBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Flask app for Render
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "🎶 Multi-Source Music Downloader Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)


# 🎬 Start Command
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    await message.reply_text(
        "👋 **Welcome to MusicPro Bot!** 🎵\n\n"
        "Use `/song <name>` to download from 🎧 **YouTube**, 🎵 **SoundCloud**, or 🎶 **JioSaavn**.\n\n"
        "Example:\n`/song Kesariya` or `/song Arijit Singh`"
    )


# 🎧 Song Downloader
@app.on_message(filters.command("song") & filters.private)
async def song_cmd(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Please provide a song name!\nExample: `/song Arijit Singh`")
        return

    query = " ".join(message.command[1:])
    status = await message.reply_text(f"🔎 Searching for **{query}** ...")

    # Try JioSaavn first
    try:
        jio_url = f"https://saavn.dev/api/search/songs?query={query}"
        jio_data = requests.get(jio_url).json()
        songs = jio_data.get("data", {}).get("results", [])
        if songs:
            song = songs[0]
            title = song["title"]
            url = song["downloadUrl"][-1]["url"]
            await status.edit_text(f"⬇️ Downloading **{title}** from JioSaavn ...")
            file_name = f"{title}.mp3"
            r = requests.get(url)
            with open(file_name, "wb") as f:
                f.write(r.content)
            await message.reply_audio(audio=file_name, title=title, caption=f"🎶 {title} (JioSaavn)")
            os.remove(file_name)
            await status.delete()
            return
    except Exception:
        pass

    # Try SoundCloud
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "%(title)s.%(ext)s",
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"scsearch1:{query}", download=True)
            entry = info["entries"][0]
            file_path = ydl.prepare_filename(entry)
            title = entry["title"]

        await status.edit_text(f"⬆️ Uploading **{title}** from SoundCloud ...")
        await message.reply_audio(audio=file_path, title=title, caption=f"🎧 {title} (SoundCloud)")
        os.remove(file_path)
        await status.delete()
        return
    except Exception:
        pass

    # Fallback to YouTube
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "%(title)s.%(ext)s",
            "noplaylist": True,
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            entry = info["entries"][0]
            file_path = ydl.prepare_filename(entry)
            title = entry["title"]

        await status.edit_text(f"⬆️ Uploading **{title}** from YouTube ...")
        await message.reply_audio(audio=file_path, title=title, caption=f"🎥 {title} (YouTube)")
        os.remove(file_path)
        await status.delete()

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("🚀 Multi-Source Music Bot started...")
    app.run()
