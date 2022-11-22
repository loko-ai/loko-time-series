import json
import os

from loko_time_series.utils.logger_utils import logger


def serialize(path, obj):
    logger.debug(f"path::: {path}\n obj:::{obj}\n ------------")
    with open(os.path.join(path, "blueprint.json"), "w") as jf:
        json.dump(obj, jf, indent=2)


def deserialize(path):
    with open(os.path.join(path, "blueprint.json"), "r") as file:
        j = json.load(file)
    return j

