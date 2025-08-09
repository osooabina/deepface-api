from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from deepface import DeepFace
import cv2
import numpy as np
import base64
import uvicorn
from typing import Optional

# Define the FastAPI application
app = FastAPI(
    title="DeepFace Verification API",
    description="A microservice for facial verification using the DeepFace library.",
    version="1.0.0",
)

# --- Pydantic Model for Request Body ---
class VerificationRequest(BaseModel):
    """
    Data model for the verification request body.
    Expects two images as base64-encoded strings.
    """
    img1_base64: str
    img2_base64: str
    model_name: Optional[str] = "VGG-Face"
    distance_metric: Optional[str] = "cosine"

# --- Helper Functions ---
def base64_to_image(base64_string: str):
    """Decodes a base64 string into a OpenCV image format (numpy array)."""
    try:
        # The base64 string might contain 'data:image/jpeg;base64,' prefix. Remove it.
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]
        
        img_bytes = base64.b64decode(base64_string)
        img_np = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Could not decode base64 string into an image.")
        
        return img
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 string: {str(e)}")

# --- API Endpoints ---
@app.post("/verify_face")
async def verify_face(request: VerificationRequest):
    """
    Performs a 1:1 facial verification between two images.
    
    Args:
        request (VerificationRequest): A Pydantic model containing two base64-encoded images.

    Returns:
        dict: A dictionary containing the verification result.
    """
    try:
        # Decode base64 strings to images
        img1 = base64_to_image(request.img1_base64)
        img2 = base64_to_image(request.img2_base64)

        # Use DeepFace to verify the images
        result = DeepFace.verify(
            img1_path=img1, 
            img2_path=img2,
            model_name=request.model_name,
            distance_metric=request.distance_metric
        )
        
        # DeepFace returns a dictionary; we'll return it as is.
        return result

    except HTTPException as http_exc:
        raise http_exc
    except ValueError as val_exc:
        raise HTTPException(status_code=400, detail=str(val_exc))
    except Exception as e:
        # Catch any other unexpected errors and provide a clear message
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred during facial verification: {str(e)}"
        )

# A simple root endpoint to show the API is running
@app.get("/")
def read_root():
    return {"message": "DeepFace Verification API is running."}

# --- For local testing ---
# To run this file locally, use: uvicorn main:app --reload
# You'll need to install the dependencies:
# pip install fastapi deepface uvicorn "python-multipart"
# pip install "uvicorn[standard]"
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
