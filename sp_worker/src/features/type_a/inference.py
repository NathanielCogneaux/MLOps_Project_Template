import pandas as pd
import numpy as np
from itertools import product
import pytz
import logging

from config.settings import DEFAULT_TIMEZONE
from .basic import basic_feature_engineering, categorical_handler
from ..shared_features import (
    add_events_features,
    add_temp_features,
    unseen_rooms_pred_manager,
    unseen_channels_pred_manager,
)
from utils.data_reader import load_ai_prices, file_search_timestamp


tz = pytz.timezone(DEFAULT_TIMEZONE)

logger = logging.getLogger(__name__)


def add_predicted_type_B_prices(
    prediction_data: pd.DataFrame, property_id: int, now: pd.Timestamp
) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return prediction_data


def _get_close_lead_hours_data(prediction_data, price_stats):

    ### --- OMITTED --- ###

    return prediction_data


def feature_processing_pred(
    dict_df_client_A: dict[str, pd.DataFrame],
    dict_df_comp_A: dict[str, pd.DataFrame],
    property_id_roomtype_mapping: pd.DataFrame,
    property_id_channel_cat: pd.DataFrame,
    property_id: int,
) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return prediction_data
