import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from flask import Flask
import threading

# 🔑 Config (Render Environment Variables)
API_ID = int(os.environ.get("API_ID", "21302239"))
API_HASH = os.environ.get("API_HASH", "1560930c983fbca6a1fcc8eab760d40d")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8399464240:AAFocUbqy6t88-GNj3eK1RlvfIx1y1XPF0M")

# Pyrogram Bot
app = Client(
    "SongBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Flask app for Render port binding
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ JioSaavn Song Downloader Bot is running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# 🎬 Start command
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    await message.reply_text(
        "👋 Welcome to **Song Downloader Bot** 🎶\n\n"
        "Send me a song name like:\n`/song Tum Hi Ho`\n\n"
        "And I’ll fetch it from **JioSaavn** in HD quality 🚀"
    )

# 🎵 Song download
@app.on_message(filters.command("song") & filters.private)
async def song_downloader(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Please provide a song name!\n\nExample: `/song Tum Hi Ho`")
        return

    query = " ".join(message.command[1:])
    status = await message.reply_text(f"🔎 Searching for **{query}** ...")

    try:
        # Hit JioSaavn API
        url = f"https://jiosaavn-api.vercel.app/search?query={query}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            await status.edit_text("❌ API error, try again later!")
            return

        results = response.json().get("data", [])
        if not results:
            await status.edit_text("❌ No results found!")
            return

        # First song
        song = results[0]
        title = song.get("title") or song.get("name", "Unknown Title")
        artist = song.get("primaryArtists", "Unknown Artist")

        # 🔗 Fix: handle list OR string downloadUrl
        download_url = None
        if isinstance(song.get("downloadUrl"), list):
            download_url = song["downloadUrl"][-1].get("link")
        elif isinstance(song.get("downloadUrl"), str):
            download_url = song["downloadUrl"]

        if not download_url:
            await status.edit_text("❌ Download link not found!")
            return

        # Send audio
        await client.send_audio(
            chat_id=message.chat.id,
            audio=download_url,
            title=title,
            performer=artist,
            caption=f"🎶 {title}\n👤 {artist}\n\nPowered by JioSaavn 🚀"
        )

        await status.delete()

    except Exception as e:
        await status.edit_text(f"❌ Error: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("🚀 JioSaavn Song Bot started...")
    app.run()
