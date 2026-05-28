"""
Helper module for applying filters to streams in call.py
Provides utilities to build FFmpeg filter strings and apply to MediaStream
"""

from pytgcalls.types import AudioQuality, MediaStream, VideoQuality


def build_filter_string(chat_id: int, filter_dict: dict) -> str:
    """
    Build FFmpeg filter string for a chat
    
    Args:
        chat_id: Chat ID to get filters for
        filter_dict: Dictionary of available filters
    
    Returns:
        FFmpeg filter string or empty string if no filters
    """
    from Oneforall.plugins.play.filter import active_filters, FILTER_MAP
    
    filters_list = active_filters.get(chat_id, [])
    if not filters_list:
        return ""
    
    ffmpeg_filters = []
    for filter_key in filters_list:
        if filter_key in FILTER_MAP and FILTER_MAP[filter_key]:
            ffmpeg_filters.append(FILTER_MAP[filter_key])
    
    return ",".join(ffmpeg_filters) if ffmpeg_filters else ""


def create_media_stream_with_filter(
    file_path: str,
    video: bool = False,
    ffmpeg_filters: str = "",
    ffmpeg_parameters: str = "",
) -> MediaStream:
    """
    Create a MediaStream with applied filters
    
    Args:
        file_path: Path to media file
        video: Whether to include video
        ffmpeg_filters: Audio filters string
        ffmpeg_parameters: Additional FFmpeg parameters
    
    Returns:
        MediaStream object with filters applied
    """
    # Combine filter and additional parameters
    if ffmpeg_filters:
        if ffmpeg_parameters:
            # Add audio filters to existing parameters
            combined_params = f"-af {ffmpeg_filters} {ffmpeg_parameters}"
        else:
            combined_params = f"-af {ffmpeg_filters}"
    else:
        combined_params = ffmpeg_parameters if ffmpeg_parameters else ""
    
    if video:
        return MediaStream(
            file_path,
            audio_parameters=AudioQuality.HIGH,
            video_parameters=VideoQuality.SD_480p,
            ffmpeg_parameters=combined_params if combined_params else None,
        )
    else:
        return MediaStream(
            file_path,
            audio_parameters=AudioQuality.HIGH,
            ffmpeg_parameters=combined_params if combined_params else None,
            video_flags=MediaStream.IGNORE,
        )
