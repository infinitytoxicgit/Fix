"""
Audio Filter Implementation for Music Bot
Handles filter callbacks, storage, and real-time filter application
"""

from pyrogram import filters as pyro_filters
from pyrogram.types import InlineKeyboardMarkup

import config
from Oneforall import app
from Oneforall.core.call import Hotty
from Oneforall.misc import db
from Oneforall.utils.database import get_lang
from Oneforall.utils.inline.play import (
    filters_markup_page_1,
    filters_markup_page_2,
    filters_markup_page_3,
    filters_markup_page_4,
)
from Oneforall.utils.decorators.language import languageCB
from strings import get_string

# Store active filters per chat
active_filters = {}


# FFmpeg filter mappings
FILTER_MAP = {
    "bass_boost": "bass=g=10",
    "treble_boost": "treble=g=10",
    "echo": "echo=0.8:0.9:1000:0.3",
    "reverb": "reverb=mix=0.5",
    "chorus": "chorus=0.5:0.9:50:55:60:55",
    "compressor": "compand=.3|.3:1|1:-90/-90,-60/-60,-20/-5,0/0,-5/-12,20/20",
    "equalizer_rock": "equalizer=f=60:g=5:w=1.5,equalizer=f=500:g=3:w=1.5,equalizer=f=3000:g=-2:w=1.5",
    "equalizer_pop": "equalizer=f=100:g=5:w=2,equalizer=f=1000:g=2:w=2,equalizer=f=8000:g=4:w=2",
    "equalizer_jazz": "equalizer=f=100:g=2:w=1.5,equalizer=f=1000:g=-1:w=1.5,equalizer=f=8000:g=3:w=1.5",
    "normalizer": "loudnorm",
    "stereo_widener": "stereotools=mlev=on",
    "pitch_up": "rubberband=pitch=1.5",
    "pitch_down": "rubberband=pitch=0.67",
    "fade_in": "afade=t=in:st=0:d=2",
    "fade_out": "afade=t=out:st=0:d=2",
    "noise_reduction": "anlmdn",
    "vinyl": "lowpass=f=8000,highpass=f=75",
    "telephone": "bandpass=f=1000:w=900",
    "high_pass": "highpass=f=200",
    "low_pass": "lowpass=f=3000",
    "no_filter": "",
}


def get_filter_string(chat_id: int) -> str:
    """Get the FFmpeg filter string for a chat"""
    filters_list = active_filters.get(chat_id, [])
    if not filters_list:
        return ""
    
    # Combine multiple filters with comma
    ffmpeg_filters = []
    for filter_key in filters_list:
        if filter_key in FILTER_MAP and FILTER_MAP[filter_key]:
            ffmpeg_filters.append(FILTER_MAP[filter_key])
    
    return ",".join(ffmpeg_filters) if ffmpeg_filters else ""


@app.on_callback_query(pyro_filters.regex("ShowFilters") & ~config.BANNED_USERS)
@languageCB
async def show_filters(client, CallbackQuery, _):
    """Display filter menu"""
    try:
        callback_data = CallbackQuery.data.split()
        callback_request = callback_data[1] if len(callback_data) > 1 else ""
        
        if callback_request:
            try:
                videoid, user_id, cplay, fplay = callback_request.split("|")
            except:
                await CallbackQuery.answer("❌ Invalid callback data!", show_alert=True)
                return
        else:
            await CallbackQuery.answer("❌ No data provided!", show_alert=True)
            return
        
        if CallbackQuery.from_user.id != int(user_id):
            try:
                return await CallbackQuery.answer(_["playcb_1"], show_alert=True)
            except:
                return
        
        try:
            await CallbackQuery.answer()
        except:
            pass
        
        # Show first page of filters
        markup = filters_markup_page_1()
        await CallbackQuery.edit_message_reply_markup(reply_markup=markup)
        
    except Exception as e:
        try:
            await CallbackQuery.answer(f"❌ Error: {str(e)[:50]}", show_alert=True)
        except:
            pass


@app.on_callback_query(pyro_filters.regex("FiltersPage") & ~config.BANNED_USERS)
@languageCB
async def filter_pages(client, CallbackQuery, _):
    """Handle filter page navigation"""
    try:
        callback_data = CallbackQuery.data.split()
        page = int(callback_data[1]) if len(callback_data) > 1 else 1
        
        try:
            await CallbackQuery.answer()
        except:
            pass
        
        # Get appropriate markup based on page number
        if page == 1:
            markup = filters_markup_page_1()
        elif page == 2:
            markup = filters_markup_page_2()
        elif page == 3:
            markup = filters_markup_page_3()
        elif page == 4:
            markup = filters_markup_page_4()
        else:
            markup = filters_markup_page_1()
        
        await CallbackQuery.edit_message_reply_markup(reply_markup=markup)
        
    except Exception as e:
        try:
            await CallbackQuery.answer(f"❌ Error: {str(e)[:50]}", show_alert=True)
        except:
            pass


@app.on_callback_query(pyro_filters.regex("ApplyFilter") & ~config.BANNED_USERS)
@languageCB
async def apply_filter(client, CallbackQuery, _):
    """Apply selected filter to currently playing stream"""
    try:
        callback_data = CallbackQuery.data.split()
        filter_key = callback_data[1] if len(callback_data) > 1 else "no_filter"
        
        try:
            await CallbackQuery.answer()
        except:
            pass
        
        # Get chat_id from current message
        chat_id = CallbackQuery.message.chat.id
        original_chat_id = chat_id
        
        # Check if music is playing
        if not db.get(chat_id) or not db[chat_id]:
            await CallbackQuery.answer("❌ No music is currently playing!", show_alert=True)
            return
        
        current_song = db[chat_id][0]
        file_path = current_song.get("file")
        
        if not file_path:
            await CallbackQuery.answer("❌ Stream file not found!", show_alert=True)
            return
        
        # Update active filters
        if filter_key == "no_filter":
            active_filters[chat_id] = []
            filter_name = "❌ No Filter"
        else:
            if filter_key not in FILTER_MAP:
                await CallbackQuery.answer("❌ Unknown filter!", show_alert=True)
                return
            
            active_filters[chat_id] = [filter_key]
            # Get display name
            filter_names = {
                "bass_boost": "🔊 Bass Boost",
                "treble_boost": "📈 Treble Boost",
                "echo": "🎵 Echo",
                "reverb": "🔄 Reverb",
                "chorus": "🎶 Chorus",
                "compressor": "📊 Compressor",
                "equalizer_rock": "🎸 Rock EQ",
                "equalizer_pop": "🎤 Pop EQ",
                "equalizer_jazz": "🎺 Jazz EQ",
                "normalizer": "⚖️ Normalizer",
                "stereo_widener": "🔀 Stereo Widener",
                "pitch_up": "⬆️ Pitch Up",
                "pitch_down": "⬇️ Pitch Down",
                "fade_in": "🔆 Fade In",
                "fade_out": "🔅 Fade Out",
                "noise_reduction": "🔇 Noise Reduction",
                "vinyl": "💿 Vinyl",
                "telephone": "☎️ Telephone",
                "high_pass": "📡 High Pass",
                "low_pass": "🔊 Low Pass",
            }
            filter_name = filter_names.get(filter_key, filter_key.replace("_", " ").title())
        
        # Apply filter to the stream
        try:
            from Oneforall.core.call_filter_helper import create_media_stream_with_filter
            
            streamtype = current_song.get("streamtype", "audio")
            video = str(streamtype) == "video"
            
            # Get FFmpeg filter string
            ffmpeg_filters = get_filter_string(chat_id)
            
            # Build stream with filters
            stream = create_media_stream_with_filter(
                file_path,
                video=video,
                ffmpeg_filters=ffmpeg_filters,
            )
            
            # Get assistant and apply stream change
            from Oneforall.utils.database import group_assistant
            assistant = await group_assistant(Hotty, chat_id)
            await assistant.change_stream(chat_id, stream)
            
            # Store filter info in db
            current_song["current_filter"] = filter_key
            
            await CallbackQuery.answer(f"✅ Applied: {filter_name}", show_alert=True)
            
        except Exception as e:
            await CallbackQuery.answer(f"❌ Error: {str(e)[:50]}", show_alert=True)
    
    except Exception as e:
        try:
            await CallbackQuery.answer(f"❌ Error: {str(e)[:50]}", show_alert=True)
        except:
            pass


async def remove_filter(chat_id: int):
    """Remove active filter for a chat"""
    if chat_id in active_filters:
        del active_filters[chat_id]
