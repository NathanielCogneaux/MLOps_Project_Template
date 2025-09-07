import mlflow
import numpy as np
import datetime

from config.settings import MLFLOW_TRACKING_URI


def log_cv_metrics(
    property_id: int, scrap_type: str, all_scores: dict[str, dict[str, list]]
):
    tracking_uri = MLFLOW_TRACKING_URI
    mlflow.set_tracking_uri(tracking_uri)

    experiment_name = "baseline"
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=f"property_{property_id}_type_{scrap_type.upper()}"):
        mlflow.log_param("property_id", property_id)
        mlflow.set_tag("type", scrap_type.upper())
        mlflow.set_tag(
            "timestamp", datetime.datetime.now().isoformat(timespec="seconds")
        )

        for split in ["train", "val", "test"]:
            for metric, values in all_scores[split].items():
                mlflow.log_metric(f"{split}_{metric}", np.mean(values))
