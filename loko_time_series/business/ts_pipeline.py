from types import NoneType
from typing import List, Union

import numpy as np
import pandas as pd
from sktime.forecasting.compose import TransformedTargetForecaster

from loko_time_series.model.transformer_model import TimeSeriesTransformer
from sktime.forecasting.base import ForecastingHorizon

from loko_time_series.utils.logger_utils import logger
from sktime.performance_metrics.forecasting import mean_squared_error, mean_absolute_error, MeanAbsolutePercentageError


class TSPipeline():
    def __init__(self, **kwargs):
        self.id = "Unknown"
        self.steps = []
        self.fitted = False
        self.datetime_feature = None
        self.datetime_frequency = None
        self.__dict__.update(kwargs)
        print("tspipeline ", self.__dict__)

    #
    # def _unpack_transformer(self, transformer: TimeSeriesTransformer):
    #     return (transformer.name, transformer.transformer)

    def add(self, obj):
        self.steps.append(obj)

    #
    # def initialize_pipeline(self):
    #     pipeline_steps = [self._unpack_transformer(t) for t in self.transformers]
    #     pipeline_steps.append(self.model)
    #     self.pipeline = TransformedTargetForecaster(pipeline_steps)

    def fit(self, y, X=None, horizon: Union[int, list] = None, **kwargs):
        logger.info(f"fitting predictor {self.id}")
        logger.debug('y size: %s' % str(len(y)))
        logger.debug('y shape %s' % str(y.shape))
        # logger.debug("n. target: ", str(y.shape[1]))
        if isinstance(X, pd.DataFrame):
            logger.debug('X size: %s' % str(X.shape))
        for i in range(len(self.steps)):
            name, obj = self.steps[i]
            logger.debug(f'Fitting {name}')
            if name == 'transformer':
                logger.debug('TRANSFORMER: %s' % str(obj))
                if isinstance(X, pd.DataFrame):
                    obj.fit(X=y, y=X)
                    y = obj.transform(X=y, y=X) #andiamo ad applicare la trasformazione su y, tenendo conto dei valori di X
                else:
                    y = obj.fit_transform(y)
                # y = y.astype(np.float)
                # logger.debug('X transformed size: %s' % str(X.shape))

            if name == 'model':
                logger.debug('MODEL: %s' % str(obj))
                # m = obj.fit(y = y, x=X, **kwargs)
                if horizon:
                    logger.debug(f"horizon: {horizon}")
                    if isinstance(horizon, int):
                        horizon = np.arange(1, horizon + 1)
                    fh = ForecastingHorizon(horizon, is_relative=True)
                    try:
                        obj.fit(y=y, X=X, fh=fh)
                    except Exception as e:
                        logger.error(f"Error:: {e}")
                        raise e
                else:
                    if obj.get_tag("requires-fh-in-fit"):
                        raise Exception("You have to specify an horizon in order to fit this model..")
                    obj.fit(y=y, X=X, **kwargs)


    def predict(self, X=None, horizon: Union[int, list, pd.PeriodIndex] = None, h_is_relative: bool=True, **kwargs):
        logger.debug('PREDICT')
        logger.debug(f"XXXXXXXXXXXXXXXXX {X}")
        # logger.debug(f"X rows {len(X)}")
        # logger.debug('X size: %s' % str(X.shape))
        for name, obj in self.steps:
            if name == 'transformer':
                logger.debug('TRANSFORMER: %s' % str(obj))
                #todo: decidere se applicare transformer all'interno o all'esterno
                # if isinstance(X, pd.DataFrame):
                #     X = obj.transform(X)
                #     X = X.astype(np.float)
                #     logger.debug('X transformed size: %s' % str(X.shape))
            if name == 'model':

                logger.debug('MODEL: %s' % str(obj))
                logger.debug(f"horrrrrrr {horizon}")
                if not isinstance(horizon, NoneType):
                    if isinstance(horizon, int):
                        horizon = np.arange(1, horizon + 1)
                    if isinstance(horizon, pd.PeriodIndex):
                        h_is_relative = False

                else:
                    logger.debug("no forecasting horizon specified, predicting the next available occurrence...")
                    horizon = [1]
                fh = ForecastingHorizon(horizon, is_relative=h_is_relative)
                logger.debug(f"ciiiaooo {fh}")
                # if include_probs:
                #     if hasattr(obj, "predict_proba"):
                #         classes = obj.classes_
                #         try:
                #             return [sorted(zip(classes, row), key=lambda x: x[1], reverse=True)
                #                     for row in obj.predict_proba(X, **kwargs)]
                #         except AttributeError:
                #             raise PredictProbaException("%s has not predict_proba" % obj.__class__.__name__)
                #     else:
                #         raise PredictProbaException("%s has not predict_proba" % obj.__class__.__name__)
                # else:
                preds = obj.predict(fh=fh, X=X, **kwargs)
                logger.debug(f"prediction: {preds.to_dict()}")
                for name, obj in self.steps:
                    if name == "transformer":
                        preds = obj.inverse_transform(X=preds, y=X)
                        break
                preds = preds.to_dict()
                logger.debug(f"prediction after transformation: {preds}")
                return preds

    def get_forecast_report(self, y, X=None):
        # horizon =
        if not isinstance(X, pd.DataFrame):
            horizon = y.index
            print(f'Horizon {horizon}')

        else:
            horizon = X.index

        logger.debug(f"horizon:: {horizon}")

        y_pred = self.predict(X=X, horizon=horizon, h_is_relative=False)
        y_pred = pd.DataFrame(y_pred)
        logger.debug("computing metrics")
        logger.debug(f"ypred {y_pred}")
        logger.debug(f"y true {y}")

        mape = MeanAbsolutePercentageError()
        mape = mape.evaluate(y, y_pred)

        smape = MeanAbsolutePercentageError(symmetric=True)
        smape = smape.evaluate(y, y_pred)

        mse = mean_squared_error(y, y_pred)
        rmse = mean_squared_error(y, y_pred, squared=False)
        mae = mean_absolute_error(y, y_pred)
        # R2 = r2_score(y, y_pred),
        # EXPLAINED_VARIANCE = explained_variance_score(y, y_pred),
        perc_error = mae * 100.0 / (max(y.values.flatten()) - min(y.values.flatten()))
        perc_error_recomputed = (abs(np.array(y_pred) - np.array(y)) / (np.array(y) + 1)).mean()
        scatter = dict(y_true=y.values.flatten().tolist(), y_pred=y_pred.values.flatten().tolist())

        report = dict(
            MAPE=mape,
            SMAPE=smape,
            MSE=mse,
            RMSE=rmse,
            MAE=mae,
            # R2 = r2_score(y, y_pred),
            # EXPLAINED_VARIANCE = explained_variance_score(y, y_pred),
            PERC_ERROR=perc_error,
            PERC_ERROR_RECOMPUTED=perc_error_recomputed,
            scatter=scatter)
        logger.debug('MSE SCORE: %s' % str(report['MSE']))
        # logger.debug('R2: %s' % str(report['R2']))
        return report

    # def partial_fit(self, df, update_params=False):
    #     """
    #     > The function takes in a dataframe and updates the model parameters
    #
    #     :param df: The dataframe to be used for training
    #     :param update_params: If True, the model parameters are updated. If False, the model parameters are not updated,
    #     defaults to False (optional)
    #     """
    # self.model.update(df, update_params=update_params)

    # def get_params(self):
    #     """
    #     It returns the parameters of the model that have been fitted to the data
    #     :return: The fitted parameters of the model.
    #     """
    #     return self.model.get_fitted_params()
