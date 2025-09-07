import os
import pandas as pd
from typing import Any
import logging
from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from concurrent.futures import ThreadPoolExecutor, as_completed

from config.paths import RAW_DATA_PATH
from config.settings import DEFAULT_TIMEZONE
from utils.data_reader import load_latest_updates_raw_data
from utils.data_saver import save_latest_updates_raw_data, write_raw_data_to_feather

logger = logging.getLogger(__name__)

load_dotenv()


def _connect_ai_db() -> Engine:
    prefix = "OMMITED_1"
    POSTGRES_USER = os.getenv(f"{prefix}_POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv(f"{prefix}_POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv(f"{prefix}_POSTGRES_HOST")
    POSTGRES_PORT = os.getenv(f"{prefix}_POSTGRES_PORT")
    POSTGRES_DATABASE = os.getenv(f"{prefix}_POSTGRES_DATABASE")
    DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
    return create_engine(DATABASE_URL, pool_size=50, max_overflow=50, echo=False)


# ----------------------------------------------------------------------------------------------------------


def _fetch_incremental_updates_parallel(
    engine: Engine,
    tables_to_fetch: list[str],
    id_list: list[int],
    scrap_type: str,
    last_updates: dict[str, dict[str, pd.Timestamp]],
    max_workers: int = 4,
) -> dict[str, pd.DataFrame]:

    def query_table(table: str) -> tuple[str, pd.DataFrame]:

        ### --- OMITTED --- ###

        query = text(
            f"""
            SELECT {columns}
            FROM {table}
            WHERE {where_clause}
        """
        )

        try:
            with engine.connect() as conn:

                result = conn.execute(query, params)

                ### --- OMITTED --- ###

                logger.info("OMITTED")
                return key, df

        except Exception as e:
            logger.error(f"Error fetching {key}: {e}")
            return key, pd.DataFrame()

    updates: dict[str, pd.DataFrame] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(query_table, table): table for table in tables_to_fetch
        }
        for future in as_completed(futures):
            key, df = future.result()
            updates[key] = df

    return updates


def sync_incremental_data(
    tables_to_fetch: list[str], id_list: list[int], scrap_type: str
) -> None:
    engine = _connect_ai_db()

    last_updates: dict[str, dict[str, pd.Timestamp]] = load_latest_updates_raw_data(
        scrap_type
    )

    try:
        full_reload: dict[str, bool] = {}
        for table in tables_to_fetch:
            feather_path = RAW_DATA_PATH / scrap_type / f"{table}.feather"
            feather_exists = feather_path.exists()
            has_updates = table in last_updates and last_updates[table]

            full_reload[table] = True  # Assume full reload by default
            if not feather_exists and has_updates:
                logger.warning(
                    f"No data file for {table} but found log of updates → fallback to full reload for {table}."
                )
                last_updates.pop(table, None)

            elif feather_exists and not has_updates:
                logger.warning(
                    f"Data file exists for {table} but no log of updates → fallback to full reload for {table}."
                )
                feather_path.unlink()

            else:
                full_reload[table] = False

        new_data = _fetch_incremental_updates_parallel(
            engine, tables_to_fetch, id_list, scrap_type, last_updates
        )
        latest_updates: dict[str, dict[str, pd.Timestamp]] = {}

        for table, df in new_data.items():
            latest_updates[table] = last_updates.get(table, {})
            if not df.empty:
                for hid, group in df.groupby("hotel_id"):
                    latest_updates[table][str(hid)] = pd.to_datetime(
                        group["updated"].max()
                    )
                df = df.drop(columns=["updated"])
                write_raw_data_to_feather(
                    table, df, scrap_type=scrap_type, full_reload=full_reload[table]
                )

        save_latest_updates_raw_data(latest_updates, scrap_type=scrap_type)

    finally:
        engine.dispose()


# ----------------------------------------------------------------------------------------------------------


# # NOTE: the corresponding table has to be updated when new clients are registered
def get_mapping_id() -> pd.DataFrame:
    engine = _connect_ai_db()

    query = text(
        """
        OMMITTED
    """
    )

    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df
    except Exception as e:
        logger.error(f"Error fetching data from property_hotel_mapping: {e}")
        return pd.DataFrame()
    finally:
        engine.dispose()
