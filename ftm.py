import os
import logging
import datetime
import yt_dlp
import threading
from pyrogram import Client, filters
from flask import Flask
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Required Bot Credentials
API_ID = int(os.getenv("API_ID", "22141398"))
API_HASH = os.getenv("API_HASH", "0c8f8bd171e05e42d6f6e5a6f4305389")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8105194942:AAFzL74g4y3EMJdouoVUtRig4SP_1eZk_xs")
LOG_CHANNEL_ID =os.getenv("LOG_CHANNEL_ID", "-1002613994353")  # Added Log Channel Credential

# Enable logging
logging.basicConfig(level=logging.INFO)

# Initialize bot
app = Client("YouTubeDownloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

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

# Function to send logs to the log channel
async def send_log_to_channel(client, message):
    try:
        await client.send_message(LOG_CHANNEL_ID, message)
    except Exception as e:
        logging.error(f"Failed to send log: {e}")

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
    await send_log_to_channel(client, f"✅ Bot Started by {user_name} ({user_id})")

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
        await client.send_video(LOG_CHANNEL_ID, video=file_path, caption=f"📥 Video downloaded by {callback_query.from_user.first_name} ({callback_query.from_user.id})")
        os.remove(file_path)

    except Exception as e:
        await callback_query.message.reply_text(f"❌ `yt-dlp` failed: {str(e)}")
        await send_log_to_channel(client, f"❌ Download failed for {callback_query.from_user.first_name} ({callback_query.from_user.id}) - {str(e)}")

if __name__ == "__main__":
    app.run()


I've added LOG_CHANNEL_ID as an environment variable, similar to API_ID. Now, logs and activity details will be sent to the log channel. Let me know if you want any further refinements!

