import os
import requests
import threading
from pyrogram import Client, filters
from pyrogram.types import Message
from flask import Flask

# 🔑 Config
API_ID = 21302239
API_HASH = "1560930c983fbca6a1fcc8eab760d40d"
BOT_TOKEN = "8399464240:AAFocUbqy6t88-GNj3eK1RlvfIx1y1XPF0M"  # Render पर Environment Variable डालना

app = Client(
    "JioSaavnBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# 🌐 Dummy Flask app for Render
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

# 🎵 Handle Song Search
@app.on_message(filters.text & filters.private)
async def song_downloader(client: Client, message: Message):
    query = message.text.strip()
    status = await message.reply_text(f"🔎 Searching JioSaavn for **{query}** ...")

    try:
        results = []

        # ✅ Primary API
        url = f"https://saavn.dev/api/search/songs?query={query}"
        res = requests.get(url, timeout=10)

        if res.status_code == 200:
            data = res.json()
            results = data.get("data", {}).get("results", [])

        # ✅ Backup API
        if not results:
            backup_url = f"https://jiosaavn-api.vercel.app/search/songs?query={query}"
            res = requests.get(backup_url, timeout=10)

            if res.status_code == 200:
                data = res.json()
                results = data.get("data", [])

        if not results:
            await status.edit_text("❌ No results found on any API!")
            return

        # First song
        song = results[0]
        title = song.get("title") or song.get("name", "Unknown Title")
        artist = song.get("primaryArtists", "Unknown Artist")
        download_url = song.get("downloadUrl", [{}])[-1].get("link")

        if not download_url:
            await status.edit_text("❌ Download link not found!")
            return

        # Send song
        await client.send_audio(
            chat_id=message.chat.id,
            audio=download_url,
            title=title,
            performer=artist,
            caption=f"🎶 **{title}**\n👤 {artist}"
        )

        await status.delete()

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("🚀 JioSaavn Music Bot started...")
    app.run()
