import asyncio
import json

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from Oneforall import app
from Oneforall.misc import SUDOERS


# SAFE EDIT
async def safe_edit(msg, text):

    try:
        await msg.edit_text(text)

    except FloodWait as e:

        await asyncio.sleep(e.value)

        try:
            await msg.edit_text(text)
        except:
            pass

    except:
        pass


@app.on_message(
    filters.command(
        ["speedtest", "spt"]
    ) & SUDOERS
)
async def speedtest_command(
    client,
    message: Message
):

    msg = await message.reply_text(
        "⚡ Running Speed Test..."
    )

    try:

        process = await asyncio.create_subprocess_shell(

            "speedtest --format=json",

            stdout=asyncio.subprocess.PIPE,

            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if stderr:

            err = stderr.decode()

            if (
                err.strip()
                and "Testing from" not in err
            ):

                return await safe_edit(
                    msg,
                    f"❌ Error:\n`{err}`"
                )

        data = json.loads(
            stdout.decode()
        )

        # SPEED
        download = round(
            data["download"]["bandwidth"]
            * 8 / 1000000,
            2
        )

        upload = round(
            data["upload"]["bandwidth"]
            * 8 / 1000000,
            2
        )

        ping = data["ping"]["latency"]

        # CLIENT
        isp = data["isp"]

        ip = data["interface"][
            "externalIp"
        ]

        # SERVER
        server = data["server"]["host"]

        sponsor = data["server"]["name"]

        # RESULT IMAGE
        result_url = data["result"]["url"]

        caption = f"""
╭───────────────⭓
│ ⚡ SPEED TEST
├───────────────
│ 📥 Download: {download} Mbps
│ 📤 Upload: {upload} Mbps
│ 🏓 Ping: {ping} ms
├───────────────
│ 🌍 ISP: {isp}
│ 🌐 IP: {ip}
├───────────────
│ 🖥 Server: {server}
│ 🏢 Sponsor: {sponsor}
╰───────────────⭓
"""

        # SEND RESULT
        await message.reply_photo(
            photo=result_url,
            caption=caption
        )

        try:
            await msg.delete()
        except:
            pass

    except Exception as e:

        await safe_edit(
            msg,
            f"❌ Error:\n`{e}`"
        )


__MODULE__ = "SpeedTest"

__HELP__ = """
/speedtest
/spt

Run server speed test with image.
"""