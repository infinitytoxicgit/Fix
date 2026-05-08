import requests
from pyrogram import filters
from Oneforall import app


@app.on_message(filters.command(["ig", "instagram", "reel"]))
async def download_instagram_video(client, message):

    if len(message.command) < 2:
        return await message.reply_text(
            "**Usage:**\n`/ig instagram_link`"
        )

    url = message.command[1]

    # Remove tracking params
    url = url.split("?")[0]

    status = await message.reply_text(
        "**📥 Downloading Instagram Reel...**"
    )

    try:
        api_url = (
            "https://nodejs-1xn1lcfy3-jobians.vercel.app/"
            f"v2/downloader/instagram?url={url}"
        )

        response = requests.get(api_url, timeout=20)

        if response.status_code != 200:
            return await status.edit(
                "❌ API Error.\nTry again later."
            )

        data = response.json()

        if not data.get("status"):
            return await status.edit(
                "❌ Failed to fetch reel."
            )

        reel_data = data.get("data")

        if not reel_data:
            return await status.edit(
                "❌ No media found."
            )

        video_url = reel_data[0].get("url")

        if not video_url:
            return await status.edit(
                "❌ Video URL not found."
            )

        await client.send_video(
            chat_id=message.chat.id,
            video=video_url,
            caption="✅ **Instagram Reel Downloaded**"
        )

        await status.delete()

    except Exception as e:
        await status.edit(
            f"❌ Error:\n`{e}`"
        )


__MODULE__ = "Instagram"

__HELP__ = """
/ig [link] - Download Instagram Reel
/reel [link] - Download Instagram Reel
/instagram [link] - Download Instagram Reel
"""