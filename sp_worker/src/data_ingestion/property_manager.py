import pandas as pd

from .database_loader_1 import get_mapping_id
from .database_loader_2 import fetch_ims_mapping_roomtype
from .hotel_class import HotelProperty
from config.paths import MANUAL_CHANNEL_ROOMTYPE_MAPPING_PATH


def _concat_with_manual_mapping(df_rt_mappings: pd.DataFrame) -> pd.DataFrame:

    ### --- OMITTED --- ###

    return df_combined


def get_properties() -> list[HotelProperty]:

    ### --- OMITTED --- ###

    return properties
