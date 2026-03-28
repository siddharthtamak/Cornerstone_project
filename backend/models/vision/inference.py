import os
import torch

# import new model logic
from models.vision.video_model import (
    InferConfig,
    classify_video_clips
)

# ==============================
# CONFIG
# ==============================

CLASSES = ["neutral", "sexual_content", "violence", "hate_speech"]

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "best_model.pt")

# ==============================
# LOAD CONFIG
# ==============================

print("🎥 Loading Vision Model...")

try:
    cfg = InferConfig(checkpoint=MODEL_PATH)
    print("✅ Vision model ready")
except Exception as e:
    print(f"❌ Vision model load error: {e}")
    cfg = None


# ==============================
# PROBABILITY MAPPING
# ==============================

def map_to_distribution(p_n, p_v):
    """
    Convert Bernoulli outputs → proper distribution
    """

    sexual_content = p_n
    violence = p_v

    neutral = (1 - p_n) * (1 - p_v)

    return {
        "neutral": float(neutral),
        "sexual_content": float(sexual_content),
        "violence": float(violence),
        "hate_speech": 0.0
    }


# ==============================
# MAIN FUNCTION
# ==============================

def predict_vision(video_path: str):

    if cfg is None:
        return {c: 0.0 for c in CLASSES}

    try:
        result = classify_video_clips(video_path, cfg)

        p_n = result.get("nudity_prob", 0.0)
        p_v = result.get("violence_prob", 0.0)

        return map_to_distribution(p_n, p_v)

    except Exception as e:
        print(f"❌ Vision inference error: {e}")
        return {c: 0.0 for c in CLASSES}