import os
import logging
import datetime
import threading
import yt_dlp
from flask import Flask
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
import pytz

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Log Channel ID (replace with actual channel ID)
LOGGING_CHANNEL_ID = "-1002613994353"  # Your log channel ID (integer, not a username)

# Function to send logs to Telegram log channel
async def send_log_to_channel(app, message):
    try:
        await app.send_message(LOGGING_CHANNEL_ID, f"📜 **Bot Log:**\n\n{message}")
    except Exception as e:
        logging.error(f"Failed to send log to Telegram: {e}")

# Log bot startup (call this when the bot starts)
async def log_bot_start(app: Client, bot_name: str, user):
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(tz)
    start_time = now.strftime("%Y-%m-%d %H:%M:%S %p")

    log_message = f"🚀 **{bot_name} Started by {user.mention}**\n" \
                  f"🆔 User ID: `{user.id}`\n" \
                  f"⏰ Time: {start_time} GMT+5:30"

    logging.info(log_message)
    await send_log_to_channel(app, log_message)

# Log user activity (user requests download)
async def log_download_request(app: Client, message, video_url):
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(tz)
    log_time = now.strftime("%Y-%m-%d %H:%M:%S %p")

    log_message = f"🎬 **Download Request**\n" \
                  f"👤 User: {message.from_user.mention}\n" \
                  f"🆔 User ID: `{message.from_user.id}`\n" \
                  f"🔗 URL: {video_url}\n" \
                  f"📅 Time: {log_time} GMT+5:30"

    logging.info(log_message)
    await send_log_to_channel(app, log_message)

# Log download completion
async def log_download_complete(app: Client, message):
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(tz)
    log_time = now.strftime("%Y-%m-%d %H:%M:%S %p")

    log_message = f"✅ **Download Completed**\n" \
                  f"👤 User: {message.from_user.mention}\n" \
                  f"🆔 User ID: `{message.from_user.id}`\n" \
                  f"📅 Time: {log_time} GMT+5:30"

    logging.info(log_message)
    await send_log_to_channel(app, log_message)

# Hook to log bot start automatically when the bot starts
def log_bot_start_on_init(app: Client):
    @app.on_message(filters.command("start"))
    async def start_command(client, message):
        await log_bot_start(app, "Fᴛᴍ TᴜʙᴇFᴇᴛᴄʜ", message.from_user)
        await message.reply("Hello! I'm **Fᴛᴍ TᴜʙᴇFᴇᴛᴄʜ**. Send a YouTube link to download.")

# Hook to log download requests automatically when a user sends a video URL
def log_download_request_on_message(app: Client):
    @app.on_message(filters.text & filters.private)
    async def download_video(client, message):
        video_url = message.text.strip()
        await log_download_request(app, message, video_url)
        # Simulate download process and respond
        await message.reply("🔄 Downloading video...")
        # Simulate sending download completion log
        await log_download_complete(app, message)
        await message.reply("✅ Video downloaded successfully!")

# Required Bot Credentials
API_ID = int(os.getenv("API_ID", "22141398"))
API_HASH = os.getenv("API_HASH", "0c8f8bd171e05e42d6f6e5a6f4305389")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8105194942:AAFzL74g4y3EMJdouoVUtRig4SP_1eZk_xs")

# Initialize bot
app = Client("YouTubeDownloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

log_bot_start_on_init(app)
log_download_request_on_message(app)

# Flask Web Server for Deployment Stability
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "TubeFetch is running! Visit the bot for downloads."

def run_web():
    flask_app.run(host='0.0.0.0', port=8000)

# Start Flask in a separate thread
threading.Thread(target=run_web, daemon=True).start()

# for bot to work 24×7
@flask_app.route('/keepalive')
def keepalive():
    return "Running", 200

# Store links to prevent losing them
youtube_links = {}

# Custom start message
@app.on_message(filters.command("start"))
async def start(client, message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    current_time = datetime.datetime.now().strftime("%H:%M %p")

    start_text = f"""
ʜᴇʏ {user_name}, `{user_id}`, Good welcome as `{current_time}` 🌤️ 👋  

ɪ ᴀᴍ ᴠᴇʀʏ ᴀɴᴅ ᴍᴏsᴛ ᴘᴏᴡᴇʀꜰᴜʟ 🎥 YᴏᴜTᴜʙᴇ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ ɴᴀᴍᴇᴅ ᴀs ⚡ **ғᴛᴍ ᴛᴜʙᴇғᴇᴛᴄʜ** ᴛɪʟʟ ɴᴏᴡ ᴄʀᴇᴀᴛᴇᴅ ʙʏ **Fᴛᴍ Dᴇᴠᴇʟᴏᴘᴇʀᴢ** 🚀  
Opened at **{current_time}**  

🌿 **ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ:** [Fᴛᴍ Dᴇᴠᴇʟᴏᴘᴇʀᴢ](https://t.me/ftmdeveloperz)
    """

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Updates", url="https://t.me/ftmbotzx")],
        [InlineKeyboardButton("💬 Support", url="https://t.me/ftmbotzx_support")],
        [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/ftmdeveloperz")],
        [InlineKeyboardButton("👑 Owner", url="https://t.me/ftmdeveloperz")]
    ])

    await message.reply_text(start_text, reply_markup=keyboard, disable_web_page_preview=True)


# Fetch available qualities using `yt-dlp`
@app.on_message(filters.text & filters.regex(r"(https?:\/\/)?(www\.|m\.)?(youtube\.com|youtu\.?be)\/.+"))
async def fetch_qualities(client, message):
    url = message.text
    youtube_links[message.chat.id] = url  # Save the link
    print(f"Received YouTube link: {url}")  # Debugging

    try:
        ydl_opts = {"quiet": True, "cookiefile": "cookies.txt"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])

        buttons = []
        for fmt in formats:
            if fmt.get("ext") == "mp4" and fmt.get("height"):
                res = f"{fmt.get('height')}p"
                buttons.append([InlineKeyboardButton(res, callback_data=f"ytdlp_{fmt['format_id']}")])

        buttons.append([InlineKeyboardButton("🔊 Audio Only", callback_data="ytdlp_audio")])

        keyboard = InlineKeyboardMarkup(buttons)
        await message.reply_text(f"🎬 **{info.get('title')}**\n\nSelect a quality:", reply_markup=keyboard)

    except Exception as e:
        await message.reply_text(f"❌ `yt-dlp` failed: {str(e)}")


# Download using `yt-dlp`
@app.on_callback_query(filters.regex(r"ytdlp_"))
async def download_ytdlp(client, callback_query):
    format_id = callback_query.data.split("_")[1]
    chat_id = callback_query.message.chat.id
    url = youtube_links.get(chat_id)  # Retrieve stored link
    
    if not url:
        await callback_query.message.reply_text("❌ Error: Unable to find the original YouTube link.")
        return

    try:
        ydl_opts = {
            "format": format_id if format_id != "audio" else "bestaudio",
            "outtmpl": "%(title)s.%(ext)s",
            "quiet": True,
            "cookiefile": "cookies.txt",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await callback_query.message.reply_text("📥 Downloading... Please wait.")
        await callback_query.message.reply_video(video=file_path, caption="✅ Download Complete!")
        os.remove(file_path)

    except Exception as e:
        await callback_query.message.reply_text(f"❌ `yt-dlp` failed: {str(e)}")


if __name__ == "__main__":
    app.run()
