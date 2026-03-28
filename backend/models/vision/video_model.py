import cv2
import numpy as np
from PIL import Image
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as T
import timm

# =========================================================
# CONFIG
# =========================================================

@dataclass
class InferConfig:
    checkpoint: str = "runs/exp1/best_model.pt"
    image_size: int = 224
    num_frames: int = 16
    backbone_name: str = "convnext_tiny.fb_in1k"
    backbone_embed_dim: int = 768
    proj_dim: int = 512
    tcn_dropout: float = 0.25
    threshold_nudity: float = 0.7
    threshold_violence: float = 0.7


# =========================================================
# MODEL
# =========================================================

class ResidualTCNBlock(nn.Module):
    def __init__(self, channels, dilation, dropout):
        super().__init__()
        self.conv1 = nn.Conv1d(channels, channels, 3, padding=dilation, dilation=dilation)
        self.conv2 = nn.Conv1d(channels, channels, 3, padding=dilation, dilation=dilation)
        self.norm1 = nn.BatchNorm1d(channels)
        self.norm2 = nn.BatchNorm1d(channels)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        residual = x
        x = self.dropout(F.gelu(self.norm1(self.conv1(x))))
        x = self.dropout(F.gelu(self.norm2(self.conv2(x))))
        return x + residual


class AttentionPool1D(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.attn = nn.Linear(dim, 1)

    def forward(self, x):
        w = self.attn(x).squeeze(-1)
        a = torch.softmax(w, dim=1)
        pooled = torch.sum(x * a.unsqueeze(-1), dim=1)
        return pooled


class VideoModerationModel(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.backbone = timm.create_model(
            cfg.backbone_name,
            pretrained=False,
            num_classes=0,
            global_pool="avg",
        )

        self.proj = nn.Linear(cfg.backbone_embed_dim, cfg.proj_dim)

        self.tcn = nn.Sequential(
            ResidualTCNBlock(cfg.proj_dim, 1, cfg.tcn_dropout),
            ResidualTCNBlock(cfg.proj_dim, 2, cfg.tcn_dropout),
            ResidualTCNBlock(cfg.proj_dim, 4, cfg.tcn_dropout),
        )

        self.nudity_pool = AttentionPool1D(cfg.proj_dim)
        self.violence_pool = AttentionPool1D(cfg.proj_dim)

        self.nudity_head = nn.Sequential(
            nn.LayerNorm(cfg.proj_dim),
            nn.Dropout(0.3),
            nn.Linear(cfg.proj_dim, cfg.proj_dim // 2),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(cfg.proj_dim // 2, 1),
        )

        self.violence_head = nn.Sequential(
            nn.LayerNorm(cfg.proj_dim),
            nn.Dropout(0.3),
            nn.Linear(cfg.proj_dim, cfg.proj_dim // 2),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(cfg.proj_dim // 2, 1),
        )
    def forward(self, video):
        b, t, c, h, w = video.shape

        x = video.view(b * t, c, h, w)
        feats = self.backbone(x)
        feats = self.proj(feats)
        feats = feats.view(b, t, -1)

        x = feats.transpose(1, 2)
        x = self.tcn(x).transpose(1, 2)

        z_n = self.nudity_pool(x)
        z_v = self.violence_pool(x)

        logit_n = self.nudity_head(z_n).squeeze(-1)
        logit_v = self.violence_head(z_v).squeeze(-1)

        return torch.stack([logit_n, logit_v], dim=1)


# =========================================================
# TRANSFORM
# =========================================================

def build_transform(image_size):
    return T.Compose([
        T.Resize((image_size, image_size)),
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406],
                    [0.229, 0.224, 0.225]),
    ])


def frame_to_pil(frame):
    return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


# =========================================================
# VIDEO PROCESSING
# =========================================================

def get_video_metadata(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return fps, total_frames


def get_clip_ranges(video_path, clip_duration=5):
    fps, total_frames = get_video_metadata(video_path)
    clip_size = int(fps * clip_duration)

    ranges = []
    for start in range(0, total_frames, clip_size):
        end = min(start + clip_size, total_frames)
        ranges.append((start, end))

    return ranges


def read_frames_from_range(video_path, start, end, num_frames):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start)

    length = end - start
    idxs = np.linspace(0, length - 1, num_frames).astype(int)

    frames = []
    i = 0

    while cap.isOpened() and i < length:
        ret, frame = cap.read()
        if not ret:
            break
        if i in idxs:
            frames.append(frame)
        i += 1

    cap.release()

    while len(frames) < num_frames:
        frames.append(frames[-1].copy())

    return frames[:num_frames]


# =========================================================
# MAIN INFERENCE
# =========================================================

def classify_video_clips(video_path, cfg):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = VideoModerationModel(cfg)
    ckpt = torch.load(cfg.checkpoint, map_location="cpu")
    model.load_state_dict(ckpt["model_state"])
    model.to(device)
    model.eval()

    transform = build_transform(cfg.image_size)

    clip_ranges = get_clip_ranges(video_path, 5)

    all_preds = []

    for start, end in clip_ranges:
        frames = read_frames_from_range(video_path, start, end, cfg.num_frames)
        frames = [transform(frame_to_pil(f)) for f in frames]
        video = torch.stack(frames).unsqueeze(0).to(device)

        with torch.no_grad():
            logits = model(video)
            probs = torch.sigmoid(logits)[0].cpu().numpy()

        p_n, p_v = float(probs[0]), float(probs[1])

        all_preds.append({
            "start": start,
            "end": end,
            "nudity": p_n,
            "violence": p_v
        })

    # MAX POOLING
    max_n = max(p["nudity"] for p in all_preds)
    max_v = max(p["violence"] for p in all_preds)

    # FINAL DECISION
    if max_n >= cfg.threshold_nudity and max_n >= max_v:
        label = "nudity"
    elif max_v >= cfg.threshold_violence:
        label = "violence"
    else:
        label = "neutral"

    # ONLY RETURN FINAL RESULT
    return {
        "video": video_path,
        "nudity_prob": max_n,
        "violence_prob": max_v,
        "label": label
    }

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--checkpoint", default="runs/exp1/best_model.pt")
    args = parser.parse_args()

    cfg = InferConfig(checkpoint=args.checkpoint)

    result = classify_video_clips(args.video, cfg)
    print(result)