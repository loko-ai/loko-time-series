from sktime.forecasting.model_selection import temporal_train_test_split

import numpy as np
import sklearn
from sktime.classification.interval_based import TimeSeriesForestClassifier
from sktime.datasets import load_arrow_head
from sklearn.metrics import accuracy_score
from sktime.transformations.panel.rocket import Rocket
from sklearn.linear_model import RidgeClassifierCV
from sktime.datasets import load_longley


_, y = load_longley()
y = y.drop(columns=["UNEMP", "ARMED", "POP"])
print(y)
from sktime.forecasting.arima import ARIMA

import pandas as pd
print("inizio")
filename = "/home/roberta/Downloads/Pedestrian_Counting_System_-_Monthly__counts_per_hour_.csv"
df = pd.read_csv(filename, usecols=['Date_Time', 'Sensor_Name', 'Hourly_Counts'])
# Convert date to datetime
df['Date_Time'] = pd.to_datetime(df['Date_Time'])

# Group all sensors
df_grouped = df.groupby(['Date_Time']).agg({'Hourly_Counts': 'sum'}).rename(columns={'Hourly_Counts': 'Count_Pedestrians'})

# Aggregate weekly
df_weekly = df_grouped.resample('W').sum()

# Filter from the start of 2010 to end of 2019
df_weekly = df_weekly['2010-01-01': '2019-12-31']
# example = df_weekly.head(5)
df_weekly.index = df_weekly.index.strftime('%m-%d-%Y %H:%M:%S.%f')
print("qui")
# example.reset_index(drop=False, inplace=True)

# print(example.to_dict(orient="records"))

y = df_weekly.squeeze() # prepare the data as a pandas Series
# print(y)
#
# ex_dict = [{'Date_Time': '01/03/2010 08:00:20', 'Count_Pedestrians': 1509634}, {'Date_Time': '01/10/2010', 'Count_Pedestrians': 1581344}, {'Date_Time': '01/17/2010  08:00:20', 'Count_Pedestrians': 1614204}, {'Date_Time': '01/24/2010  09:00:20', 'Count_Pedestrians': 1897725}, {'Date_Time': '01/31/2010  08:20:40', 'Count_Pedestrians': 1759063}]
ex_dict2 = {"data":[{"Date_Time": "01/03/2010  08:00:20" },
       {"Date_Time": "01/10/2010  08:00:20"},
       {"Date_Time": "01/17/2010  08:00:20"},
       {"Date_Time": "01/24/2010  09:00:20"},
       {"Date_Time": "01/31/2010  08:20:40"},
      {"Date_Time": "02/07/2010  08:20:40"},
      {"Date_Time": "02/14/2010  08:20:40"},
      {"Date_Time": "02/21/2010  08:20:40"},
      {"Date_Time": "02/28/2010  08:20:40"},
      {"Date_Time": "03/07/2010  08:20:40"},
      {"Date_Time": "03/14/2010  08:20:40"},
      {"Date_Time": "03/21/2010  08:20:40"}],
     "target":[1509634,1581344, 1614204, 1897725, 1759063,1320022, 1559063, 1659063, 1859063, 1551083, 1819012, 1801029]}


e = pd.DataFrame.from_dict(ex_dict2)
e["new_dt"] = pd.to_datetime(e["Date_Time"])
print(e)
e.set_index("Date_Time", inplace=True)
# e = e.squeeze()

# [{'Date_Time': Timestamp('2010-01-03 00:00:00'), 'Count_Pedestrians': 1509634}, {'Date_Time': Timestamp('2010-01-10 00:00:00'), 'Count_Pedestrians': 1581344}, {'Date_Time': Timestamp('2010-01-17 00:00:00'), 'Count_Pedestrians': 1614204}, {'Date_Time': Timestamp('2010-01-24 00:00:00'), 'Count_Pedestrians': 1897725}, {'Date_Time': Timestamp('2010-01-31 00:00:00'), 'Count_Pedestrians': 1759063}]

from sktime.forecasting.model_selection import temporal_train_test_split


from sktime.forecasting.base import ForecastingHorizon
print("splitto")
y_train, y_test = temporal_train_test_split(y=y, X=None, test_size=5)
print(y_test)

y_train.index = pd.to_datetime(y_train.index, infer_datetime_format=True,)

y_test.index = pd.to_datetime(y_test.index, infer_datetime_format=True,)

fh = ForecastingHorizon(list(e["new_dt"]), is_relative=False)
print(fh)



forecaster = ARIMA()
forecaster.fit(y, fh=[1,2,3])
# fh = ForecastingHorizon(y_test.index, is_relative=False)
print("--------------------!!! ",forecaster.predict())
