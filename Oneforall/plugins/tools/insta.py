from pyrogram import filters
import os
import re
import yt_dlp
from pyrogram.types import Message
from Oneforall import app

URL_PATTERN = r"(https?://[^\s]+)"

def download_video(url: str):
    try:
        path = "downloads"
        os.makedirs(path, exist_ok=True)

        # Instagram tracking params remove
        url = url.split("?")[0]

        ydl_opts = {
            "outtmpl": f"{path}/%(title).50s.%(ext)s",

            # Better formats
            "format": "mp4/best",

            # Fixes
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "geo_bypass": True,

            # Instagram fixes
            "extractor_args": {
                "instagram": {
                    "api_version": "v1"
                }
            },

            # Mobile headers
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                    "Version/16.0 Mobile/15E148 Safari/604.1"
                )
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        return file_path

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        return None


@app.on_message(filters.text & filters.regex(URL_PATTERN))
async def auto_downloader(client, message: Message):

    match = re.search(URL_PATTERN, message.text)

    if not match:
        return

    url = match.group(0)

    status = await message.reply_text("⚡ **Downloading...**")

    try:
        file_path = download_video(url)

        if not file_path or not os.path.exists(file_path):
            return await status.edit(
                "❌ **Download Failed**\n\n"
                "Instagram may be blocking requests."
            )

        await status.edit("📤 **Uploading...**")

        await message.reply_video(
            video=file_path,
            caption=f"✅ **Here is your video**\n\n🔗 {url}"
        )

        try:
            os.remove(file_path)
        except:
            pass

        await status.delete()

    except Exception as e:
        await status.edit(f"❌ **Error:**\n`{e}`")