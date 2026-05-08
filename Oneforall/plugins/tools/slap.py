import random
import requests

from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from Oneforall import app


# ALL COMMANDS
anime_actions = [

    # NORMAL
    "waifu",
    "neko",
    "shinobu",
    "megumin",

    # REACTIONS
    "bully",
    "cry",
    "hug",
    "kiss",
    "lick",
    "pat",
    "smug",
    "bonk",
    "yeet",
    "blush",
    "smile",
    "wave",
    "highfive",
    "handhold",
    "nom",
    "bite",
    "glomp",
    "slap",
    "kill",
    "kick",
    "happy",
    "wink",
    "poke",
    "dance",
    "cringe",

    # EXTRA
    "cuddle",
    "awoo"
]


# API LIST
apis = [

    "https://api.waifu.pics/sfw/{action}",

    "https://nekos.best/api/v2/{action}",

    "https://api.otakugifs.xyz/gif?reaction={action}"
]


# FETCH IMAGE/GIF
def get_anime_media(action):

    random.shuffle(apis)

    for api in apis:

        try:

            url = api.format(action=action)

            response = requests.get(
                url,
                timeout=20
            )

            if response.status_code != 200:
                continue

            data = response.json()

            media_url = None

            # WAIFU.PICS
            if "waifu.pics" in api:
                media_url = data.get("url")

            # NEKOS.BEST
            elif "nekos.best" in api:

                results = data.get("results")

                if results:
                    media_url = results[0].get("url")

            # OTAKUGIFS
            elif "otakugifs" in api:

                media_url = (
                    data.get("url")
                    or data.get("gif")
                )

            if media_url:
                return media_url

        except Exception:
            pass

    return None


# HANDLER
for action in anime_actions:

    @app.on_message(filters.command(action))
    async def anime_handler(
        client,
        message,
        action=action
    ):

        status = await message.reply_text(
            f"✨ Fetching {action}..."
        )

        try:

            media_url = get_anime_media(
                action
            )

            if not media_url:

                return await status.edit_text(
                    "❌ No media found."
                )

            buttons = InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(
                        "🔄 Again",
                        callback_data=f"anime_{action}"
                    )
                ]]
            )

            # GIF
            if (
                ".gif" in media_url
                or "gif" in media_url
            ):

                await message.reply_animation(
                    animation=media_url,
                    caption=(
                        f"✨ {action.title()}"
                    ),
                    reply_markup=buttons
                )

            # IMAGE
            else:

                await message.reply_photo(
                    photo=media_url,
                    caption=(
                        f"✨ {action.title()}"
                    ),
                    reply_markup=buttons
                )

            await status.delete()

        except Exception as e:

            await status.edit_text(
                f"❌ Error:\n`{e}`"
            )


# CALLBACK
@app.on_callback_query(
    filters.regex("^anime_")
)
async def anime_callback(
    client,
    query
):

    action = (
        query.data.split("_")[1]
    )

    media_url = get_anime_media(
        action
    )

    if not media_url:

        return await query.answer(
            "No media found",
            show_alert=True
        )

    try:

        if (
            ".gif" in media_url
            or "gif" in media_url
        ):

            await query.message.reply_animation(
                animation=media_url,
                caption=f"✨ {action.title()}"
            )

        else:

            await query.message.reply_photo(
                photo=media_url,
                caption=f"✨ {action.title()}"
            )

        await query.answer()

    except Exception:

        await query.answer(
            "Failed",
            show_alert=True
        )


__HELP__ = """
Anime Reaction Commands

/hug
/kiss
/slap
/pat
/waifu
/neko
/cry
/dance
/wink
/happy
/blush
/bite
/highfive
/cuddle
"""