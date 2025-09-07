import os
from pathlib import Path

# Detect if running inside Airflow container
IS_AIRFLOW = os.getenv("AIRFLOW_HOME") is not None

if IS_AIRFLOW:
    BASE_DIR = Path("/opt/airflow/src")  # code source inside container
else:
    BASE_DIR = Path(__file__).resolve().parent.parent  # repo root locally

# Data path: contract via environment variable
# For Airflow, default to the shared volume; for local dev, default to ./data
if IS_AIRFLOW:
    DATA_PATH = Path(os.getenv("DATA_PATH", "/shared-data"))
else:
    DATA_PATH = Path(os.getenv("DATA_PATH", BASE_DIR.parent / "data"))

# Data directories
LAST_UPDATE_PATH = DATA_PATH / "last_updates"
OUTPUTS_PATH = DATA_PATH / "outputs"
RAW_DATA_PATH = DATA_PATH / "raw_data"
PROCESSED_DATA_PATH = DATA_PATH / "processed"
PROPERTIES_PATH = DATA_PATH / "properties"

# Extra data (kept in source tree, not in volume)
EXTRA_DATA_PATH = BASE_DIR / "utils" / "extra_data"
MANUAL_CHANNEL_ROOMTYPE_MAPPING_PATH = (
    EXTRA_DATA_PATH / "manual_channel_roomtype_mapping.feather"
)
MANUAL_PROPID_EVENT_AREA_MAPPING_PATH = (
    EXTRA_DATA_PATH / "manual_prop_id_event_area_mapping.feather"
)
MANUAL_CHANNEL_CATEGORY_PATH = EXTRA_DATA_PATH / "channel_categories.feather"

# ML paths
AI_PATH = BASE_DIR / "ml"
OPTIMIZED_BASELINE_FITTED_PARAMS_PATH = (
    AI_PATH / "optimized_baseline" / "fitted_params.json"
)

# MLflow tracking (always under DATA_PATH so it persists)
MFLOW_BASELINE_TRACKING_PATH = DATA_PATH / "mlruns"


def ensure_directories():
    """Ensure required directories exist."""
    directories = [
        DATA_PATH,
        LAST_UPDATE_PATH,
        OUTPUTS_PATH,
        RAW_DATA_PATH,
        PROCESSED_DATA_PATH,
        PROPERTIES_PATH,
        MFLOW_BASELINE_TRACKING_PATH,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Ensured directory exists: {directory}")


# Auto-create directories at import
ensure_directories()
