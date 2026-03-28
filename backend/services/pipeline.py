import os
import gc
import uuid

from models.audio.inference import predict_audio
from models.vision.inference import predict_vision
from models.text.inference import predict_text

from utils.media import extract_audio_from_video, get_video_duration
from utils.transcription import transcribe_audio

from moviepy.video.io.VideoFileClip import VideoFileClip

TEMP_DIR = "temp"


# ==============================
# 🔥 CLAMP SEGMENTS
# ==============================

def clamp_segments(segments, video_duration):
    fixed = []

    for seg in segments:
        start = max(0, float(seg["start"]))
        end = min(float(seg["end"]), video_duration)

        if end <= start:
            continue

        fixed.append({
            "start": start,
            "end": end,
            "text": seg.get("text", "")
        })

    return fixed


# ==============================
# 🔥 FALLBACK SEGMENTS (IF EMPTY)
# ==============================

def create_fallback_segments(video_duration, chunk_size=7.0):
    segments = []
    start = 0.0

    while start < video_duration:
        end = min(start + chunk_size, video_duration)

        segments.append({
            "start": start,
            "end": end,
            "text": ""
        })

        start = end

    return segments


# ==============================
# MAIN PIPELINE
# ==============================

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
        # 2. GET VIDEO DURATION
        # ======================
        video_duration = get_video_duration(video_path)

        # ======================
        # 3. TRANSCRIPTION
        # ======================
        segments = transcribe_audio(audio_file)

        # 🔥 fallback if whisper failed
        if not segments:
            print("⚠️ No segments from Whisper → using fallback")
            segments = create_fallback_segments(video_duration)

        # 🔥 clamp timestamps
        segments = clamp_segments(segments, video_duration)

        segment_results = []
        full_transcript = []

        # ======================
        # 4. LOAD VIDEO ONCE
        # ======================
        video = VideoFileClip(video_path)

        for seg in segments:
            start = seg["start"]
            end = seg["end"]
            text = seg["text"]

            full_transcript.append(text)

            seg_id = str(uuid.uuid4())
            seg_audio_path = os.path.join(TEMP_DIR, f"{seg_id}.wav")
            seg_video_path = os.path.join(TEMP_DIR, f"{seg_id}.mp4")

            try:
                # ======================
                # SAFETY CHECK
                # ======================
                if end <= start:
                    continue

                # ======================
                # CUT VIDEO
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
                # CUT AUDIO
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
        gc.collect()

        # ======================
        # FINAL RESPONSE
        # ======================
        return {
            "verdict": "frontend_computed",
            "confidence": 0.0,
            "segments": segment_results,
            "transcript": " ".join(full_transcript).strip(),
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