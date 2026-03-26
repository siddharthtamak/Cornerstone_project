import os
import gc
import uuid

from models.audio.inference import predict_audio
from models.vision.inference import predict_vision
from models.text.inference import predict_text

from utils.media import extract_audio_from_video
from utils.transcription import transcribe_audio

from moviepy.video.io.VideoFileClip import VideoFileClip

TEMP_DIR = "temp"


def process_video(video_path: str):

    base_name = str(uuid.uuid4())
    audio_path = os.path.join(TEMP_DIR, f"{base_name}.wav")

    try:
        # ======================
        # 1. EXTRACT FULL AUDIO
        # ======================
        audio_file = extract_audio_from_video(video_path, audio_path)

        if audio_file is None:
            return {
                "verdict": "neutral",
                "confidence": 1.0,
                "segments": [],
                "transcript": "",
                "modalities": {}
            }

        # ======================
        # 2. GET SEGMENTS
        # ======================
        segments = transcribe_audio(audio_file)

        segment_results = []
        full_transcript = []

        # ======================
        # 3. LOAD VIDEO ONCE
        # ======================
        video = VideoFileClip(video_path)

        for seg in segments:
            start = seg["start"]
            end = seg["end"]
            text = seg["text"]

            full_transcript.append(text)

            # ======================
            # CREATE TEMP FILES
            # ======================
            seg_id = str(uuid.uuid4())

            seg_audio_path = os.path.join(TEMP_DIR, f"{seg_id}.wav")
            seg_video_path = os.path.join(TEMP_DIR, f"{seg_id}.mp4")

            try:
                # ======================
                # CUT VIDEO SEGMENT
                # ======================
                subclip = video.subclip(start, end)

                subclip.write_videofile(
                    seg_video_path,
                    codec="libx264",
                    audio_codec="aac",
                    verbose=False,
                    logger=None
                )

                # ======================
                # CUT AUDIO SEGMENT
                # ======================
                subclip.audio.write_audiofile(
                    seg_audio_path,
                    codec="pcm_s16le",
                    logger=None
                )

                # ======================
                # RUN MODELS
                # ======================
                text_scores = predict_text(text)
                audio_scores = predict_audio(seg_audio_path)
                vision_scores = predict_vision(seg_video_path)

                # ======================
                # STORE RESULT
                # ======================
                segment_results.append({
                    "start": start,
                    "end": end,
                    "text": text,
                    "modalities": {
                        "text": text_scores,
                        "audio": audio_scores,
                        "vision": vision_scores
                    }
                })

            except Exception as e:
                print(f"❌ Segment error ({start}-{end}): {e}")

            finally:
                # CLEAN TEMP FILES
                if os.path.exists(seg_audio_path):
                    os.remove(seg_audio_path)
                if os.path.exists(seg_video_path):
                    os.remove(seg_video_path)

        video.close()

        # ======================
        # FINAL RESPONSE
        # ======================
        return {
            "verdict": "frontend_computed",
            "confidence": 0.0,
            "segments": segment_results,
            "transcript": " ".join(full_transcript),
            "modalities": {}
        }

    except Exception as e:
        print(f"❌ Pipeline error: {e}")

        return {
            "verdict": "error",
            "confidence": 0.0,
            "segments": [],
            "transcript": "",
            "modalities": {},
            "error": str(e)
        }