import pandas as pd
import logging

from utils.data_reader import (
    load_latest_updates_processed,
    load_processed_data_subfolder,
)
from utils.data_saver import save_comp_prices, save_market_stats, save_events_data
from .sub_charts import get_comp_price_data, get_market_trend_chart, get_events_data
from .ext_event_and_holidays import merge_event_importance_with_calendar_events

from config.paths import MANUAL_PROPID_EVENT_AREA_MAPPING_PATH


logger = logging.getLogger(__name__)


def sub_charts_updater(scrap_type: str):

    latest_updates: dict[int, pd.Timestamp] = load_latest_updates_processed(
        scrap_type=scrap_type
    )
    property_ids: list[int] = list(latest_updates.keys())

    for property_id in property_ids:

        dict_df_comp: dict[str, pd.DataFrame] = load_processed_data_subfolder(
            property_id, scrap_type, "comp_data"
        )

        # Generate and competitor prices stats
        dict_df_prices: dict[str, pd.DataFrame] = get_comp_price_data(
            dict_df_comp, scrap_type
        )
        save_comp_prices(dict_df_prices, property_id, scrap_type)

        if scrap_type == "B":
            # Generate and save market stats
            dict_price_stats: dict[str, pd.DataFrame] = get_market_trend_chart(
                dict_df_comp
            )
            save_market_stats(dict_price_stats, property_id)

            # Generate and save events data
            df_event_importance: pd.DataFrame = get_events_data(dict_df_comp)

            df_prop_id_event_area_mapping = pd.read_feather(
                MANUAL_PROPID_EVENT_AREA_MAPPING_PATH
            )
            area_name: str = df_prop_id_event_area_mapping[
                df_prop_id_event_area_mapping["property_id"] == property_id
            ]["event_area"].iloc[0]

            df_event_importance_with_name: pd.DataFrame = (
                merge_event_importance_with_calendar_events(
                    df_event_importance, area_name
                )
            )

            save_events_data(df_event_importance_with_name, property_id)


### EXAMPLE OF AIRFLOW TASKS ###

# from airflow.decorators import task
# import pandas as pd
# from utils.data_reader import load_processed_data_subfolder, load_latest_updates_processed
# from utils.data_saver import save_comp_prices, save_market_stats, save_events_data
# from src.data_analytics.sub_charts import get_comp_price_data, get_market_trend_chart, get_events_data
# from src.data_analytics.ext_event_and_holidays import merge_event_importance_with_calendar_events
# from config.paths import MANUAL_PROPID_EVENT_AREA_MAPPING_PATH

# @task
# def update_comp_price(property_id: int, scrap_type: str):
#     dict_df_comp = load_processed_data_subfolder(property_id, scrap_type, "comp_data")
#     dict_df_prices = get_comp_price_data(dict_df_comp, scrap_type)
#     save_comp_prices(dict_df_prices, property_id, scrap_type)

# @task
# def update_market_stats(property_id: int):
#     dict_df_comp = load_processed_data_subfolder(property_id, "B", "comp_data")
#     dict_price_stats = get_market_trend_chart(dict_df_comp)
#     save_market_stats(dict_price_stats, property_id)

# @task
# def update_events_data(property_id: int):
#     dict_df_comp = load_processed_data_subfolder(property_id, "B", "comp_data")
#     df_event_importance = get_events_data(dict_df_comp)
#     df_prop_id_event_area_mapping = pd.read_feather(MANUAL_PROPID_EVENT_AREA_MAPPING_PATH)
#     area_name = df_prop_id_event_area_mapping[df_prop_id_event_area_mapping["property_id"] == property_id]["event_area"].iloc[0]
#     df_event_importance_with_name = merge_event_importance_with_calendar_events(df_event_importance, area_name)
#     save_events_data(df_event_importance_with_name, property_id)

# @task
# def get_property_ids(scrap_type: str):
#     latest_updates = load_latest_updates_processed(scrap_type)
#     return list(latest_updates.keys())
