from fastapi import APIRouter, HTTPException

from backend.services.product_service import get_conditions, get_condition, get_skin_types

router = APIRouter(prefix="/api/conditions", tags=["conditions"])


@router.get("")
async def list_conditions():
    return {"conditions": get_conditions()}


@router.get("/skin-types")
async def list_skin_types():
    return {"skin_types": get_skin_types()}


@router.get("/{name}")
async def get_condition_detail(name: str):
    condition = get_condition(name)
    if condition is None:
        raise HTTPException(status_code=404, detail="Condition not found")
    return condition
