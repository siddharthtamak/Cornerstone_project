import os
import torch

# Import your existing pipeline
from models.vision.violence_model import ViolenceDetectionModel
from models.vision.inference_pipeline import VideoViolenceInference
# (we'll fix this import below depending on your file naming)

# ==============================
# CONFIG
# ==============================

CLASSES = ["neutral", "sexual_content", "violence", "hate_speech"]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "best_model.pth")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ==============================
# LOAD MODEL (GLOBAL)
# ==============================

print("🎥 Loading Vision Model...")

if os.path.exists(MODEL_PATH):
    try:
        vision_pipeline = VideoViolenceInference(
            classifier_path=MODEL_PATH,
            device=device
        )
        print("✅ Vision model loaded")
    except Exception as e:
        print(f"❌ Vision model load error: {e}")
        vision_pipeline = None
else:
    print(f"⚠️ Vision model not found at {MODEL_PATH}")
    vision_pipeline = None


# ==============================
# VISION INFERENCE FUNCTION
# ==============================

def predict_vision(video_path: str):
    """
    Runs violence detection on video.
    Maps result to 4-class output format.
    """

    if vision_pipeline is None:
        return {c: 0.0 for c in CLASSES}

    try:
        result = vision_pipeline.process_video(video_path)

        if "classification" not in result:
            return {c: 0.0 for c in CLASSES}

        violence_prob = result["classification"]["violence_prob"]
        neutral_prob = 1.0 - violence_prob

        return {
            "neutral": float(neutral_prob),
            "sexual_content": 0.0,
            "violence": float(violence_prob),
            "hate_speech": 0.0
        }

    except Exception as e:
        print(f"❌ Vision inference error: {e}")
        return {c: 0.0 for c in CLASSES}