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


# data loading for illustration (see section 1 for explanation)
print("a")
y = load_airline()
y_train, y_test = temporal_train_test_split(y=y, test_size=36)
print(y_test)
print("qui")
forecaster = PolynomialTrendForecaster(degree=1)
transformer = Detrender(forecaster=forecaster)
yt = transformer.fit_transform(y_train)

# internally, the Detrender uses the in-sample predictions
# of the PolynomialTrendForecaster
forecaster = PolynomialTrendForecaster(degree=1)
fh_ins = -np.arange(len(y_train))  # in-sample forecasting horizon
y_pred = forecaster.fit(y_train).predict(fh=fh_ins)

# plot_series(y_train, y_pred, yt, labels=["y_train", "fitted linear trend", "residuals"]);

forecaster = (
    Deseasonalizer(model="multiplicative", sp=12)
    * Deseasonalizer(model="multiplicative", sp=3)
    * ARIMA()
)

print(forecaster.get_params())


forecaster = TransformedTargetForecaster(
    [
        ("deseasonalize", Deseasonalizer(model="multiplicative", sp=12)),
        ("deseasonalize", Deseasonalizer(model="multiplicative", sp=3)),

        ("",Detrender(forecaster=PolynomialTrendForecaster(degree=1))),

        ("forecast", ARIMA()),
    ]
)
print(forecaster.get_params())
a = Deseasonalizer(model="multiplicative", sp=12)

# y_pred = forecaster.predict(fh)
# plot_series(y_train, y_test, y_pred, labels=["y_train", "y_test", "y_pred"])
# mean_absolute_percentage_error(y_test, y_pred, symmetric=False)

import joblib

# save
joblib.dump(forecaster, "model_forecast")

idx = [1,2,5,8]
fh = ForecastingHorizon(idx, is_relative=True)
clf2 = joblib.load("model_forecast")
print("===================")
print(type(clf2))
print("=====================")
print(clf2.predict(fh))
print("===================")
print(forecaster.predict(fh))