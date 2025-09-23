import os
import requests
import threading
from pyrogram import Client, filters
from pyrogram.types import Message
from flask import Flask

# 🔑 Config
API_ID = 21302239
API_HASH = "1560930c983fbca6a1fcc8eab760d40d"
BOT_TOKEN = "8399464240:AAFocUbqy6t88-GNj3eK1RlvfIx1y1XPF0M"  # Render पर Environment Variable में डालना

app = Client(
    "JioSaavnBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Dummy Flask app for Render
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ JioSaavn Music Bot is running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# 🎵 Start Command
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    await message.reply_text(
        "👋 Welcome to **JioSaavn Music Bot** 🎶\n\n"
        "👉 बस गाने का नाम भेजो और मैं तुम्हें mp3 दे दूँगा।\n\n"
        "Powered by **JioSaavn API** 🚀"
    )

# 🎵 Handle Text (Song Search)
@app.on_message(filters.text & filters.private)
async def song_downloader(client: Client, message: Message):
    query = message.text.strip()
    await message.reply_text(f"🔎 Searching JioSaavn for **{query}** ...")

    try:
        # API Call
        url = f"https://jiosaavn-api.vercel.app/search/songs?query={query}"
        res = requests.get(url).json()

        if not res.get("data"):
            await message.reply_text("❌ No results found!")
            return

        # First song details
        song = res["data"][0]
        title = song["name"]
        artist = song["primaryArtists"]
        download_url = song["downloadUrl"][-1]["link"]  # High quality (320kbps)

        # Send song
        await message.reply_audio(
            audio=download_url,
            title=title,
            performer=artist,
            caption=f"🎶 **{title}**\n👤 {artist}"
        )

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("🚀 JioSaavn Music Bot started...")
    app.run()
