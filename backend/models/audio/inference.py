import os
import numpy as np
import tensorflow as tf
from scipy.io import wavfile
import scipy.signal

# ==============================
# CONFIG
# ==============================

CLASSES = ["neutral", "sexual_content", "violence", "hate_speech"]

SAMPLE_RATE = 22050
DURATION = 5
N_MELS = 128
INPUT_FRAMES = 212  # matches training

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "audio_moderation_model.h5")

# ==============================
# LOAD MODEL (GLOBAL)
# ==============================

print("🔊 Loading Audio Model...")

if os.path.exists(MODEL_PATH):
    try:
        audio_model = tf.keras.models.load_model(MODEL_PATH)
        print("✅ Audio model loaded")
    except Exception as e:
        print(f"❌ Error loading audio model: {e}")
        audio_model = None
else:
    print(f"⚠️ Audio model not found at {MODEL_PATH}")
    audio_model = None


# ==============================
# FEATURE EXTRACTION
# ==============================

def extract_features(file_path: str):
    """
    Convert audio file → log-mel spectrogram (same as training)
    """

    try:
        # 1. Load audio using SciPy
        sr, audio = wavfile.read(file_path)

        # 2. Normalize
        if audio.dtype == np.int16:
            audio = audio.astype(np.float32) / 32768.0
        elif audio.dtype == np.int32:
            audio = audio.astype(np.float32) / 2147483648.0
        else:
            audio = audio.astype(np.float32)

        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))

        # 3. Convert stereo → mono
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        # 4. Resample if needed
        if sr != SAMPLE_RATE:
            num_samples = int(len(audio) * float(SAMPLE_RATE) / sr)
            audio = scipy.signal.resample(audio, num_samples)

        # 5. Convert to tensor
        audio_tensor = tf.convert_to_tensor(audio, dtype=tf.float32)

        # 6. Pad / truncate
        target_len = SAMPLE_RATE * DURATION
        audio_len = tf.shape(audio_tensor)[0]

        def pad():
            return tf.pad(audio_tensor, [[0, target_len - audio_len]])

        def clip():
            return audio_tensor[:target_len]

        audio_tensor = tf.cond(audio_len < target_len, pad, clip)

        # 7. STFT
        stft = tf.signal.stft(
            audio_tensor,
            frame_length=2048,
            frame_step=512,
            window_fn=tf.signal.hann_window
        )

        spectrogram = tf.abs(stft)

        # 8. Mel conversion
        num_spectrogram_bins = tf.shape(spectrogram)[-1]

        mel_weight = tf.signal.linear_to_mel_weight_matrix(
            num_mel_bins=N_MELS,
            num_spectrogram_bins=num_spectrogram_bins,
            sample_rate=SAMPLE_RATE,
            lower_edge_hertz=0.0,
            upper_edge_hertz=8000.0
        )

        mel_spectrogram = tf.matmul(spectrogram, mel_weight)
        log_mel = tf.math.log(mel_spectrogram + 1e-6)

        # 9. Transpose to (mel, time)
        log_mel = tf.transpose(log_mel)

        # 10. Add channel dimension
        features = log_mel[..., tf.newaxis]

        # 11. Resize to expected input shape
        if features.shape[1] != INPUT_FRAMES:
            features = tf.image.resize(features, (N_MELS, INPUT_FRAMES))

        return features.numpy()

    except Exception as e:
        print(f"❌ Feature extraction error: {e}")
        return None


# ==============================
# INFERENCE FUNCTION
# ==============================

def predict_audio(audio_path: str):
    """
    Main function used by pipeline
    Returns:
        {
            "neutral": float,
            "sexual_content": float,
            "violence": float,
            "hate_speech": float
        }
    """

    if audio_model is None:
        return {c: 0.0 for c in CLASSES}

    try:
        features = extract_features(audio_path)

        if features is None:
            return {c: 0.0 for c in CLASSES}

        # Add batch dimension
        input_data = np.expand_dims(features, axis=0)

        # Predict
        preds = audio_model.predict(input_data, verbose=0)[0]

        # Map outputs (IMPORTANT: same as training mapping)
        return {
            "neutral": float(preds[3]),
            "sexual_content": float(preds[0]),
            "violence": float(preds[1]),
            "hate_speech": float(preds[2])
        }

    except Exception as e:
        print(f"❌ Audio inference error: {e}")
        return {c: 0.0 for c in CLASSES}