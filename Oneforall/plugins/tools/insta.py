from pyrogram import filters
import os
import re
import requests
import yt_dlp

from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from Oneforall import app


# URL PATTERN
URL_PATTERN = r"(https?://[^\s]+)"


# INSTAGRAM APIs
INSTAGRAM_APIS = [

    "https://api.agatz.xyz/api/instagram?url={url}",

    "https://api.neoxr.eu/api/ig?url={url}&apikey=mcandy",

    "https://api.ryzendesu.vip/api/downloader/instagram?url={url}"
]


# DOWNLOAD FUNCTION
def download_video(url: str):

    try:

        path = "downloads"

        os.makedirs(path, exist_ok=True)

        url = url.split("?")[0]

        # INSTAGRAM
        if "instagram.com" in url:

            for api in INSTAGRAM_APIS:

                try:

                    api_url = api.format(
                        url=url
                    )

                    response = requests.get(
                        api_url,
                        timeout=30
                    ).json()

                    video_url = None

                    # AGATZ
                    if response.get("data"):

                        data = response["data"]

                        if isinstance(data, list):

                            if isinstance(
                                data[0],
                                dict
                            ):
                                video_url = (
                                    data[0].get("url")
                                )
                            else:
                                video_url = data[0]

                        elif isinstance(data, dict):

                            video_url = (
                                data.get("url")
                            )

                    # RESULT
                    if (
                        not video_url
                        and response.get("result")
                    ):

                        result = response[
                            "result"
                        ]

                        if isinstance(
                            result,
                            list
                        ):

                            if isinstance(
                                result[0],
                                dict
                            ):
                                video_url = (
                                    result[0].get(
                                        "url"
                                    )
                                )
                            else:
                                video_url = result[0]

                        elif isinstance(
                            result,
                            dict
                        ):

                            video_url = (
                                result.get("url")
                            )

                    if video_url:

                        file_path = (
                            f"{path}/instagram.mp4"
                        )

                        video = requests.get(
                            video_url,
                            stream=True,
                            timeout=60
                        )

                        with open(
                            file_path,
                            "wb"
                        ) as f:

                            for chunk in (
                                video.iter_content(
                                    chunk_size=1024
                                )
                            ):

                                if chunk:
                                    f.write(chunk)

                        return file_path

                except Exception as e:

                    print(
                        "INSTAGRAM API ERROR:",
                        e
                    )

        # YOUTUBE
        ydl_opts = {

            "outtmpl":
                f"{path}/%(title).50s.%(ext)s",

            "format":
                "bestvideo+bestaudio/best",

            "merge_output_format":
                "mp4",

            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "geo_bypass": True,

            "http_headers": {

                "User-Agent":
                    "Mozilla/5.0"
            }
        }

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            file_path = (
                ydl.prepare_filename(
                    info
                )
            )

            if not file_path.endswith(
                ".mp4"
            ):

                file_path = (
                    os.path.splitext(
                        file_path
                    )[0]
                    + ".mp4"
                )

        return file_path

    except Exception as e:

        print(
            "DOWNLOAD ERROR:",
            e
        )

        return None


# MAIN DOWNLOADER
async def process_download(
    message,
    url
):

    status = await message.reply_text(
        "⚡ **Downloading...**"
    )

    try:

        file_path = download_video(
            url
        )

        if (
            not file_path
            or not os.path.exists(
                file_path
            )
        ):

            return await status.edit(
                "❌ Download Failed"
            )

        await status.edit(
            "📤 Uploading..."
        )

        buttons = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    "🔗 Original Link",
                    url=url
                )
            ]]
        )

        await message.reply_video(
            video=file_path,
            caption=(
                "✅ Download Complete"
            ),
            reply_markup=buttons
        )

        try:
            os.remove(file_path)
        except:
            pass

        await status.delete()

    except Exception as e:

        await status.edit(
            f"❌ Error:\n`{e}`"
        )


# AUTO LINK DOWNLOADER
@app.on_message(
    filters.text &
    filters.regex(URL_PATTERN)
)
async def auto_downloader(
    client,
    message: Message
):

    match = re.search(
        URL_PATTERN,
        message.text
    )

    if not match:
        return

    url = match.group(0)

    if (
        "instagram.com" not in url
        and "youtube.com" not in url
        and "youtu.be" not in url
    ):
        return

    await process_download(
        message,
        url
    )


# COMMANDS
@app.on_message(
    filters.command(
        [
            "instagram",
            "ig",
            "insta"
        ]
    )
)
async def instagram_command(
    client,
    message: Message
):

    if len(message.command) < 2:

        return await message.reply_text(
            "**Usage:**\n"
            "/ig instagram_link"
        )

    url = message.command[1]

    await process_download(
        message,
        url
    )


__HELP__ = """
/ig link
/insta link
/instagram link

Auto downloads:
Instagram + YouTube links
"""

__MODULE__ = "Downloader"