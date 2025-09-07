from fastapi import APIRouter, Depends, HTTPException, Query
from services.data_service import SmartPricingDataService
from controllers.dependencies import get_data_service
from models.data_models import (
    ScrapType,
    CompPricesResponse,
    AIPricesResponse,
    MarketStatsResponse,
    EventsResponse,
    PropertiesResponse,
)
import logging

from config.custom_logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/comp-prices/{property_id}", response_model=CompPricesResponse)
async def get_comp_prices(
    property_id: int,
    date: str = Query(
        ..., description="Date in ISO8601 format (e.g. 2025-08-26T12:53:27+09:00)"
    ),
    scrap_type: ScrapType = Query(..., description="Scraping type (A=hourly, B=daily)"),
    data_service: SmartPricingDataService = Depends(get_data_service),
) -> CompPricesResponse:
    """Get competitor prices for a property on a specific date"""
    try:
        return await data_service.get_comp_prices(property_id, date, scrap_type.value)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving comp prices: {e}")
        raise HTTPException(
            status_code=500, detail="Error retrieving competitor prices"
        )


@router.get("/ai-prices/{property_id}", response_model=AIPricesResponse)
async def get_ai_prices(
    property_id: int,
    date: str = Query(
        ..., description="Date in ISO8601 format (e.g. 2025-08-26T12:53:27+09:00)"
    ),
    model: str = Query(..., description="Model type (baseline, optimized_baseline)"),
    scrap_type: ScrapType = Query(..., description="Scraping type (A=hourly, B=daily)"),
    data_service: SmartPricingDataService = Depends(get_data_service),
) -> AIPricesResponse:
    """Get AI price predictions for a property"""
    try:
        return await data_service.get_ai_prices(
            property_id, date, model, scrap_type.value
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving AI prices: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving AI prices")


@router.get("/market-stats/{property_id}", response_model=MarketStatsResponse)
async def get_market_stats(
    property_id: int,
    date: str = Query(
        ..., description="Date in ISO8601 format (e.g. 2025-08-26T12:53:27+09:00)"
    ),
    data_service: SmartPricingDataService = Depends(get_data_service),
) -> MarketStatsResponse:
    """Get market statistics for a property"""
    try:
        return await data_service.get_market_stats(property_id, date)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving market stats: {e}")
        raise HTTPException(
            status_code=500, detail="Error retrieving market statistics"
        )


@router.get("/events/{property_id}", response_model=EventsResponse)
async def get_events(
    property_id: int,
    date: str = Query(
        ..., description="Date in ISO8601 format (e.g. 2025-08-26T12:53:27+09:00)"
    ),
    data_service: SmartPricingDataService = Depends(get_data_service),
) -> EventsResponse:
    """Get events data for a property"""
    try:
        return await data_service.get_events(property_id, date)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving events: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving events")


@router.get("/properties", response_model=PropertiesResponse)
async def get_properties(
    data_service: SmartPricingDataService = Depends(get_data_service),
) -> PropertiesResponse:
    """Get all properties data"""
    try:
        return await data_service.get_properties()
    except Exception as e:
        logger.error(f"Error retrieving properties: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving properties")
