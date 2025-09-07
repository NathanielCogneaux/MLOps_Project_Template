import pandas as pd
import numpy as np

from utils.data_manip import df_merger
from ..shared_features import lead_time_changer, CATEGORICAL_COLS_B


def client_processor(dict_df_client_B: dict[str, pd.DataFrame]) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return df_client


def comp_processor(dict_df_comp_B: dict[str, pd.DataFrame]) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return df_comp


def basic_feature_engineering(
    dict_df_client_B: dict[str, pd.DataFrame],
    dict_df_comp_B: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:

    ### --- OMITTED --- ###

    return df_client, price_stats


def categorical_handler(X: pd.DataFrame) -> pd.DataFrame:
    for col in CATEGORICAL_COLS_B:
        X[col] = X[col].astype("category")
    return X
