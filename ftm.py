import os
import logging
import datetime
import threading
import yt_dlp
from flask import Flask
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
 
from pyrogram import Client, filters

# Required Bot Credentials
API_ID = int(os.getenv("API_ID", "22141398"))
API_HASH = os.getenv("API_HASH", "0c8f8bd171e05e42d6f6e5a6f4305389")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8105194942:AAFzL74g4y3EMJdouoVUtRig4SP_1eZk_xs")

# Log Channel ID (replace with actual channel ID)
LOGGING_CHANNEL_ID = "-1002613994353" # Your log channel ID (integer, not a username)

# Initialize bot
app = Client("YouTubeDownloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to send logs to Telegram channel
async def send_log(message):
    try:
        await app.send_message(chat_id=LOGGING_CHANNEL_ID, text=f"📢 **Log:** {message}")
    except Exception as e:
        logging.error(f"Failed to send log: {e}")

# Log bot startup
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user = message.from_user
    log_message = f"🚀 Bot started by {user.first_name} (@{user.username}) | User ID: {user.id}"
    await send_log(log_message)
    await message.reply_text("Hello! Bot is online.")

# Log any command usage
@app.on_message(filters.command(["help", "about"]) & filters.private)
async def log_command(client, message):
    user = message.from_user
    log_message = f"📝 {user.first_name} (@{user.username}) used {message.text} | User ID: {user.id}"
    await send_log(log_message)

# Log when a user sends any message
@app.on_message(filters.text & filters.private)
async def log_messages(client, message):
    user = message.from_user
    log_message = f"📩 Message from {user.first_name} (@{user.username}): {message.text} | User ID: {user.id}"
    await send_log(log_message)

# Download video, send logs, and send the video to the log channel
@app.on_message(filters.command("download") & filters.private)
async def download_video(client, message):
    user = message.from_user
    args = message.text.split(" ", 1)

    if len(args) < 2:
        await message.reply_text("⚠ Please provide a YouTube URL.")
        return

    download_url = args[1]
    log_message = f"🎥 {user.first_name} (@{user.username}) started downloading:\n🔗 {download_url} | User ID: {user.id}"
    await send_log(log_message)

    try:
        ydl_opts = {
            'outtmpl': './downloads/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',  # Download best available quality
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(download_url, download=True)
            video_title = info_dict.get("title", "Unknown Title")
            file_path = ydl.prepare_filename(info_dict)

            log_message = f"✅ Download completed: '{video_title}' for {user.first_name} (@{user.username})"
            await send_log(log_message)

            # Send the downloaded video to the log channel
            await client.send_video(chat_id=LOGGING_CHANNEL_ID, video=file_path, caption=f"🎥 **Downloaded Video:** {video_title}")

    except Exception as e:
        log_message = f"❌ Download failed for {user.first_name} (@{user.username}): {e}"
        await send_log(log_message)
        
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
