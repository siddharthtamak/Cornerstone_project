"""
Simplified Inference Pipeline: Violence Detection Only
"""

import torch
import cv2
import numpy as np
from pathlib import Path
import json
from typing import Dict, List
import time
import os

class VideoViolenceInference:
    def __init__(self, classifier_path, device='cuda'):

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        from models.vision.violence_model import ViolenceDetectionModel

        self.classifier = ViolenceDetectionModel(num_classes=2)

        if os.path.isdir(classifier_path):
            # If it's a folder, PyTorch 2.0+ can often load it if you point to the DIR
            checkpoint = torch.load(classifier_path, map_location=self.device)
        else:
            checkpoint = torch.load(classifier_path, map_location=self.device)

        self.classifier.load_state_dict(checkpoint['model_state_dict'])

        self.classifier.to(self.device)
        self.classifier.eval()

        print(f"Violence classifier loaded on {self.device}")

    def extract_frames(self, video_path, num_frames=16):
        """Extract frames uniformly from video"""

        cap = cv2.VideoCapture(str(video_path))

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        duration = total_frames / fps if fps > 0 else 0

        if total_frames < num_frames:
            frame_indices = list(range(total_frames))
        else:
            frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)

        frames = []

        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()

            if ret:
                frames.append(frame)

        cap.release()

        metadata = {
            "total_frames": total_frames,
            "fps": fps,
            "duration": duration,
            "extracted_frames": len(frames)
        }

        return np.array(frames), metadata

    def preprocess_frames(self, frames):
        """Prepare frames for classifier"""

        processed = []

        for frame in frames:

            frame = cv2.resize(frame, (224, 224))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame = frame.astype(np.float32) / 255.0
            processed.append(frame)

        frames_tensor = torch.from_numpy(
            np.array(processed)
        ).permute(0, 3, 1, 2)

        mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)

        frames_tensor = (frames_tensor - mean) / std

        return frames_tensor

    def classify_violence(self, frames_tensor):
        """Run model inference"""

        with torch.no_grad():

            frames_tensor = frames_tensor.unsqueeze(0).to(self.device)

            logits = self.classifier(frames_tensor)

            probs = torch.softmax(logits, dim=1)

            pred_class = torch.argmax(probs, dim=1).item()

            confidence = probs[0][pred_class].item()

            is_violent = pred_class == 1

        return {
            "is_violent": is_violent,
            "confidence": confidence,
            "violence_prob": probs[0][1].item(),
            "non_violence_prob": probs[0][0].item()
        }

    def process_video(self, video_path):

        start_time = time.time()

        print(f"\nProcessing: {video_path}")
        print("-" * 40)

        frames, metadata = self.extract_frames(video_path)

        if len(frames) == 0:
            return {"error": "Could not extract frames"}

        frames_tensor = self.preprocess_frames(frames)

        classification = self.classify_violence(frames_tensor)

        processing_time = time.time() - start_time

        result = {
            "video_path": str(video_path),
            "metadata": metadata,
            "classification": classification,
            "processing_time": processing_time
        }

        self._print_results(result)

        return result

    def _print_results(self, result):

        print("\n=== VIOLENCE DETECTION RESULT ===")

        c = result["classification"]

        print(f"Violence Detected: {'YES' if c['is_violent'] else 'NO'}")
        print(f"Confidence: {c['confidence']:.2%}")
        print(f"Violence Probability: {c['violence_prob']:.2%}")

        print(f"\nProcessing Time: {result['processing_time']:.2f}s")

    def process_batch(self, video_paths, output_json=None):

        results = []

        for video_path in video_paths:

            result = self.process_video(video_path)

            results.append(result)

        if output_json:

            with open(output_json, "w") as f:
                json.dump(results, f, indent=2)

        return results


if __name__ == "__main__":

    pipeline = VideoViolenceInference(
        classifier_path="./checkpoints/best_model.pth",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )

    pipeline.process_video("test_video.mp4")