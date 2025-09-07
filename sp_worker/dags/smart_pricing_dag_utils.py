from pytz import timezone
from datetime import datetime, timedelta

from src.config.custom_logging import setup_logging

setup_logging()

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "start_date": datetime(2025, 8, 18, tzinfo=timezone("Asia/Seoul")),
    "retry_delay": timedelta(minutes=5),
}
