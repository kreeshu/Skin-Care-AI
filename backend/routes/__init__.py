from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from backend.services.analyzer_service import analyze_image

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze")
async def analyze_skin(
    image: UploadFile = File(...),
    use_slm: bool = Form(False),
):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await image.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

    try:
        result = analyze_image(contents, use_slm=use_slm)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    return JSONResponse(content=result)
