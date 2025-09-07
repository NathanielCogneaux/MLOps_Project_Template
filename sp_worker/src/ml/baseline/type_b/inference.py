import pandas as pd
import numpy as np

### --- OMITTED --- ###

from features.type_b.inference import feature_processing_pred


def _extrapolate_predictions(
    prediction_data: pd.DataFrame, missing_mask: pd.Series, window: int = 20
) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return df


def baseline_model_B_predict(
    model: ### --- OMITTED --- ###,
    dict_df_client_B: dict[str, pd.DataFrame],
    dict_df_comp_B: dict[str, pd.DataFrame],
    property_id_roomtype_mapping: pd.DataFrame,
    property_id_channel_cat: pd.DataFrame,
    property_id: int,
    extrapolate: bool = False,
    window: int = 20,
) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return prediction_data
