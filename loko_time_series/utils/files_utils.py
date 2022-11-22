import json

import requests

from loko_time_series.config.AppConfig import EVALUATE_FILES_EXTENSION, PREDICTOR_EVALUATE_FOLDER, ORCHESTRATOR
from loko_time_series.utils.logger_utils import logger


def save_eval_file(eval_fname, data):
    fpath = PREDICTOR_EVALUATE_FOLDER + "/" + eval_fname + EVALUATE_FILES_EXTENSION
    file_writer_path = ORCHESTRATOR + "files" + fpath
    logger.debug(f"GW url for writing file: {file_writer_path}")
    data = json.dumps(data)
    res = requests.post(file_writer_path, data=data)
    logger.debug(f"Response GW post request: {res}")
