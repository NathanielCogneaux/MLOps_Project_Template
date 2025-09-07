import pandas as pd
from typing import Any

from models.data_models import (
    AIPrices,
    PriceEntry,
    ChannelCompPrices,
    DateValues,
    ChannelMarketStats,
    DateStats,
    EventEntry,
    HotelProperty,
    UpdateResponse,
)


def build_ai_prices_obj(df: pd.DataFrame) -> list[AIPrices]:
    result = []
    for (name, channel), group in df.groupby(["name", "channel"], observed=True):
        prices = [
            PriceEntry(checkIn=str(row["checkIn"]), price=row["predicted_price"])
            for _, row in group.iterrows()
        ]
        result.append(AIPrices(name=name, channel=channel, prices=prices))
    return result


def build_comp_prices_objects(
    dict_df: dict[str, pd.DataFrame],
) -> list[ChannelCompPrices]:
    result = []
    for channel, df in dict_df.items():
        df = df.copy()
        # Just in case, ensure checkIn column is str (for grouping) and values
        df["checkIn"] = df["checkIn"].astype(str)
        dates = [
            DateValues(
                checkIn=str(checkin),  # Make sure it's a string!
                values=[float(v) for v in group["price_display"]],
            )
            for checkin, group in df.groupby("checkIn")
        ]
        result.append(ChannelCompPrices(channel=channel, dates=dates))
    return result


def build_market_stats_objects(
    dict_df: dict[str, pd.DataFrame],
) -> list[ChannelMarketStats]:
    result = []
    for channel, df in dict_df.items():
        df = df.copy()
        df["checkIn"] = df["checkIn"].astype(str)
        dates = [
            DateStats(
                checkIn=row["checkIn"],
                min=float(row["min"]),
                max=float(row["max"]),
                median=float(row["median"]),
                p5=float(row["p5"]),
                p15=float(row["p15"]),
                p25=float(row["p25"]),
                p35=float(row["p35"]),
                p45=float(row["p45"]),
                p55=float(row["p55"]),
                p65=float(row["p65"]),
                p75=float(row["p75"]),
                p85=float(row["p85"]),
                p95=float(row["p95"]),
            )
            for _, row in df.iterrows()
        ]
        result.append(ChannelMarketStats(channel=channel, dates=dates))
    return result


def build_events_objects(df: pd.DataFrame) -> list[EventEntry]:
    df = df.copy()
    df["checkIn"] = df["checkIn"].astype(str)
    return [
        EventEntry(
            checkIn=row["checkIn"],
            event_importance=int(row["event_importance"]),
            event_name=row.get(
                "event_local_name"
            ),  # .get() handles optional field safely
        )
        for _, row in df.iterrows()
    ]


def build_properties_objects(properties_list) -> tuple[list[HotelProperty], list[int]]:
    """
    Convert loaded HotelProperty objects to Pydantic models, excluding df_rt_mapping
    Returns tuple of (properties_list, all_property_ids)
    """
    pydantic_properties = []
    all_property_ids = []

    for prop in properties_list:
        pydantic_prop = HotelProperty(
            property_id=prop.property_id,
            client_ids=prop.client_ids,
            comp_ids=prop.comp_ids,
            is_using_IMS=prop.is_using_IMS,
        )
        pydantic_properties.append(pydantic_prop)
        all_property_ids.append(prop.property_id)

    return pydantic_properties, all_property_ids


def build_updates_response(
    scrap_type: str,
    raw_updates: dict[str, dict[str, Any]],
    processed_updates: dict[int, Any],
) -> UpdateResponse:
    """
    Build updates response with proper timestamp serialization
    """
    # Convert timestamps to ISO strings for JSON serialization
    raw_updates_serializable = {}
    for ota, hotels in raw_updates.items():
        raw_updates_serializable[ota] = {
            str(hotel_id): ts.isoformat() for hotel_id, ts in hotels.items()
        }

    processed_updates_serializable = {
        str(pid): ts.isoformat() for pid, ts in processed_updates.items()
    }

    return UpdateResponse(
        scrap_type=scrap_type,
        raw_data_updates=raw_updates_serializable,
        processed_data_updates=processed_updates_serializable,
    )
