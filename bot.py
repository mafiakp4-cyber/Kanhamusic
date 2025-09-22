import os
import threading
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaAudio, InputMediaPhoto
from flask import Flask
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time

# 🔑 Config (Apna Spotify API aur Telegram BOT_TOKEN set kar diya)
SPOTIFY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
SPOTIFY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"

API_ID = 21302239
API_HASH = "1560930c983fbca6a1fcc8eab760d40d"
BOT_TOKEN = "8040887080:AAGrOVmImlAQDJi9VhuL0o_yvaKUTdo2hnU"

# Pyrogram Client
app = Client(
    "SpotifyMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Flask app for Render
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Spotify Music Bot is running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# Spotipy client
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Start command
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    await message.reply_text(
        "👋 Welcome to **Spotify Music Bot**!\n\n"
        "बस मुझे गाने का नाम भेजो 🎶\n"
        "मैं track info + preview mp3 भेज दूँगा 🚀\n\n"
        "Example: `Tum Hi Ho Arijit Singh`"
    )

# Handle text = song name
@app.on_message(filters.text & filters.private)
async def spotify_song(client, message: Message):
    query = message.text.strip()
    if not query:
        return

    status = await message.reply_text(f"🔎 Searching for **{query}** on Spotify...")

    try:
        results = sp.search(query, type="track", limit=1)
        if len(results['tracks']['items']) == 0:
            await status.edit_text("❌ No track found on Spotify.")
            return

        track = results['tracks']['items'][0]
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        album_name = track['album']['name']
        album_art_url = track['album']['images'][0]['url'] if track['album']['images'] else None
        preview_url = track['preview_url']

        if not preview_url:
            await status.edit_text("⚠️ Preview not available for this track.")
            return

        # Download preview mp3
        timestamp = int(time.time())
        filename = f"{message.from_user.id}_{timestamp}.mp3"

        def download_preview():
            r = requests.get(preview_url, stream=True)
            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

        thread = threading.Thread(target=download_preview)
        thread.start()
        thread.join()

        caption = f"🎶 {track_name} — {artist_name}\nAlbum: {album_name}"

        # Send album art + audio
        if album_art_url:
            await message.reply_photo(photo=album_art_url, caption=caption)
        await message.reply_audio(audio=filename, title=track_name, performer=artist_name)

        os.remove(filename)
        await status.delete()

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("🚀 Spotify Music Bot started...")
    app.run()
