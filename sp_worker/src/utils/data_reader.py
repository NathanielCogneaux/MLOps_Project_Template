import os
import json
import pickle
import pandas as pd
from typing import Optional
import logging

from config.paths import (
    RAW_DATA_PATH,
    LAST_UPDATE_PATH,
    PROCESSED_DATA_PATH,
    OUTPUTS_PATH,
    PROPERTIES_PATH,
)
from config.settings import DEFAULT_TIMEZONE, TABLES_TO_FETCH
from .data_manip import find_best_matching_file
from data_ingestion.hotel_class import HotelProperty

logger = logging.getLogger(__name__)


# ----------------------------------- read updates -----------------------------------


def load_latest_updates_raw_data(scrap_type: str) -> dict[str, dict[str, pd.Timestamp]]:
    path = LAST_UPDATE_PATH / "raw_data" / scrap_type / "latest_updates.json"
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        raw = json.load(f)
    today = pd.Timestamp.now(tz=DEFAULT_TIMEZONE).normalize()
    yesterday = today - pd.Timedelta(days=1)

    parsed: dict[str, dict[str, pd.Timestamp]] = {}

    for ota, hotel_dict in raw.items():
        parsed[ota] = {}
        for hotel_id, ts_str in hotel_dict.items():
            ts = pd.Timestamp(ts_str)
            ts = (
                ts.tz_convert(DEFAULT_TIMEZONE)
                if ts.tzinfo
                else ts.tz_localize(DEFAULT_TIMEZONE)
            )
            parsed[ota][hotel_id] = ts

            if ts < yesterday:
                logger.warning(
                    f"OTA '{ota}' - Hotel ID {hotel_id} has not been updated since {ts.isoformat()}"
                )
    return parsed


def load_latest_updates_processed(scrap_type: str) -> dict[int, pd.Timestamp]:
    path = LAST_UPDATE_PATH / "processed_data" / scrap_type / "latest_updates.json"
    if not path.exists():
        return {}
    try:
        with open(path, "r") as f:
            raw_dict = json.load(f)
        today = pd.Timestamp.now(tz=DEFAULT_TIMEZONE).normalize()
        yesterday = today - pd.Timedelta(days=1)
        parsed_updates: dict[int, pd.Timestamp] = {}
        for pid_str, ts_str in raw_dict.items():
            pid = int(pid_str)
            ts = pd.Timestamp(ts_str)
            ts = (
                ts.tz_convert(DEFAULT_TIMEZONE)
                if ts.tzinfo
                else ts.tz_localize(DEFAULT_TIMEZONE)
            )
            parsed_updates[pid] = ts
            if ts < yesterday:
                logger.warning(
                    f"Property {pid} has not been updated since {ts.isoformat()}"
                )
        return parsed_updates
    except Exception as e:
        raise RuntimeError(f"Failed to read or parse: {path}\n{e}")


# ----------------------------------- read data in feather -----------------------------------


def load_raw_data(name: str, scrap_type: str) -> Optional[pd.DataFrame]:
    path = RAW_DATA_PATH / scrap_type / f"{name}.feather"
    if os.path.exists(path):
        return pd.read_feather(path)
    logger.warning(
        f"No raw data found for {name} in scrap type {scrap_type}. Skipping it."
    )
    return None


def load_all_raw_data(scrap_type: str) -> dict[str, pd.DataFrame]:
    dict_df_otas_all_raw: dict[str, pd.DataFrame] = {}
    for table in TABLES_TO_FETCH:
        name = table

        ### --- OMITTED --- ###

        df_ota_raw: Optional[pd.DataFrame] = load_raw_data(name, scrap_type)
        if df_ota_raw is None:
            continue
        dict_df_otas_all_raw[name] = df_ota_raw

    if not dict_df_otas_all_raw:
        from src.data_ingestion.ingestion_pipeline import raw_data_updater

        logger.warning("No raw data found. Running fallback with raw_data_updater...")
        raw_data_updater(scrap_type)

        for table in TABLES_TO_FETCH:
            name = table

            ### --- OMITTED --- ###

            df_ota_raw: Optional[pd.DataFrame] = load_raw_data(name, scrap_type)
            if df_ota_raw is None:
                continue
            dict_df_otas_all_raw[name] = df_ota_raw

        if not dict_df_otas_all_raw:
            raise RuntimeError(
                f"[FATAL] No raw data could be loaded for scrap_type '{scrap_type}' "
                f"even after fallback recovery with raw_data_updater()."
            )

    return dict_df_otas_all_raw


def load_processed_data_subfolder(
    property_id: int, scrap_type: str, subfolder: str
) -> dict[str, pd.DataFrame]:
    folder_path = (
        PROCESSED_DATA_PATH / f"property_id_{property_id}" / scrap_type / subfolder
    )
    dict_df = {}

    def try_load() -> dict[str, pd.DataFrame]:
        # Attempt to load all feather files in the folder.
        data = {}
        if not folder_path.exists():
            return data

        for file in folder_path.glob("*.feather"):
            ota = file.stem
            try:
                data[ota] = pd.read_feather(file)
            except Exception as e:
                logger.error(f"Could not load {file.name} from {subfolder}: {e}")
        return data

    dict_df = try_load()
    if dict_df:
        return dict_df

    logger.warning(f"No processed data found at {folder_path}. Running fallback...")
    from src.data_ingestion.ingestion_pipeline import raw_data_updater, data_cleaner

    logger.warning("Running raw_data_updater as first fallback...")
    raw_data_updater(scrap_type)
    logger.warning("Running data_cleaner as second fallback...")
    data_cleaner(scrap_type)

    dict_df = try_load()
    if not dict_df:
        raise RuntimeError(
            f"[FATAL] Failed to load processed data for property_id={property_id}, "
            f"scrap_type='{scrap_type}', subfolder='{subfolder}' even after fallback."
        )
    return dict_df


# ----------------------------------- read outputs in feather -----------------------------------


def load_comp_prices(
    date: pd.Timestamp, property_id: int, scrap_type: str
) -> Optional[dict[str, pd.DataFrame]]:
    base_folder = (
        OUTPUTS_PATH / "comp_prices" / f"property_id_{property_id}" / scrap_type
    )
    if not base_folder.exists():
        logger.warning(f"comp_prices folder does not exist: {base_folder}")
        return None

    result: dict[str, pd.DataFrame] = {}

    for ota_folder in base_folder.iterdir():
        if not ota_folder.is_dir():
            continue

        ota_name = ota_folder.name
        best_file = find_best_matching_file(ota_folder, date, scrap_type)

        if best_file is not None:
            try:
                df = pd.read_feather(best_file)
                result[ota_name] = df
            except Exception as e:
                logger.error(
                    f"Failed to read comp_prices for OTA '{ota_name}' from {best_file}: {e}"
                )
        else:
            logger.warning(
                f"No matching file found for OTA '{ota_name}' at {date.strftime('%Y-%m-%d %H:%M:%S')}"
            )

    return result if result else None


def load_market_stats(
    date: pd.Timestamp, property_id: int
) -> Optional[dict[str, pd.DataFrame]]:
    base_folder = OUTPUTS_PATH / "market_stats" / f"property_id_{property_id}"
    if not base_folder.exists():
        logger.warning(f"market_stats folder does not exist: {base_folder}")
        return None

    result = {}
    for ota_folder in base_folder.iterdir():
        if not ota_folder.is_dir():
            continue
        best_file = find_best_matching_file(ota_folder, date, scrap_type="B")
        if best_file:
            try:
                result[ota_folder.name] = pd.read_feather(best_file)
            except Exception as e:
                logger.error(
                    f"Failed to read market_stats for OTA '{ota_folder.name}' from {best_file}: {e}"
                )

    return result if result else None


def load_events_data(date: pd.Timestamp, property_id: int) -> Optional[pd.DataFrame]:
    folder = OUTPUTS_PATH / "events" / f"property_id_{property_id}"
    if not folder.exists():
        logger.warning(f"events folder does not exist: {folder}")
        return None

    best_file = find_best_matching_file(folder, date, scrap_type="B")
    if best_file:
        try:
            return pd.read_feather(best_file)
        except Exception as e:
            logger.error(f"Failed to read events data from {best_file}: {e}")
    else:
        logger.warning(f"No matching events file found for {date}")
    return None


def load_ai_prices(
    date: pd.Timestamp, model: str, property_id: int, scrap_type: str
) -> Optional[pd.DataFrame]:
    # NOTE: model = baseline | optimized_baseline
    base_folder = (
        OUTPUTS_PATH / "ai_prices" / model / f"property_id_{property_id}" / scrap_type
    )
    if not base_folder.exists():
        logger.warning(f"AI prices folder does not exist: {base_folder}")
        if model == "optimized_baseline":
            logger.warning(
                f"Perhaps you're trying to get optimized baseline predictions for a property ({property_id}) not actively using the IMS."
            )
        return None

    best_file = find_best_matching_file(base_folder, date, scrap_type)
    if best_file is None:
        logger.warning(f"No matching AI prices file found for {date} in {base_folder}")
        return None

    try:
        df_pred = pd.read_feather(best_file)
        return df_pred
    except Exception as e:
        logger.error(f"Failed to read AI prices from {best_file}: {e}")
        return None


# ----------------------------------- read properties in pickle -----------------------------------


def load_properties() -> list[HotelProperty]:
    path = PROPERTIES_PATH / "properties.pkl"
    if not path.exists():
        logger.error(f"Properties pickle file does not exist: {path}")
        raise FileNotFoundError(f"Properties pickle file does not exist: {path}")
    try:
        with open(path, "rb") as f:
            properties: list[HotelProperty] = pickle.load(f)
        return properties
    except Exception as e:
        logger.error(f"Failed to load HotelProperty objects from '{path}': {e}")
        raise RuntimeError(
            f"Failed to load HotelProperty objects from '{path}': {e}"
        ) from e


# ------------------------------------------ helper -----------------------------------------------


def file_search_timestamp(ts: pd.Timestamp, scrap_type: str) -> pd.Timestamp:
    ts = (
        ts.tz_convert(DEFAULT_TIMEZONE)
        if ts.tzinfo
        else ts.tz_localize(DEFAULT_TIMEZONE)
    )
    return ts.normalize() if scrap_type == "B" else ts.floor("h")
