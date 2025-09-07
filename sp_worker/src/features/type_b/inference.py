import pandas as pd
from itertools import product
import pytz

from config.settings import DEFAULT_TIMEZONE

from .basic import basic_feature_engineering, categorical_handler
from ..shared_features import (
    add_events_features,
    add_temp_features,
    unseen_rooms_pred_manager,
    unseen_channels_pred_manager,
    lead_time_changer,
)


tz = pytz.timezone(DEFAULT_TIMEZONE)


def _get_close_days_after_data(prediction_data, price_stats):

    ### --- OMITTED --- ###

    return prediction_data


def feature_processing_pred(
    dict_df_client_B: dict[str, pd.DataFrame],
    dict_df_comp_B: dict[str, pd.DataFrame],
    property_id_roomtype_mapping: pd.DataFrame,
    property_id_channel_cat: pd.DataFrame,
    property_id: int,
) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return prediction_data
