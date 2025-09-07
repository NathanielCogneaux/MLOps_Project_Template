import pandas as pd
import numpy as np

from utils.data_manip import df_merger
from utils.data_reader import load_processed_data_subfolder
from .basic import basic_feature_engineering, categorical_handler
from ..shared_features import (
    add_events_features,
    add_temp_features,
    channel_category_handler,
    unknown_channel_simulator,
    unknown_room_simulator,
)


def _type_B_processor_for_type_A(property_id: int) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return df_client_B


def feature_processing_train(
    dict_df_client_A: dict[str, pd.DataFrame],
    dict_df_comp_A: dict[str, pd.DataFrame],
    property_id: int,
) -> tuple[pd.DataFrame, pd.Series]:

    ### --- OMITTED --- ###

    return X, y
