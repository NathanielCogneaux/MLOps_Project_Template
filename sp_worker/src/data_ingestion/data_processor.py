import pandas as pd
import pytz
import logging

from .property_manager import HotelProperty
from .database_loader_1 import sync_incremental_data
from config.settings import DEFAULT_TIMEZONE, TABLES_TO_FETCH

local_tz = pytz.timezone(DEFAULT_TIMEZONE)

logger = logging.getLogger(__name__)


def data_updater(scrap_type: str, properties: list[HotelProperty]) -> None:
    id_set: set[int] = set()
    for property in properties:
        id_set.update(property.client_ids)
        id_set.update(property.comp_ids)

    id_list: list[int] = list(id_set)
    sync_incremental_data(
        tables_to_fetch=TABLES_TO_FETCH, id_list=id_list, scrap_type=scrap_type
    )


def _remove_outliers(
    dict_df: dict[str, pd.DataFrame],
    column: str,
    lower_quantile: float,
    upper_quantile: float,
) -> dict[str, pd.DataFrame]:
    for ota, df in dict_df.items():

        lower_bound: float = df[column].quantile(lower_quantile)
        upper_bound: float = df[column].quantile(upper_quantile)

        dict_df[ota] = df[(df[column] < upper_bound) & (df[column] > lower_bound)]

    return dict_df


def _date_columns_processor(
    dict_df: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:

    for table in dict_df.keys():
        dict_df[table]["scraping_id"] = pd.to_datetime(
            dict_df[table]["scraping_id"]
        ).dt.tz_convert(local_tz)
        dict_df[table]["checkIn"] = (
            pd.to_datetime(dict_df[table]["checkIn"])
            .dt.tz_convert(local_tz)
            .dt.normalize()
        )

    return dict_df


def _get_client_and_competitors(
    dict_df_otas: dict[str, pd.DataFrame], comp_ids: list[int], client_ids: list[int]
) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:

    dict_df_comp: dict[str, pd.DataFrame] = {}
    dict_df_client: dict[str, pd.DataFrame] = {}

    for ota, df in dict_df_otas.items():
        dict_df_comp[ota] = df[df["hotel_id"].isin(comp_ids)]
        dict_df_client[ota] = df[df["hotel_id"].isin(client_ids)]

    return dict_df_client, dict_df_comp


def _channel_rt_name_mapping(
    dict_df_client: dict[str, pd.DataFrame],
    df_rt_mapping: pd.DataFrame,
    property_id: int,
) -> dict[str, pd.DataFrame]:

    ### --- OMITTED --- ###

    return dict_df_client


def data_processor(
    dict_df_otas_all_ids_raw: dict[str, pd.DataFrame], property_ids: list[HotelProperty]
) -> dict[int, tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]]:

    dict_df_otas_all_ids_raw = _remove_outliers(
        dict_df=dict_df_otas_all_ids_raw,
        column="price_display",
        lower_quantile=0.001,
        upper_quantile=0.975,
    )

    dict_df_otas_all_ids_raw = _date_columns_processor(dict_df_otas_all_ids_raw)

    dict_prop_id_client_comp: dict[
        int, tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]
    ] = {}

    for property in property_ids:

        property_id: int = property.property_id
        client_ids: list[int] = property.client_ids
        comp_ids: list[int] = property.comp_ids
        df_rt_mapping: pd.DataFrame = property.df_rt_mapping
        is_using_IMS: bool = property.is_using_IMS

        dict_df_client, dict_df_comp = _get_client_and_competitors(
            dict_df_otas=dict_df_otas_all_ids_raw,
            comp_ids=comp_ids,
            client_ids=client_ids,
        )

        dict_df_client = _channel_rt_name_mapping(
            dict_df_client=dict_df_client,
            df_rt_mapping=df_rt_mapping,
            property_id=property_id,
        )

        for ota in dict_df_client:

            ### --- OMITTED --- ###

        dict_prop_id_client_comp[property_id] = (dict_df_client, dict_df_comp)

    return dict_prop_id_client_comp
