from ds4biz_commons.business.factories import BaseFactory
from sktime.transformations.compose import TransformerPipeline
from ds4biz_commons.utils.submodules import ClassByNameLoader
from loko_time_series.utils.logger_utils import logger
# from sktime.forecasting.

logger.debug("starting base factory ....")

FACTORY = BaseFactory()


for name,kl in ClassByNameLoader("sktime").klasses.items():
    print(f"name {name}, kl {kl}")
    # kl=filter_modules(kl, ["sklearn.utils.tests.test_pprint","sklearn.ensemble._gb_losses"])
    FACTORY.register("skt."+name,list(kl)[0])


# for name,kl in ClassByNameLoader("sktime.transformations").klasses.items():
#    # kl=filter_modules(kl, ["sklearn.utils.tests.test_pprint","sklearn.ensemble._gb_losses"])
#    FACTORY.register("skt."+name,list(kl)[0])

FACTORY.register("skt.TransformerPipeline", TransformerPipeline)
logger.debug("factory done....")

if __name__ == '__main__':
    print("\n\n\n")
    print(FACTORY.__dict__)
    # a = {"__klass__": "skt.TransformerPipeline",
    #             "steps": [{"__klass__": "skt.Deseasonalizer", "model":"multiplicative","sp":12 }]}
    # r = FACTORY(a)
    # print(type(r))


