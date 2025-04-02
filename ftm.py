import os
import logging 
import datetime
import pytz 
from pyrogram import Client, filters 
from pytube import YouTube

Setup logging configuration

logging.basicConfig( level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" )

Log Channel ID (replace with your actual log channel ID)

LOGGING_CHANNEL_ID = "-1002613994353"

Function to send logs to Telegram log channel

async def send_log_to_channel(app, message): try: await app.send_message(LOGGING_CHANNEL_ID, f"📜 Bot Log:\n\n{message}") except Exception as e: logging.error(f"Failed to send log to Telegram: {e}")

Initialize bot

app = Client("ftm_tubefetch_bot")

@app.on_message(filters.command("start")) async def start(client, message): user = message.from_user bot_name = "Fᴛᴍ TᴜʙᴇFᴇᴛᴄʜ" await message.reply_text(f"Hello {user.first_name}, send me a YouTube link to download!") log_message = f"✅ Bot Started\n\n🤖 Bot: {bot_name}\n👤 User: {user.first_name} (@{user.username})\n🆔 ID: {user.id}" await send_log_to_channel(client, log_message)

@app.on_message(filters.regex(r"https?://(?:www.)?youtube.com/watch?v=[\w-]+|https?://youtu.be/[\w-]+")) async def youtube_handler(client, message): url = message.text user = message.from_user await message.reply_text("🔍 Fetching video details...") log_message = f"🔗 YouTube URL Received\n\n👤 User: {user.first_name} (@{user.username})\n🆔 ID: {user.id}\n🎥 URL: {url}" await send_log_to_channel(client, log_message)

try:
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    file_path = stream.download()
    
    log_message = f"⏳ **Download Started**\n\n👤 User: {user.first_name} (@{user.username})\n🆔 ID: {user.id}\n🎥 URL: {url}\n📥 Quality: {stream.resolution}"
    await send_log_to_channel(client, log_message)
    
    await message.reply_video(video=file_path, caption="✅ Download Complete!")
    await client.send_video(
        LOGGING_CHANNEL_ID,
        video=file_path,
        caption=f"✅ **Download Completed**\n\n👤 User: {user.first_name} (@{user.username})\n🆔 ID: {user.id}\n🎥 URL: {url}\n📂 File Sent Successfully"
    )
    
    os.remove(file_path)
except Exception as e:
    await message.reply_text("❌ Download failed! Please try again later.")
    log_message = f"❌ **Download Failed**\n\n👤 User: {user.first_name} (@{user.username})\n🆔 ID: {user.id}\n🎥 URL: {url}\n⚠️ Error: {str(e)}"
    await send_log_to_channel(client, log_message)

app.run()

