from fastapi import APIRouter

from backend.services.product_service import get_skin_types

router = APIRouter(prefix="/api/conditions", tags=["conditions"])


@router.get("/skin-types")
async def list_skin_types():
    return {"skin_types": get_skin_types()}
