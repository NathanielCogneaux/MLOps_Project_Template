import pandas as pd
import asyncio
import logging
from config.custom_logging import setup_logging

from utils.data_reader import (
    load_comp_prices,
    load_market_stats,
    load_events_data,
    load_ai_prices,
    load_properties,
    load_latest_updates_raw_data,
    load_latest_updates_processed,
    file_search_timestamp,
)
from utils.response_builders import (
    build_ai_prices_obj,
    build_comp_prices_objects,
    build_market_stats_objects,
    build_events_objects,
    build_properties_objects,
    build_updates_response,
)
from models.data_models import (
    AIPricesResponse,
    CompPricesResponse,
    MarketStatsResponse,
    EventsResponse,
    PropertiesResponse,
    UpdateResponse,
)
from config.settings import DEFAULT_TIMEZONE

setup_logging()
logger = logging.getLogger(__name__)


class SmartPricingDataService:

    async def get_comp_prices(
        self,
        property_id: int,
        date: str,
        scrap_type: str,
    ) -> CompPricesResponse:
        """Get competitor prices data"""
        try:
            date_ts = (
                pd.to_datetime(date).tz_convert(DEFAULT_TIMEZONE)
                if pd.to_datetime(date).tzinfo
                else pd.to_datetime(date).tz_localize(DEFAULT_TIMEZONE)
            )
            date_ts = file_search_timestamp(date_ts, scrap_type)

            # Run in thread pool to avoid blocking
            comp_data = await asyncio.get_event_loop().run_in_executor(
                None, load_comp_prices, date_ts, property_id, scrap_type
            )

            if comp_data is None:
                raise ValueError(
                    f"No competitor prices found for property {property_id} on {date}"
                )

            comp_prices_list = build_comp_prices_objects(comp_data)

            return CompPricesResponse(comp_prices=comp_prices_list)

        except Exception as e:
            logger.error(f"Error loading comp prices: {e}")
            raise

    async def get_ai_prices(
        self,
        property_id: int,
        date: str,
        model: str,
        scrap_type: str,
    ) -> AIPricesResponse:
        """Get AI price predictions"""
        try:
            date_ts = (
                pd.to_datetime(date).tz_convert(DEFAULT_TIMEZONE)
                if pd.to_datetime(date).tzinfo
                else pd.to_datetime(date).tz_localize(DEFAULT_TIMEZONE)
            )
            date_ts = file_search_timestamp(date_ts, scrap_type)

            ai_data = await asyncio.get_event_loop().run_in_executor(
                None, load_ai_prices, date_ts, model, property_id, scrap_type
            )

            if ai_data is None:
                raise ValueError(
                    f"No AI prices found for property {property_id}, model {model} on {date}"
                )

            ai_prices_list = build_ai_prices_obj(ai_data)

            return AIPricesResponse(ai_prices=ai_prices_list)

        except Exception as e:
            logger.error(f"Error loading AI prices: {e}")
            raise

    async def get_market_stats(
        self,
        property_id: int,
        date: str,
    ) -> MarketStatsResponse:
        """Get market statistics"""
        try:
            date_ts = (
                pd.to_datetime(date).tz_convert(DEFAULT_TIMEZONE)
                if pd.to_datetime(date).tzinfo
                else pd.to_datetime(date).tz_localize(DEFAULT_TIMEZONE)
            )
            date_ts = file_search_timestamp(date_ts, "B")

            market_data = await asyncio.get_event_loop().run_in_executor(
                None, load_market_stats, date_ts, property_id
            )

            if market_data is None:
                raise ValueError(
                    f"No market stats found for property {property_id} on {date}"
                )

            market_stats_list = build_market_stats_objects(market_data)

            return MarketStatsResponse(market_stats=market_stats_list)

        except Exception as e:
            logger.error(f"Error loading market stats: {e}")
            raise

    async def get_events(
        self,
        property_id: int,
        date: str,
    ) -> EventsResponse:
        """Get events data"""
        try:
            date_ts = (
                pd.to_datetime(date).tz_convert(DEFAULT_TIMEZONE)
                if pd.to_datetime(date).tzinfo
                else pd.to_datetime(date).tz_localize(DEFAULT_TIMEZONE)
            )
            today = pd.Timestamp.now(tz=DEFAULT_TIMEZONE).normalize()
            cutoff = today + pd.Timedelta(days=180)
            date_ts = file_search_timestamp(date_ts, "B")

            events_data = await asyncio.get_event_loop().run_in_executor(
                None, load_events_data, date_ts, property_id
            )

            if events_data is None:
                raise ValueError(
                    f"No events found for property {property_id} on {date}"
                )

            # filter by 180-day window -> saved more than 180 days (without names) for AI trainings
            events_data = events_data[
                (events_data["checkIn"] >= today) & (events_data["checkIn"] <= cutoff)
            ]

            events_list = build_events_objects(events_data)

            return EventsResponse(events=events_list)

        except Exception as e:
            logger.error(f"Error loading events: {e}")
            raise

    async def get_properties(self) -> PropertiesResponse:
        """Get properties data"""
        try:
            properties = await asyncio.get_event_loop().run_in_executor(
                None, load_properties
            )

            properties_list, all_property_ids = build_properties_objects(properties)

            return PropertiesResponse(
                properties=properties_list, all_properties_ids=all_property_ids
            )

        except Exception as e:
            logger.error(f"Error loading properties: {e}")
            raise

    async def get_latest_updates(self, scrap_type: str) -> UpdateResponse:
        """Get latest update timestamps"""
        try:
            raw_updates = await asyncio.get_event_loop().run_in_executor(
                None, load_latest_updates_raw_data, scrap_type
            )
            processed_updates = await asyncio.get_event_loop().run_in_executor(
                None, load_latest_updates_processed, scrap_type
            )

            return build_updates_response(scrap_type, raw_updates, processed_updates)

        except Exception as e:
            logger.error(f"Error loading latest updates: {e}")
            raise
