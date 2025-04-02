import os
import logging
import datetime
import yt_dlp
import threading
from pyrogram import Client, filters
from flask import Flask
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Log Channel ID (replace with your actual log channel ID)
LOGGING_CHANNEL_ID = "-1002613994353"

# Function to send logs to Telegram log channel
async def send_log_to_channel(app, message):
    try:
        await app.send_message(LOGGING_CHANNEL_ID, f"\ud83d\udcdd **Bot Log:**\n\n{message}")
    except Exception as e:
        logging.error(f"Failed to send log to Telegram: {e}")

# Required Bot Credentials
API_ID = int(os.getenv("API_ID", "22141398"))
API_HASH = os.getenv("API_HASH", "0c8f8bd171e05e42d6f6e5a6f4305389")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8105194942:AAFzL74g4y3EMJdouoVUtRig4SP_1eZk_xs")

# Initialize bot
app = Client("YouTubeDownloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Flask Web Server for Deployment Stability
flask_app = Flask(__name__)

def run_web():
    flask_app.run(host='0.0.0.0', port=8000)

threading.Thread(target=run_web, daemon=True).start()

@app.on_message(filters.command("start"))
async def start(client, message):
    user = message.from_user
    bot_name = "Fᴛᴍ TᴜʙᴇFᴇᴛᴄʜ"
    log_message = f"✅ **Bot Started**\n\n🤖 Bot: {bot_name}\n👤 User: {user.first_name} (@{user.username})\n🆔 ID: {user.id}"
    await send_log_to_channel(client, log_message)
    
    await message.reply_text("Hey, welcome to Fᴛᴍ TᴜʙᴇFᴇᴛᴄʜ!")

youtube_links = {}

@app.on_message(filters.text & filters.regex(r"(https?:\/\/)?(www\.|m\.)?(youtube\.com|youtu\.?be)\/.*"))
async def fetch_qualities(client, message):
    url = message.text
    youtube_links[message.chat.id] = url
    log_message = f"🔗 **YouTube URL Received**\n\n👤 User: {message.from_user.first_name} (@{message.from_user.username})\n🆔 ID: {message.from_user.id}\n🎥 URL: {url}"
    await send_log_to_channel(client, log_message)
    
    await message.reply_text("Processing video...")

@app.on_callback_query(filters.regex(r"ytdlp_"))
async def download_ytdlp(client, callback_query):
    format_id = callback_query.data.split("_")[1]
    chat_id = callback_query.message.chat.id
    url = youtube_links.get(chat_id)
    
    if not url:
        await callback_query.message.reply_text("❌ Error: Unable to find the original YouTube link.")
        return
    
    try:
        log_message = f"⏳ **Download Started**\n\n👤 User: {callback_query.from_user.first_name} (@{callback_query.from_user.username})\n🆔 ID: {callback_query.from_user.id}\n🎥 URL: {url}\n📥 Quality: {format_id}"
        await send_log_to_channel(client, log_message)
        
        ydl_opts = {
            "format": format_id if format_id != "audio" else "bestaudio",
            "outtmpl": "%(title)s.%(ext)s",
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        
        await callback_query.message.reply_video(video=file_path, caption="✅ Download Complete!")
        os.remove(file_path)
        
        log_message = f"✅ **Download Completed**\n\n👤 User: {callback_query.from_user.first_name} (@{callback_query.from_user.username})\n🆔 ID: {callback_query.from_user.id}\n🎥 URL: {url}\n📂 File Sent Successfully"
        await send_log_to_channel(client, log_message)
    
    except Exception as e:
        log_message = f"❌ **Download Failed**\n\n👤 User: {callback_query.from_user.first_name} (@{callback_query.from_user.username})\n🆔 ID: {callback_query.from_user.id}\n🎥 URL: {url}\n⚠️ Error: {str(e)}"
        await send_log_to_channel(client, log_message)
        await callback_query.message.reply_text(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    app.run()
