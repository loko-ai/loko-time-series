# from ds4biz_commons.business.factories import BaseFactory
from loko_time_series.config.factory_config import FACTORY
from loko_time_series.utils.serialization_utils import deserialize

blueprint = deserialize("/home/roberta/Documents/ds4biz-projects/ds4biz-time-series/repo/transformers/prova1/")
a = FACTORY(blueprint)
# FACTORY.register("")
print(a)