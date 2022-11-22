from typing import Union, List

import numpy as np
import pandas as pd
from sktime.forecasting.model_selection import temporal_train_test_split
from sktime.forecasting.base import ForecastingHorizon
# from sktime.forecasting.naive import NaiveForecaster
from sktime.forecasting.arima import ARIMA


class TimeSeriesPredictor():
    def __init__(self, model=None):
        self.model = model or ARIMA()
        self.fitted = False

    def fit(self, y, X=None,horizon:Union[int, list]=None, **kwargs):
        """
        If the horizon is specified, then the model is fitted with the horizon. If the horizon is not specified, then the
        model is fitted without the horizon. Some of the Sktime alghorithms necessary requires an horizon.

        :param y: the time series to be forecasted
        :param X: The input data
        :param horizon: The number of periods to forecast
        :type horizon: Union[int, list]
        """
        if horizon:
            if isinstance(horizon, int):
                horizon = np.arange(1, horizon + 1)
            fh = ForecastingHorizon(horizon, is_relative=True)
            self.model.fit(y,X , fh=fh, **kwargs)
        else:
            if self.model.get_tag("requires-fh-in-fit"):
                raise Exception("You have to specify an horizon in order to fit this model..")
            self.model.fit(y, X, **kwargs)
        self.fitted = True

    def predict(self, horizon: Union[int, List] = None):
        """
        The function takes in a horizon (which is a list of integers or an integers) and returns a forecast.
        If no horizon is specified, the function return the right next period with respect to the training set

        :param horizon: The number of periods to forecast
        :type horizon: Union[int, List]
        :return: A dataframe with the predicted values
        """
        if horizon:
            fh = ForecastingHorizon(horizon, is_relative=True)
        else:
            fh = ForecastingHorizon([1], is_relative=True)
        return self.model.predict(fh)

    def partial_fit(self, df, update_params=False):
        """
        > The function takes in a dataframe and updates the model parameters

        :param df: The dataframe to be used for training
        :param update_params: If True, the model parameters are updated. If False, the model parameters are not updated,
        defaults to False (optional)
        """
        self.model.update(df, update_params=update_params)

    def get_params(self):
        """
        It returns the parameters of the model that have been fitted to the data
        :return: The fitted parameters of the model.
        """
        return self.model.get_fitted_params()

