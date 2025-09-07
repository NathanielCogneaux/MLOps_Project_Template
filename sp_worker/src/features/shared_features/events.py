import pandas as pd
from typing import Optional
import logging

from utils.data_reader import file_search_timestamp, load_events_data
from config.settings import DEFAULT_TIMEZONE

logger = logging.getLogger(__name__)


def get_event_feature_B(property_id: int) -> pd.DataFrame:

    ### --- OMITTED --- ###

    if df_events is not None and not df_events.empty:
        return df_events[["checkIn", "event_importance"]]

    raise RuntimeError(
        f"[FATAL] Could not load event feature B data for property_id={property_id} "
        f"on date={date} even after fallback with sub_charts_updater('B')."
    )


def add_events_features(df: pd.DataFrame, col: str, property_id: int) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return df
