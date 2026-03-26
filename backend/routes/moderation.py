from fastapi import APIRouter, UploadFile, File
import shutil
import os
import uuid

from services.pipeline import process_video

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/moderate-video")
async def moderate_video(file: UploadFile = File(...)):
    """
    Upload video → run pipeline → return moderation results
    """

    # ==============================
    # 1. SAVE FILE (UNIQUE NAME)
    # ==============================
    try:
        unique_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1]
        filename = f"{unique_id}{ext}"

        video_path = os.path.join(UPLOAD_DIR, filename)

        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    except Exception as e:
        return {
            "status": "error",
            "message": f"File upload failed: {str(e)}"
        }

    # ==============================
    # 2. RUN PIPELINE
    # ==============================
    try:
        result = process_video(video_path)

    except Exception as e:
        return {
            "status": "error",
            "message": f"Processing failed: {str(e)}"
        }

    # ==============================
    # 3. CLEANUP VIDEO FILE
    # ==============================
    try:
        if os.path.exists(video_path):
            os.remove(video_path)
    except:
        pass

    # ==============================
    # 4. RETURN RESPONSE
    # ==============================
    return {
        "status": "success",
        **result
    }