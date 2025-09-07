import pandas as pd
import numpy as np
import logging

### --- OMITTED --- ###

from features.type_a.training import feature_processing_train
from features.shared_features.categoricals import CATEGORICAL_COLS_A
from ..params import HYPERPARAMETERS_BASELINE_A
from ..mlflow_logger import log_cv_metrics

logger = logging.getLogger(__name__)


def baseline_model_A_train(
    dict_df_client_A: dict[str, pd.DataFrame],
    dict_df_comp_A: dict[str, pd.DataFrame],
    property_id: int,
    n_splits: int = 6,
) -> ### --- OMITTED --- ###:

    ### --- OMITTED --- ###

    return models[best_model_index]
