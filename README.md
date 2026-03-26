# 🛡️ Aegis AI — Multimodal Video Content Moderation

Aegis AI is a multimodal content moderation system that analyzes videos using **text, audio, and visual signals** to detect harmful content such as:

- Hate Speech
- Violence
- Sexual Content
- Neutral Content

It combines deep learning models across multiple modalities and produces:
- Final classification
- Confidence scores
- Segment-wise analysis with timestamps

---

## 🔥 Features

- 🎥 Video upload and preview
- 🧠 Multimodal AI analysis (Text + Audio + Vision)
- ⏱️ Timestamp-based segmentation
- 📊 Confidence scores across modalities
- 📈 Interactive frontend dashboard
- 🧩 Segment-level explainability

---

## 🧠 How It Works

### Pipeline Overview

```
Video
↓
Audio Extraction
↓
Transcription (Whisper)
↓
Segment Generation (with gap filling)
↓
For each segment:
  → Text Model (RoBERTa)
  → Audio Model (CNN)
  → Vision Model (YOLO + CNN)
↓
Segment-wise results
↓
Frontend aggregation & visualization
```
---

## 🧱 Project Structure

Cornerstone_Project/
│
├── backend/
│ ├── models/
│ │ ├── audio/
│ │ │ ├── audio_moderation_model.h5
│ │ │ └── inference.py
│ │ │
│ │ ├── vision/
│ │ │ ├── best_model.pth
│ │ │ ├── inference.py
│ │ │ └── violence_model.py
│ │ │
│ │ └── text/
│ │ ├── inference.py
│ │ └── roberta/
│ │ ├── config.json
│ │ ├── tokenizer.json
│ │ ├── tokenizer_config.json
│ │ └── model.safetensors
│ │
│ ├── services/
│ │ └── pipeline.py
│ │
│ ├── routes/
│ │ └── moderation.py
│ │
│ ├── utils/
│ │ ├── media.py
│ │ └── transcription.py
│ │
│ ├── uploads/
│ ├── temp/
│ └── main.py
│
├── frontend/
│ ├── src/
│ │ ├── components/
│ │ ├── pages/
│ │ ├── hooks/
│ │ ├── services/
│ │ └── utils/
│ │
│ ├── public/
│ ├── index.html
│ ├── package.json
│ └── vite.config.js
│
└── README.md


---

## ⚙️ Installation & Setup

### 🔹 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```
### 🔹 2. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 🔹 3. Install Required System Dependencies
Make sure you have:

Python 3.9+
FFmpeg (required for audio/video processing)
```bash
sudo apt install ffmpeg
```

### 🔹 4. Run Backend
```bash
uvicorn main:app --reload
```
Backend will run at:
```bash
http://127.0.0.1:8000
```

### 🔹 5. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Backend will run at:
```bash
http://localhost:5173
```

📦 Model Download (IMPORTANT)

Due to size constraints, model files are not included in the repository.

👉 Download all models from the link below:

📁 After Download, Place Files Like This:

backend/models/

├── audio/
│   └── audio\_moderation\_model.h5
│
├── vision/
│   └── best\_model.pth
│
└── text/
    └── roberta/
        ├── config.json
        ├── tokenizer.json
        ├── tokenizer\_config.json
        └── model.safetensors

📊 Output Format

The backend returns:
{
  "verdict": "violence",
  "confidence": 0.82,
  "transcript": "...",
  "segments": [
    {
      "start": 2.0,
      "end": 6.5,
      "text": "...",
      "modalities": {
        "text": {...},
        "audio": {...},
        "vision": {...}
      }
    }
  ]
}

🚧 Current Limitations
Models are not fully optimized (non-SOTA)
Processing is slower due to segment-wise video slicing
Audio & vision are computed per segment (expensive but accurate)
🔮 Future Improvements
⚡ Faster pipeline using FFmpeg instead of MoviePy
🧠 Better aggregation (weighted pooling)
🎯 Improved model accuracy
🎥 Clickable timeline UI
🌐 Scalable deployment
👨‍💻 Authors
Siddharth Tamak
Team Members (add names)
📜 License

This project is for academic/research purposes.

⭐ Acknowledgements
OpenAI Whisper
HuggingFace Transformers
YOLO-based vision models
TensorFlow / PyTorch ecosystem


---

# 🚀 What You Should Do Next

1. Paste this into `README.md`
2. Replace:
   - `YOUR_USERNAME`
   - `YOUR_REPO`
   - Google Drive link
3. Add team members

---

# 🔥 This README Will Help You

- Look **professional**
- Make your repo understandable
- Help evaluators quickly grasp your system
- Stand out from typical student projects

---

If you want next:
👉 I can also help you create a **clean GitHub repo structure + .gitignore (important for venv + models)**
