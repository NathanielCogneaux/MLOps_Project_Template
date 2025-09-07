import pandas as pd

from .basic import basic_feature_engineering, categorical_handler
from ..shared_features import (
    add_events_features,
    add_temp_features,
    channel_category_handler,
    unknown_channel_simulator,
    unknown_room_simulator,
)


def feature_processing_train(
    dict_df_client_B: dict[str, pd.DataFrame],
    dict_df_comp_B: dict[str, pd.DataFrame],
    property_id: int,
) -> tuple[pd.DataFrame, pd.Series]:

    ### --- OMITTED --- ###

    return X, y
