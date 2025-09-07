from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class ScrapType(str, Enum):
    A = "A"  # hourly
    B = "B"  # daily


class DateValues(BaseModel):
    checkIn: str
    values: list[float]


class ChannelCompPrices(BaseModel):
    channel: str
    dates: list[DateValues]


class CompPricesResponse(BaseModel):
    comp_prices: list[ChannelCompPrices]


class PriceEntry(BaseModel):
    checkIn: str
    price: float


class AIPrices(BaseModel):
    name: str
    channel: str
    prices: list[PriceEntry]


class AIPricesResponse(BaseModel):
    ai_prices: list[AIPrices]


class DateStats(BaseModel):
    checkIn: str
    min: float
    max: float
    median: float
    p5: float
    p15: float
    p25: float
    p35: float
    p45: float
    p55: float
    p65: float
    p75: float
    p85: float
    p95: float


class ChannelMarketStats(BaseModel):
    channel: str
    dates: list[DateStats]


class MarketStatsResponse(BaseModel):
    market_stats: list[ChannelMarketStats]


class EventEntry(BaseModel):
    checkIn: str
    event_importance: int
    event_name: Optional[str]


class EventsResponse(BaseModel):
    events: list[EventEntry]


class HotelProperty(BaseModel):
    property_id: int
    client_ids: list[int]
    comp_ids: list[int]
    is_using_IMS: bool


class PropertiesResponse(BaseModel):
    properties: List[HotelProperty]
    all_properties_ids: List[int]


class UpdateResponse(BaseModel):
    scrap_type: str
    raw_data_updates: dict[str, dict[str, str]]  # {ota_name: {hotel_id: iso_timestamp}}
    processed_data_updates: dict[str, str]  # {property_id: iso_timestamp}
