import pandas as pd

from .property_manager import get_properties
from .hotel_class import HotelProperty
from .data_processor import data_updater, data_processor

from utils.data_reader import load_all_raw_data, load_properties
from utils.data_saver import save_processed_data, save_properties


def raw_data_updater(scrap_type: str) -> None:
    # get all properties info
    properties: list[HotelProperty] = get_properties()
    # update all their data given the tables to fetch and scrap type
    data_updater(scrap_type, properties)

    save_properties(properties)


def data_cleaner(scrap_type: str) -> None:
    # load that data
    dict_df_otas_all_raw: dict[str, pd.DataFrame] = load_all_raw_data(scrap_type)
    properties: list[HotelProperty] = load_properties()
    # Process it
    dict_prop_id_client_comp: dict[
        int, tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]
    ] = data_processor(dict_df_otas_all_raw, properties)
    # save it
    save_processed_data(dict_prop_id_client_comp, scrap_type)
