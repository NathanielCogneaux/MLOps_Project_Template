import os
import logging
from dotenv import load_dotenv
import pandas as pd

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

load_dotenv()


def _connect_ims_db() -> Engine:
    prefix = "OMITTED_2"
    POSTGRES_USER = os.getenv(f"{prefix}_POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv(f"{prefix}_POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv(f"{prefix}_POSTGRES_HOST")
    POSTGRES_PORT = os.getenv(f"{prefix}_POSTGRES_PORT")
    POSTGRES_DATABASE = os.getenv(f"{prefix}_POSTGRES_DATABASE")

    DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
    return create_engine(DATABASE_URL, pool_size=10, max_overflow=20, echo=False)


# ----------------------------------------------------------------------------------------------------------


def fetch_ims_mapping_roomtype(property_ids: list[int]) -> pd.DataFrame:
    engine = _connect_ims_db()

    query = text(
        """
        OMITTED
    """
    )

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"property_ids": property_ids})
            df_all = pd.DataFrame(result.fetchall(), columns=result.keys())

            ### --- OMITTED --- ###

            return df_all.reset_index(drop=True)

    except Exception as e:
        logger.error(
            f"Error fetching room type mapping for property_ids {property_ids}: {e}"
        )
        return pd.DataFrame()

    finally:
        try:
            engine.dispose()
        except Exception as e:
            logger.warning(f"Error disposing OMITTED_2 DB engine: {e}")


# ----------------------------------------------------------------------------------------------------------


def get_ims_occ(property_id: int, scrap_type: str) -> pd.DataFrame:
    engine = _connect_ims_db()
    today = pd.Timestamp.now().normalize()

    ### --- OMITTED --- ###

    query = text(
        """
        OMITTED
    """
    )

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"property_id": property_id, "dates": dates})
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df

    except Exception as e:
        logger.error(
            f"Failed to fetch occupancy data for property_id {property_id} and scrap_type '{scrap_type}': {e}"
        )
        return pd.DataFrame()

    finally:
        try:
            engine.dispose()
        except Exception as e:
            logger.warning(f"Error disposing IMS DB engine: {e}")


# ----------------------------------------------------------------------------------------------------------


def fetch_all_existing_roomtypes(property_ids: list[int]) -> pd.DataFrame:

    if not property_ids:
        return pd.DataFrame(columns=["room_name", "property_id", "category_id"])

    engine = _connect_ims_db()

    query = text(
        f"""
        OMITTED
    """
    )

    try:
        with engine.connect() as conn:
            result = conn.execute(query, params)
            df_all = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df_all

    except Exception as e:
        logger.error(f"Failed to fetch room types for property_ids {property_ids}: {e}")
        return pd.DataFrame()

    finally:
        try:
            engine.dispose()
        except Exception as e:
            logger.warning(f"Error disposing IMS DB engine: {e}")


# ----------------------------------------------------------------------------------------------------------


def fetch_all_used_channels() -> pd.DataFrame:

    engine = _connect_ims_db()

    query = text(
        """
        OMITTED
    """
    )

    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            df_all = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df_all

    except Exception as e:
        logger.error(f"Failed to fetch channels from channel: {e}")
        return pd.DataFrame()

    finally:
        try:
            engine.dispose()  # Remove this if using pooled engine
        except Exception as e:
            logger.warning(f"Error disposing IMS DB engine: {e}")
