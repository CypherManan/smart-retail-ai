from fastapi import APIRouter, UploadFile, File
from app.services import pipeline
from app.schemas import FaceRecognitionResponse, ProductClassificationResponse

router = APIRouter(tags=["vision"])


@router.post("/recognize-face", response_model=FaceRecognitionResponse)
async def recognize_face(file: UploadFile = File(...)):
    image_bytes = await file.read()
    return pipeline.recognize_face(image_bytes)


@router.post("/classify-product", response_model=ProductClassificationResponse)
async def classify_product(file: UploadFile = File(...)):
    image_bytes = await file.read()
    return pipeline.classify_product(image_bytes)
