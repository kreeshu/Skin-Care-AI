from fastapi import APIRouter, HTTPException
from typing import Optional

from backend.services.product_service import (
    get_products,
    get_product,
    get_categories,
)

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("")
async def list_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    skin_type: Optional[str] = None,
    sort_by: str = "rating",
    page: int = 1,
    page_size: int = 20,
):
    result = get_products(
        search=search,
        category=category,
        skin_type=skin_type,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    return result


@router.get("/categories")
async def list_categories():
    return {"categories": get_categories()}


@router.get("/{product_id}")
async def get_product_detail(product_id: int):
    product = get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
