import os
import re
from datetime import timedelta
from typing import Optional, Union
import pandas as pd
import requests
import pytz
import logging
from dotenv import load_dotenv

from config.settings import DEFAULT_TIMEZONE

logger = logging.getLogger(__name__)
tz = pytz.timezone(DEFAULT_TIMEZONE)

load_dotenv()

GOV_API_KEY = os.getenv("GOV_API_KEY")


def get_area_code(area_name: str) -> Optional[str]:

    ### --- OMITTED --- ###

    return None


def get_events(
    start_date: str, end_date: str, area_name: str
) -> list[dict[str, Union[str, None]]]:

    ### --- OMITTED --- ###

    return []


def get_korean_holidays(
    start_date: str, end_date: str
) -> list[dict[str, Union[str, None]]]:

    ### --- OMITTED --- ###

    return holidays


def get_eves(df: pd.DataFrame) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return df


def get_events_and_holidays(
    start_date: str,
    end_date: str,
    area_name: str,
    with_eves: bool = True,
) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return df_all


def merge_event_importance_with_calendar_events(
    df_event_importance: pd.DataFrame,
    area_name: str,
) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return df_merged
