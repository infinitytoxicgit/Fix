import os
import requests

from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from Oneforall import app


# UPLOAD FUNCTION
def upload_file(file_path):

    try:

        server_data = requests.get(
            "https://api.gofile.io/servers",
            timeout=30
        ).json()

        server = (
            server_data["data"]["servers"][0]["name"]
        )

        with open(file_path, "rb") as f:

            response = requests.post(
                f"https://{server}.gofile.io/uploadFile",
                files={"file": f},
                timeout=120
            )

        data = response.json()

        # SUCCESS CHECK
        if (
            data.get("status") == "ok"
            or data.get("status") == "success"
        ):

            download_link = (
                data.get("data", {})
                .get("downloadPage")
            )

            if download_link:
                return True, download_link

        return False, str(data)

    except Exception as e:

        return False, str(e)


# COMMAND
@app.on_message(
    filters.command(
        ["tgm", "tgt", "telegraph", "tl"]
    )
)
async def telegraph_upload(client, message):

    # REPLY CHECK
    if not message.reply_to_message:

        return await message.reply_text(
            "❌ Reply to a media file."
        )

    media = message.reply_to_message

    # MEDIA CHECK
    if not (
        media.photo
        or media.video
        or media.document
        or media.audio
    ):

        return await message.reply_text(
            "❌ Unsupported media."
        )

    status = await message.reply_text(
        "📥 Downloading..."
    )

    try:

        # DOWNLOAD FILE
        file_path = await media.download()

        await status.edit_text(
            "📤 Uploading..."
        )

        # UPLOAD FILE
        success, result = upload_file(
            file_path
        )

        if success:

            buttons = InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(
                        "🌐 Open Link",
                        url=result
                    )
                ]]
            )

            await status.edit_text(
                f"✅ Uploaded Successfully\n\n{result}",
                reply_markup=buttons,
                disable_web_page_preview=True
            )

        else:

            await status.edit_text(
                f"❌ Upload Failed\n\n`{result}`"
            )

        # DELETE LOCAL FILE
        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:

        await status.edit_text(
            f"❌ Error:\n`{e}`"
        )



__HELP__ = """
**ᴛᴇʟᴇɢʀᴀᴘʜ ᴜᴘʟᴏᴀᴅ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs**

ᴜsᴇ ᴛʜᴇsᴇ ᴄᴏᴍᴍᴀɴᴅs ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴍᴇᴅɪᴀ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴘʜ:

- `/tgm`: ᴜᴘʟᴏᴀᴅ ʀᴇᴘʟɪᴇᴅ ᴍᴇᴅɪᴀ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴘʜ.
- `/tgt`: sᴀᴍᴇ ᴀs `/tgm`.
- `/telegraph`: sᴀᴍᴇ ᴀs `/tgm`.
- `/tl`: sᴀᴍᴇ ᴀs `/tgm`.

**ᴇxᴀᴍᴘʟᴇ:**
- ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴏʀ ᴠɪᴅᴇᴏ ᴡɪᴛʜ `/tgm` ᴛᴏ ᴜᴘʟᴏᴀᴅ ɪᴛ.

**ɴᴏᴛᴇ:**
ʏᴏᴜ ᴍᴜsᴛ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇᴅɪᴀ ғɪʟᴇ ғᴏʀ ᴛʜᴇ ᴜᴘʟᴏᴀᴅ ᴛᴏ ᴡᴏʀᴋ.
"""

__MODULE__ = "Tᴇʟᴇɢʀᴀᴘʜ"
