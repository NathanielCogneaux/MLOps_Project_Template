import pandas as pd
import numpy as np
import logging

from config.paths import MANUAL_CHANNEL_CATEGORY_PATH

logger = logging.getLogger(__name__)


def channel_category_handler(df_client: pd.DataFrame, property_id: int) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return df_client


def unknown_room_simulator(df: pd.DataFrame) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return df


def unknown_channel_simulator(df: pd.DataFrame) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return df


def unseen_rooms_pred_manager(
    df_client: pd.DataFrame, prediction_data: pd.DataFrame
) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return prediction_data


def unseen_channels_pred_manager(
    df_client: pd.DataFrame, prediction_data: pd.DataFrame
) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return prediction_data
