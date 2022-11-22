import sys

import pandas as pd
from sktime.datasets import load_longley
from sktime.forecasting.arima import ARIMA
from sktime.forecasting.base import ForecastingHorizon

_, y = load_longley()

y = y.drop(columns=["UNEMP", "ARMED", "POP"])
y.reset_index(drop=False)
print(y)
forecaster = ARIMA()
forecaster.fit(y)
print(forecaster.forecasters_)
idx = (pd.to_datetime(["1963", "1964","1965","1966"], format='%Y-%m-%d'))
print(y.index)
# print("============ \n", idx)

print("===============opzione 1 ==============")

#opzione 1
#passo gli anni come periodo
idx = pd.PeriodIndex([1963, 1964,1965,1966], freq="A-DEC")
fh = ForecastingHorizon(idx, is_relative=False)
print(fh)
print(forecaster.predict(fh))
print("===============opzione 2 ==============")
sys.exit(0)

#opzione 2
#passo un singolo momento t da predire
fh = ForecastingHorizon(5, is_relative=True) #equivalente a [5]
print(fh)
print(forecaster.predict(fh))

print("===============opzione 3 ==============")


#opzione 3
#passo una lista di momenti t che voglio valutare
idx = [1,2,5,8]
fh = ForecastingHorizon(idx, is_relative=True)
print(fh)
print(forecaster.predict(fh))






