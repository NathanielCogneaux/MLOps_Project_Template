from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from services.data_service import SmartPricingDataService
from controllers.dependencies import get_data_service
from models.data_models import ScrapType, UpdateResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/latest/{scrap_type}", response_model=UpdateResponse)
async def get_latest_updates(
    scrap_type: ScrapType,
    data_service: SmartPricingDataService = Depends(get_data_service),
) -> UpdateResponse:
    """Get latest update timestamps for raw and processed data"""
    try:
        return await data_service.get_latest_updates(scrap_type.value)
    except Exception as e:
        logger.error(f"Error retrieving latest updates: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving latest updates")


@router.get("/status")
async def get_update_status(
    data_service: SmartPricingDataService = Depends(get_data_service),
) -> dict[str, Any]:
    """Get overall update status for both scrap types"""
    try:
        status_a = await data_service.get_latest_updates("A")
        status_b = await data_service.get_latest_updates("B")

        return {
            "overall_status": "ok",
            "scrap_types": {
                "A": status_a.dict(),  # Convert Pydantic model to dict for nested response
                "B": status_b.dict(),  # Convert Pydantic model to dict for nested response
            },
        }
    except Exception as e:
        logger.error(f"Error retrieving update status: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving update status")
