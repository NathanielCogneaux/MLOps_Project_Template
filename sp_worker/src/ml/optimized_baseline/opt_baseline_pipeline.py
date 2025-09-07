import pandas as pd
import numpy as np
import json
import pytz
import logging
from typing import Optional

from config.paths import OPTIMIZED_BASELINE_FITTED_PARAMS_PATH
from config.settings import DEFAULT_TIMEZONE
from data_ingestion.hotel_class import HotelProperty
from sp_worker.src.data_ingestion.database_loader_2 import get_ims_occ
from utils.data_reader import load_ai_prices, file_search_timestamp, load_properties
from utils.data_saver import save_ai_prices

logger = logging.getLogger(__name__)

tz = pytz.timezone(DEFAULT_TIMEZONE)


with open(OPTIMIZED_BASELINE_FITTED_PARAMS_PATH, "r") as f:
    loaded_params = json.load(f)
    
    ### --- OMITTED --- ###


def price_inverse_logistic_fitted(occ, P0, k, v=0.25, L=1.02):

    ### --- OMITTED --- ###

    return 0


def apply_price_adjustment(row, add_discount: bool):

    ### --- OMITTED --- ###

    return row


def get_baseline_predictions(
    date: pd.Timestamp, property_id: int, scrap_type: str
) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return df_baseline_pred


def opt_baseline_model_updater(scrap_type: str, add_discount: bool = False) -> None:

    ### --- OMITTED --- ###
