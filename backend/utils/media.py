import os
from moviepy.video.io.VideoFileClip import VideoFileClip


def extract_audio_from_video(video_path: str, audio_path: str):
    """
    Extracts audio from video file and saves as WAV.

    Returns:
        audio_path if successful
        None if video has no audio or fails
    """

    try:
        with VideoFileClip(video_path) as video:
            # Case: no audio track
            if video.audio is None:
                return None

            # Ensure directory exists
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)

            # Write audio
            video.audio.write_audiofile(
                audio_path,
                codec="pcm_s16le",  # standard WAV codec
                logger=None        # suppress verbose logs
            )

            return audio_path

    except Exception as e:
        print(f"❌ Audio extraction error: {e}")
        return None