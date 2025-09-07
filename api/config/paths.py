import os
from pathlib import Path

IS_API_CONTAINER = os.getenv("DATA_PATH") is not None

if IS_API_CONTAINER:
    DATA_PATH = Path(os.getenv("DATA_PATH", "/app/data"))
else:
    DATA_PATH = Path(__file__).resolve().parent.parent.parent / "sp_worker" / "data"

# Data directories
LAST_UPDATE_PATH = DATA_PATH / "last_updates"
OUTPUTS_PATH = DATA_PATH / "outputs"
PROPERTIES_PATH = DATA_PATH / "properties"
