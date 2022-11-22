import pandas as pd
from sktime.datasets import load_arrow_head, load_basic_motions
X, y = load_arrow_head(return_X_y=True)
# X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
# print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)
# print(pd.MultiIndex.from_(X))

#{"target": ['0' '1' '2' '0' '1' '2' '0' '1' '2' '0']}

from sktime.forecasting.base import ForecastingHorizon
idx = pd.PeriodIndex(['2010-03', '2010-04'], dtype='period[M]', name='Date_Time')
fh = ForecastingHorizon(idx, is_relative =False)
print(fh)