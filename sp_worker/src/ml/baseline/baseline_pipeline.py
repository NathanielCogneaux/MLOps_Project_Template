import pandas as pd
import logging

from sp_worker.src.data_ingestion.database_loader_2 import (
    fetch_all_existing_roomtypes,
    fetch_all_used_channels,
)
from data_ingestion.hotel_class import HotelProperty

from .type_b import baseline_model_B_train, baseline_model_B_predict
from .type_a import baseline_model_A_train, baseline_model_A_predict

from utils.data_reader import load_processed_data_subfolder, load_properties
from utils.data_saver import save_ai_prices
from config.paths import (
    MANUAL_CHANNEL_CATEGORY_PATH,
    MANUAL_CHANNEL_ROOMTYPE_MAPPING_PATH,
)

logger = logging.getLogger(__name__)


def ims_channel_room_types_processor(
    property_ids: list[int],
) -> tuple[pd.DataFrame, pd.DataFrame]:

    ### --- OMITTED --- ###

    return df_roomtype_mapping, ims_channels_cat_prop_id


def get_prop_id_ims_channel_room_types(
    df_roomtype_mapping: pd.DataFrame,
    ims_channels_cat_prop_id: pd.DataFrame,
    property_id: int,
    is_using_IMS: bool,
) -> tuple[pd.DataFrame, pd.DataFrame]:

    ### --- OMITTED --- ###

    return prop_id_roomtype_mapping, property_id_channel_cat


def baseline_model_updater(scrap_type: str) -> None:

    properties: list[HotelProperty] = load_properties()
    property_ids = [p.property_id for p in properties]

    df_roomtype_mapping, ims_channels_cat_prop_id = ims_channel_room_types_processor(
        property_ids
    )

    for property in properties:
        property_id = property.property_id
        is_using_IMS = property.is_using_IMS

        dict_df_client: dict[str, pd.DataFrame] = load_processed_data_subfolder(
            property_id=property_id, scrap_type=scrap_type, subfolder="client_data"
        )
        dict_df_comp: dict[str, pd.DataFrame] = load_processed_data_subfolder(
            property_id=property_id, scrap_type=scrap_type, subfolder="comp_data"
        )

        prop_id_roomtype_mapping, property_id_channel_cat = (
            get_prop_id_ims_channel_room_types(
                df_roomtype_mapping, ims_channels_cat_prop_id, property_id, is_using_IMS
            )
        )

        if scrap_type == "B":
            model = baseline_model_B_train(dict_df_client, dict_df_comp, property_id)
            df_pred: pd.DataFrame = baseline_model_B_predict(
                model,
                dict_df_client,
                dict_df_comp,
                prop_id_roomtype_mapping,
                property_id_channel_cat,
                property_id,
                extrapolate=True,
            )
        else:
            model = baseline_model_A_train(dict_df_client, dict_df_comp, property_id)
            df_pred: pd.DataFrame = baseline_model_A_predict(
                model,
                dict_df_client,
                dict_df_comp,
                prop_id_roomtype_mapping,
                property_id_channel_cat,
                property_id,
            )

        # SAVE THE DATA
        save_ai_prices(
            df_pred=df_pred,
            model="baseline",
            property_id=property_id,
            scrap_type=scrap_type,
        )
