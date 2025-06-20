from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from deepface import DeepFace
import numpy as np
from PIL import Image
import io

app = FastAPI()

def read_imagefile(file) -> np.ndarray:
    image = Image.open(io.BytesIO(file))
    return np.array(image)

@app.post("/verify")
async def verify_faces(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    try:
        img1 = read_imagefile(await file1.read())
        img2 = read_imagefile(await file2.read())

        result = DeepFace.verify(img1_path=img1, img2_path=img2)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
