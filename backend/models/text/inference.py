import os
import re
import torch
import torch.nn.functional as F

from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ==============================
# CONFIG
# ==============================

CLASSES = ["neutral", "sexual_content", "violence", "hate_speech"]

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "roberta")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ==============================
# LOAD MODEL (GLOBAL)
# ==============================

print("🧠 Loading Text Model...")

if os.path.exists(MODEL_PATH):
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        text_model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH).to(device)
        text_model.eval()
        print("✅ RoBERTa loaded")
    except Exception as e:
        print(f"❌ RoBERTa load error: {e}")
        tokenizer = None
        text_model = None
else:
    print(f"⚠️ RoBERTa model not found at {MODEL_PATH}")
    tokenizer = None
    text_model = None


# ==============================
# TEXT CLASSIFICATION
# ==============================

def classify_text(text: str):
    """
    Classify a piece of text into 4 classes.
    """

    if text_model is None or tokenizer is None:
        return {c: 0.0 for c in CLASSES}

    if not text or not text.strip():
        return {
            "neutral": 1.0,
            "sexual_content": 0.0,
            "violence": 0.0,
            "hate_speech": 0.0
        }

    try:
        # ======================
        # 1. Sentence splitting
        # ======================
        raw = re.split(r'(?<=[.!?])\s+|\n+', text.strip())
        sentences = [s.strip() for s in raw if s.strip() and len(s.strip()) > 3]

        if not sentences:
            sentences = [text.strip()]

        # ======================
        # 2. Batch inference
        # ======================
        batch_size = 16
        all_probs = []

        for i in range(0, len(sentences), batch_size):
            batch = sentences[i:i + batch_size]

            inputs = tokenizer(
                batch,
                truncation=True,
                padding=True,
                max_length=128,
                return_tensors="pt"
            ).to(device)

            with torch.no_grad():
                logits = text_model(**inputs).logits

            probs = F.softmax(logits, dim=-1).cpu().numpy()
            all_probs.extend(probs)

        # ======================
        # 3. Aggregate results
        # ======================
        n = len(all_probs)

        return {
            "neutral": float(sum(p[0] for p in all_probs) / n),
            "sexual_content": float(sum(p[3] for p in all_probs) / n),
            "violence": float(sum(p[1] for p in all_probs) / n),
            "hate_speech": float(sum(p[2] for p in all_probs) / n)
        }

    except Exception as e:
        print(f"❌ Text classification error: {e}")
        return {c: 0.0 for c in CLASSES}


# ==============================
# PIPELINE ENTRY (CLEAN API)
# ==============================

def predict_text(text: str):
    """
    Wrapper for pipeline usage
    """
    return classify_text(text)