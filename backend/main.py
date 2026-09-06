import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router as analysis_router
from backend.routes.chat import router as chat_router
from backend.routes.products import router as products_router
from backend.routes.conditions import router as conditions_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = FastAPI(
    title="SkinCare AI API",
    description="AI-powered skin condition detection and product recommendation API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router)
app.include_router(chat_router)
app.include_router(products_router)
app.include_router(conditions_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "SkinCare AI API"}
