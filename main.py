from fastapi import FastAPI, UploadFile, File, HTTPException
from deepface import DeepFace
import shutil
import os
import uuid

app = FastAPI()

@app.post("/verify")
async def verify_faces(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    try:
        # Save uploaded files temporarily
        img1_path = f"/tmp/{uuid.uuid4()}.jpg"
        img2_path = f"/tmp/{uuid.uuid4()}.jpg"

        with open(img1_path, "wb") as buffer:
            shutil.copyfileobj(file1.file, buffer)

        with open(img2_path, "wb") as buffer:
            shutil.copyfileobj(file2.file, buffer)

        # Run DeepFace verification
        result = DeepFace.verify(
            img1_path=img1_path,
            img2_path=img2_path,
            model_name="Facenet",
            detector_backend="retinaface"
        )

        # Clean up temp files
        os.remove(img1_path)
        os.remove(img2_path)

        return {"verified": result["verified"], "distance": result["distance"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
