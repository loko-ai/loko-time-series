# print(y)
#
# ex_dict = [{'Date_Time': '01/03/2010 08:00:20', 'Count_Pedestrians': 1509634}, {'Date_Time': '01/10/2010', 'Count_Pedestrians': 1581344}, {'Date_Time': '01/17/2010  08:00:20', 'Count_Pedestrians': 1614204}, {'Date_Time': '01/24/2010  09:00:20', 'Count_Pedestrians': 1897725}, {'Date_Time': '01/31/2010  08:20:40', 'Count_Pedestrians': 1759063}]
import pandas as pd
from sktime.transformations.series.exponent import ExponentTransformer
# from sktime.transformations.all import Tra
from sktime.transformations.compose import TransformerPipeline
from sktime.forecasting.compose import TransformedTargetForecaster
from sktime.transformations.series.detrend import Deseasonalizer
from sktime.forecasting.model_selection import temporal_train_test_split
from sktime.forecasting.arima import ARIMA

ex_dict2 = {"data":[{"Date_Time": "03/2010 " },
       {"Date_Time": "01/10/2010  08:20:40"},
       {"Date_Time": "01/17/2010  08:20:40"},
       {"Date_Time": "01/24/2010  08:20:40"},
       {"Date_Time": "01/31/2010  08:20:40"},
      {"Date_Time": "02/07/2010  08:20:40"},
      {"Date_Time": "02/14/2010  08:20:40"},
      {"Date_Time": "02/21/2010  08:20:40"},
      {"Date_Time": "02/28/2010  08:20:40"},
      {"Date_Time": "03/07/2010  08:20:40"},
      {"Date_Time": "03/14/2010  08:20:40"},
      {"Date_Time": "03/21/2010  08:20:40"}],
     "target":[1509634,1581344, 1614204, 1897725, 1759063,1320022, 1559063, 1659063, 1859063, 1551083, 1819012, 1801029]}

#
#
# ex_dict2 = {"data":[{"Date_Time": "01/03/2010" },
#        {"Date_Time": "01/10/2010"},
#        {"Date_Time": "01/17/2010"},
#        {"Date_Time": "01/24/2010"},
#        {"Date_Time": "01/31/2010"},
#       {"Date_Time": "02/07/2010"},
#       {"Date_Time": "02/14/2010"},
#       {"Date_Time": "02/21/2010"},
#       {"Date_Time": "02/28/2010"},
#       {"Date_Time": "03/07/2010"},
#       {"Date_Time": "03/14/2010"},
#       {"Date_Time": "03/21/2010"}],
#      "target":[1509634,1581344, 1614204, 1897725, 1759063,1320022, 1559063, 1659063, 1859063, 1551083, 1819012, 1801029]}
#

df = pd.DataFrame(ex_dict2["data"])
df["target"] = ex_dict2["target"]
df["Date_Time"] = pd.PeriodIndex(df["Date_Time"], freq='s')

# print("!!!!!!!!!!!!!!!!!!!!!!!!", idx)

# df["Date_Time"] = pd.to_datetime(df["Date_Time"])
print(df)
df.set_index("Date_Time", inplace=True)



from sktime.forecasting.base import ForecastingHorizon
print("splitto")
y_train, y_test = temporal_train_test_split(y=df,X=None, test_size=5)
print(y_test)

# transf = TransformerPipeline(steps=[Deseasonalizer(model="additive", sp=3)])
t1 = ExponentTransformer(power=2)
transf = TransformerPipeline(steps=[ExponentTransformer(power=2)])
y_train = transf.fit_transform(y_train)
print("yyyy", y_train)

forecaster = ARIMA()
forecaster.fit(y_train)
print("ok")
fh = ForecastingHorizon([1,2,3], is_relative=True) #equivalente a [5]
print(fh)
a = forecaster.predict(fh=fh)
print("--- \n",a)
#
# from sktime.datasets import load_longley
#
#
# _, y = load_longley()
# y = y.drop(columns=["UNEMP", "ARMED", "POP", "GNPDEFL"])
# print(y)
# #
# # y_train, y_test = temporal_train_test_split(y=y,X=None, test_size=0.2)
# #
# # print(y_train)
# # y_train = transf.fit_transform(y_train)
# # print(y_train)
# res = []
# for i in range(0,16):
#     el={"Period":y.index[i]}
#     res.append(el)
# res.append({"target":y.values.reshape(-1)})
# print(res)