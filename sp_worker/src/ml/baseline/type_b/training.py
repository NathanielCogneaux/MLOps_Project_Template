import pandas as pd
import numpy as np
import logging

### --- OMITTED --- ###

from features.type_b.training import feature_processing_train
from features.shared_features.categoricals import CATEGORICAL_COLS_B
from ..params import HYPERPARAMETERS_BASELINE_B
from ..mlflow_logger import log_cv_metrics

logger = logging.getLogger(__name__)


def baseline_model_B_train(
    dict_df_client_B: dict[str, pd.DataFrame],
    dict_df_comp_B: dict[str, pd.DataFrame],
    property_id: int,
    n_splits: int = 6,
) -> ### --- OMITTED --- ###:

    ### --- OMITTED --- ###

    return models[best_model_index]
