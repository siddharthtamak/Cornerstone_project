#!/bin/bash

echo "🚀 Setting up Aegis AI backend environment..."

# =========================
# Create virtual environment
# =========================
python3 -m venv venv

echo "✅ Virtual environment created"

# =========================
# Activate venv
# =========================
source venv/bin/activate

echo "✅ Virtual environment activated"

# =========================
# Upgrade pip
# =========================
pip install --upgrade pip

# =========================
# Install core backend
# =========================
pip install fastapi uvicorn

# =========================
# Install ML dependencies
# =========================
pip install numpy scipy

# =========================
# Install PyTorch (CPU version)
# =========================
pip install torch torchvision torchaudio

# =========================
# Install TensorFlow (audio model)
# =========================
pip install tensorflow

# =========================
# Install transformers (RoBERTa)
# =========================
pip install transformers safetensors

# =========================
# Install Whisper
# =========================
pip install openai-whisper

# =========================
# Install audio/video processing
# =========================
pip install librosa moviepy opencv-python

pip install python-multipart

pip install tim

echo "🎉 Setup complete!"

echo "👉 To activate later: source venv/bin/activate"
echo "👉 To run backend: uvicorn main:app --reload"