import whisper

# LOAD MODEL
# ==============================

print("🧠 Loading Whisper model...")

try:
    model = whisper.load_model("base")
    print("✅ Whisper loaded")
except Exception as e:
    print(f"❌ Whisper load error: {e}")
    model = None


# ==============================
# MAIN FUNCTION
# ==============================

def transcribe_audio(audio_path: str):
    """
    Returns FULL coverage segments:
    [
      { start, end, text }
    ]
    """

    if model is None:
        return []

    try:
        result = model.transcribe(audio_path)
        raw_segments = result.get("segments", [])

        if not raw_segments:
            return []

        segments = [
            {
                "start": float(seg["start"]),
                "end": float(seg["end"]),
                "text": seg["text"].strip()
            }
            for seg in raw_segments
        ]

        # 🔥 Merge short segments (optional but useful)
        segments = merge_short_segments(segments)

        # 🔥 Fill silent gaps
        total_duration = result.get("duration", segments[-1]["end"])
        segments = fill_gaps(segments, total_duration)

        return segments

    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return []


# ==============================
# MERGE SHORT SEGMENTS
# ==============================
def merge_short_segments(segments, min_duration=5.0):
    """
    Merge small segments forward to ensure minimum duration.
    No overlapping segments.
    """

    if not segments:
        return []

    merged = []
    i = 0

    while i < len(segments):
        current = segments[i]

        start = current["start"]
        end = current["end"]
        text = current["text"]

        duration = end - start

        # 🔥 If too small → merge forward
        while duration < min_duration and i + 1 < len(segments):
            i += 1
            next_seg = segments[i]

            end = next_seg["end"]
            text = (text + " " + next_seg["text"]).strip()
            duration = end - start

        merged.append({
            "start": start,
            "end": end,
            "text": text
        })

        i += 1

    return merged

# ==============================
# 🔥 GAP FILLING (CORE FEATURE)
# ==============================

def fill_gaps(segments, total_duration):
    if not segments:
        return []

    filled = []
    prev_end = 0.0

    for seg in segments:
        start = seg["start"]
        end = seg["end"]

        # 🔥 gap before segment
        if start > prev_end:
            filled.append({
                "start": prev_end,
                "end": start,
                "text": ""  # silent segment
            })

        filled.append(seg)
        prev_end = end

    # 🔥 tail gap
    if prev_end < total_duration:
        filled.append({
            "start": prev_end,
            "end": total_duration,
            "text": ""
        })

    return filled