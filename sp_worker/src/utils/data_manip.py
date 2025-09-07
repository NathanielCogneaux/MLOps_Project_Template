import os
from pathlib import Path
import pandas as pd
import logging
import pytz

from config.settings import DEFAULT_TIMEZONE

logger = logging.getLogger(__name__)


def df_merger(
    dict_df: dict[str, pd.DataFrame], columns_to_keep: list[str]
) -> pd.DataFrame:
    dict_copy = {}
    for table in dict_df.keys():
        df_copy = dict_df[table].copy()
        dict_copy[table] = df_copy[columns_to_keep]
    return pd.concat(dict_copy.values(), ignore_index=True)


def find_best_matching_file(
    folder: Path, target: pd.Timestamp, scrap_type: str
) -> Path | None:
    tz = pytz.timezone(DEFAULT_TIMEZONE)
    target = target.astimezone(tz)

    candidates = []
    for file in folder.glob("*.feather"):
        try:
            timestamp_str = file.stem.replace("_", " ")
            file_ts = pd.to_datetime(
                timestamp_str, format="%Y-%m-%d %H-%M-%S"
            ).tz_localize(tz)
            candidates.append((file_ts, file))
        except Exception:
            continue

    if not candidates:
        logger.warning(f"No feather files found in folder: {folder}")
        return None

    if scrap_type == "A":
        valid_candidates = [
            f
            for f in candidates
            if f[0].date() == target.date()
            and f[0].hour in [target.hour, (target - pd.Timedelta(hours=1)).hour]
        ]
    else:
        valid_candidates = [
            f
            for f in candidates
            if f[0].date() in [target.date(), (target - pd.Timedelta(days=1)).date()]
        ]

    selected = None
    if valid_candidates:
        selected = max(valid_candidates, key=lambda x: x[0])
    else:
        if not candidates:
            logger.error(f"No candidates at all in folder: {folder}")
        else:
            closest = max(candidates, key=lambda x: x[0])
            logger.warning(
                f"No valid match for {target} in '{folder.name}'. Closest available: {closest[0]} (too far)"
            )

    return selected[1] if selected else None


def cleanup_old_files(folder: Path, max_files: int = 365) -> None:
    files = sorted(folder.glob("*.feather"), key=os.path.getmtime, reverse=True)
    for f in files[max_files:]:
        try:
            f.unlink()
            logger.info(f"Deleted old file: {f}")
        except Exception as e:
            logger.warning(f"Failed to delete old file {f}: {e}")
