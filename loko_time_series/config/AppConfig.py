import os
from pathlib import Path

from ds4biz_commons.utils.config_utils import EnvInit

from loko_time_series.utils.logger_utils import logger

env=EnvInit()

# RANDOM_STATE = 2502
logger.debug(f'env repo{env.REPO}')
REPO_PATH = os.path.abspath(env.REPO or '../../repo')
ORCHESTRATOR = f"{env.GATEWAY}/routes/orchestrator/"


PREDICTOR_EVALUATE_FOLDER = '/data/ts_evaluation'
EVALUATE_FILES_EXTENSION = ".eval"