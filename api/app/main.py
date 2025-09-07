from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from controllers.api import api_router
from config.custom_logging import setup_logging
import uvicorn
import logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Pricing API",
    description="API for accessing smart pricing data outputs",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/smart_pricing_api/v2")


@app.get("/")
async def root():
    return {"message": "Smart Pricing API", "version": "2.0.0"}


@app.on_event("startup")
async def startup_event():
    logger.info("Smart Pricing API starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Smart Pricing API shutting down...")


if __name__ == "__main__":
    import os

    api_port = int(os.getenv("API_PORT", 8005))
    uvicorn.run("app.main:app", host="0.0.0.0", port=api_port, reload=True)

