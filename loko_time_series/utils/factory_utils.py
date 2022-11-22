import importlib
import numpy as np
from sktime.forecasting.trend import PolynomialTrendForecaster
from sktime.transformations.series.detrend import Detrender
from sktime.datasets import load_airline
from sktime.forecasting.base import ForecastingHorizon
from sktime.forecasting.model_selection import temporal_train_test_split
from sktime.performance_metrics.forecasting import mean_absolute_percentage_error
from sktime.utils.plotting import plot_series
from sktime.forecasting.compose import TransformedTargetForecaster
from sktime.transformations.series.detrend import Deseasonalizer
from sktime.forecasting.arima import ARIMA
from ds4biz_commons.utils.submodules import ClassByNameLoader



def get_factory(obj, klass="__klass__"):
    if isinstance(obj, dict):
        if klass in obj:
            kl_path = obj[klass]
            mod_path = ".".join(kl_path.split(".")[:-1])
            kl_name = kl_path.split(".")[-1]
            module = importlib.import_module(mod_path)
            kl = getattr(module, kl_name)
            args = get_factory({k: get_factory(v) for k, v in obj.items() if k != klass})
            return kl(**args)
        else:
            for k, v in obj.items():
                return {k: get_factory(v) for (k, v) in obj.items()}
    if isinstance(obj, list):
        return [get_factory(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(get_factory(v) for v in obj)
    return obj


if __name__ == '__main__':
    a = {
        "__klass__": "sktime.forecasting.naive.NaiveForecaster",
        "strategy": "last",
        "sp": 12
    }

    dd = dict(__klass__="sktime.forecasting.compose.TransformedTargetForecaster", steps=[
        ("deseasonalize_year",
         dict(__klass__="sktime.transformations.series.detrend.Deseasonalizer", model="multiplicative", sp=12)), (
            "deseasonalize_trimester",
            dict(__klass__="sktime.transformations.series.detrend.Deseasonalizer", model="multiplicative", sp=3)),
        # (
            # "detrender",
            # dict(__klass__="sktime.transformations.series.detrend.Detrender",
            #      forecaster=dict(__klass__="sktime.forecasting.trend.PolynomialTrendForecaster", degree=1))),
        ("forecast", dict(__klass__="sktime.forecasting.arima.ARIMA"))])

    kl = get_factory(dd)
    print(kl.__dict__)

    forecaster = TransformedTargetForecaster(
        [
            ("deseasonalize", Deseasonalizer(model="multiplicative", sp=12)),
            ("deseasonalize", Deseasonalizer(model="multiplicative", sp=3)),

            ("", Detrender(forecaster=PolynomialTrendForecaster(degree=1))),

            ("forecast", ARIMA()),
        ]
    )

    print(forecaster.__dict__)

    # es = "sktime.forecasting.naive"
    # e = __import__(es)
    # print(e)

    # es = ClassByNameLoader("sktime.forecasting")
    # print(es)
    # "sktime.forecasting.arima.ARIMA"
    # res = get_factory(a)
    # print(type(res))

# class BaseFactory:
#     def __init__(self, klass="__klass__"):
#         self.klass = klass
#         self.transformers = {}
#
#     def register(self, name, transformer):
#         self.transformers[name] = transformer
#
#     def __call__(self, obj):
#         if isinstance(obj, dict):
#             if self.klass in obj:
#                 kl = obj[self.klass]
#                 args = self({k: self(v) for (k, v) in obj.items() if k != self.klass})
#                 if isinstance(kl, type) or callable(kl):
#                     return kl(**args)
#                 else:
#                     return self.transformers[kl](**args)
#             else:
#                 for k, v in obj.items():
#                     return {k: self(v) for (k, v) in obj.items()}
#         if isinstance(obj, list):
#             return [self(v) for v in obj]
#
#         if isinstance(obj, tuple):
#             return (self(v) for v in obj)
#
#         return obj
