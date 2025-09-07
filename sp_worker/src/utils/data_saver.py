import os
import json
import pandas as pd
import pickle
import logging
import pytz

from config.paths import (
    RAW_DATA_PATH,
    LAST_UPDATE_PATH,
    PROCESSED_DATA_PATH,
    OUTPUTS_PATH,
    PROPERTIES_PATH,
)
from config.settings import DEFAULT_TIMEZONE
from .data_manip import cleanup_old_files
from data_ingestion.hotel_class import HotelProperty

tz = pytz.timezone(DEFAULT_TIMEZONE)

logger = logging.getLogger(__name__)

# ----------------------------------- save updates -----------------------------------


def save_latest_updates_raw_data(
    latest_updates: dict[str, dict[str, pd.Timestamp]], scrap_type: str
):
    path = LAST_UPDATE_PATH / "raw_data" / scrap_type / "latest_updates.json"
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "w") as f:
        json.dump(
            {
                ota: {str(hid): ts.isoformat() for hid, ts in hotel_dict.items()}
                for ota, hotel_dict in latest_updates.items()
            },
            f,
            indent=4,
        )


def save_latest_updates_processed(property_ids: list[int], scrap_type: str) -> None:

    path = LAST_UPDATE_PATH / "processed_data" / scrap_type / "latest_updates.json"
    os.makedirs(path.parent, exist_ok=True)

    now = pd.Timestamp.now(tz=DEFAULT_TIMEZONE).isoformat()

    if path.exists():
        with open(path, "r") as f:
            try:
                existing_updates = json.load(f)
            except json.JSONDecodeError:
                existing_updates = {}
    else:
        existing_updates = {}

    for pid in property_ids:
        existing_updates[str(pid)] = now

    with open(path, "w") as f:
        json.dump(existing_updates, f, indent=4)


# ----------------------------------- save data in feater -----------------------------------


def write_raw_data_to_feather(
    name: str, df: pd.DataFrame, scrap_type: str, full_reload: bool
):
    path = RAW_DATA_PATH / scrap_type
    os.makedirs(path, exist_ok=True)
    filepath = path / f"{name}.feather"

    if full_reload == True or not os.path.exists(filepath):
        df.reset_index(drop=True).to_feather(filepath)
    else:
        existing = pd.read_feather(filepath)
        combined = pd.concat([existing, df], ignore_index=True)
        combined.reset_index(drop=True).to_feather(filepath)


def save_processed_data(
    dict_prop_id_client_comp: dict[
        int, tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]
    ],
    scrap_type: str,
) -> None:

    for property_id, (dict_df_client, dict_df_comp) in dict_prop_id_client_comp.items():
        base_path = PROCESSED_DATA_PATH / f"property_id_{property_id}" / scrap_type
        try:
            base_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Failed to create base directory: {base_path}\n{e}")

        def save_dataframes(
            dict_df: dict[str, pd.DataFrame], subfolder_name: str
        ) -> None:
            sub_path = base_path / subfolder_name
            try:
                sub_path.mkdir(exist_ok=True)
            except Exception as e:
                raise RuntimeError(f"Failed to create subdirectory: {sub_path}\n{e}")

            for ota, df in dict_df.items():
                file_path = sub_path / f"{ota}.feather"
                try:
                    df.to_feather(file_path)
                except Exception as e:
                    logger.error(
                        f"Failed to save {ota}.feather in '{subfolder_name}' for property_id={property_id}: {e}"
                    )

        save_dataframes(dict_df_client, "client_data")
        save_dataframes(dict_df_comp, "comp_data")

    save_latest_updates_processed(list(dict_prop_id_client_comp.keys()), scrap_type)


# ----------------------------------- save outputs in feather -----------------------------------


def get_timestamp_filename() -> str:
    return pd.Timestamp.now(tz=tz).strftime("%Y-%m-%d_%H-%M-%S") + ".feather"


def save_comp_prices(
    dict_df_prices: dict[str, pd.DataFrame], property_id: int, scrap_type: str
) -> None:
    base_folder = (
        OUTPUTS_PATH / "comp_prices" / f"property_id_{property_id}" / scrap_type
    )
    filename = get_timestamp_filename()

    for ota, df in dict_df_prices.items():
        folder = base_folder / ota
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory '{folder}': {e}")
            continue

        path = folder / filename
        try:
            df.to_feather(path)
            cleanup_old_files(folder)
        except Exception as e:
            logger.error(f"Failed to save comp_prices for OTA '{ota}' at '{path}': {e}")


def save_market_stats(
    dict_price_stats: dict[str, pd.DataFrame], property_id: int
) -> None:
    base_folder = OUTPUTS_PATH / "market_stats" / f"property_id_{property_id}"
    filename = get_timestamp_filename()

    for ota, df in dict_price_stats.items():
        folder = base_folder / ota
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory '{folder}': {e}")
            continue

        path = folder / filename
        try:
            df.to_feather(path)
            cleanup_old_files(folder)
        except Exception as e:
            logger.error(
                f"Failed to save market_stats for OTA '{ota}' at '{path}': {e}"
            )


def save_events_data(df_event_importance: pd.DataFrame, property_id: int) -> None:
    folder = OUTPUTS_PATH / "events" / f"property_id_{property_id}"
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create directory '{folder}': {e}")
        return

    path = folder / get_timestamp_filename()
    try:
        df_event_importance.to_feather(path)
        cleanup_old_files(folder)
    except Exception as e:
        logger.error(f"Failed to save events data at '{path}': {e}")


def save_ai_prices(
    df_pred: pd.DataFrame, model: str, property_id: int, scrap_type: str
) -> None:
    # NOTE: model = baseline | optimized_baseline

    folder = (
        OUTPUTS_PATH / "ai_prices" / model / f"property_id_{property_id}" / scrap_type
    )
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create directory '{folder}': {e}")
        return

    path = folder / get_timestamp_filename()
    try:
        df_pred.to_feather(path)
        cleanup_old_files(folder)
    except Exception as e:
        logger.error(f"Failed to save AI prices at '{path}': {e}")


# ----------------------------------- save properties in pickle -----------------------------------


def save_properties(
    properties: list[HotelProperty],
) -> None:
    folder = PROPERTIES_PATH
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create directory '{folder}': {e}")
        return

    path = folder / "properties.pkl"
    try:
        with open(path, "wb") as f:
            pickle.dump(properties, f, protocol=pickle.HIGHEST_PROTOCOL)

    except Exception as e:
        logger.error(f"Failed to save HotelProperty objects at '{path}': {e}")
