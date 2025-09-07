import pandas as pd
import numpy as np
import pytz

from utils.data_manip import df_merger
from config.settings import DEFAULT_TIMEZONE

tz = pytz.timezone(DEFAULT_TIMEZONE)

today = pd.Timestamp.now(tz=tz).normalize()
tomorrow = today + pd.Timedelta(days=1)
max_date = today + pd.DateOffset(days=179)


def get_comp_price_data(
    dict_df_comp: dict[str, pd.DataFrame], scrap_type: str
) -> dict[str, pd.DataFrame]:

    ### --- OMITTED --- ###

    return dict_df_prices


def get_market_trend_chart(
    dict_df_comp_B: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:

    ### --- OMITTED --- ###

    return dict_price_stats


def get_events_data(
    dict_df_comp_B: dict[str, pd.DataFrame],
) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return df_event_importance
