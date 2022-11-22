from loko_time_series.model.timeseries_model import TimeSeriesPredictor
from sktime.datasets import load_longley


_, y = load_longley()

y = y.drop(columns=["UNEMP", "ARMED", "POP"])

tsp = TimeSeriesPredictor()
tsp.fit(y, test_size=5)
print(tsp.predict(5))
pred = tsp.predict(5)
pred
print(tsp.predict(10))
tsp.partial_fit(pred, update_params=False)

print(tsp.predict(5))
