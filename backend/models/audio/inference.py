import os
import numpy as np
import librosa
import tensorflow as tf

# ==============================
# CONFIG
# ==============================

CLASSES = ["neutral", "sexual_content", "violence", "hate_speech"]

SAMPLE_RATE = 22050
DURATION = 6
N_MELS = 128
TARGET_FRAMES = 130

MODEL_PATH = os.path.join(os.path.dirname(__file__), "audio_moderation_model.h5")

# ==============================
# LOAD MODEL (GLOBAL - LOAD ONCE)
# ==============================

print("🔊 Loading Audio Model...")

if os.path.exists(MODEL_PATH):
    audio_model = tf.keras.models.load_model(MODEL_PATH)
    print("✅ Audio model loaded")
else:
    print(f"⚠️ Audio model not found at {MODEL_PATH}")
    audio_model = None


# ==============================
# AUDIO INFERENCE FUNCTION
# ==============================

def predict_audio(audio_path: str):
    """
    Run audio moderation model on extracted audio file.
    Returns probability scores for each class.
    """

    if audio_model is None:
        return {c: 0.0 for c in CLASSES}

    try:
        # 1. Load audio
        audio, _ = librosa.load(audio_path, sr=SAMPLE_RATE, duration=DURATION)

        # 2. Pad / truncate
        target_len = SAMPLE_RATE * DURATION
        if len(audio) < target_len:
            audio = np.pad(audio, (0, target_len - len(audio)))
        else:
            audio = audio[:target_len]

        # 3. Mel spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=audio,
            sr=SAMPLE_RATE,
            n_mels=N_MELS
        )

        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

        # 4. Add channel dimension
        data = np.expand_dims(mel_spec_db, axis=-1)

        # 5. Resize to match training shape
        if data.shape[1] != TARGET_FRAMES:
            data = tf.image.resize(data, (N_MELS, TARGET_FRAMES)).numpy()

        # 6. Add batch dimension
        input_data = np.expand_dims(data, axis=0)

        # 7. Predict
        preds = audio_model.predict(input_data, verbose=0)[0]

        # 8. Map outputs
        return {
            "neutral": float(preds[3]),
            "sexual_content": float(preds[0]),
            "violence": float(preds[1]),
            "hate_speech": float(preds[2])
        }

    except Exception as e:
        print(f"❌ Audio inference error: {e}")
        return {c: 0.0 for c in CLASSES}