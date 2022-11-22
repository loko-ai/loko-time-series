import pandas as pd

from loko_time_series.utils.core_utils import to_dataframe
from loko_time_series.utils.logger_utils import logger


def preprocessing_data(data, datetime_feature, datetime_frequency, task="forecasting", get_only_X = False):
    logger.debug(f"datetime feature::: {datetime_feature}")
    logger.debug(f"datetime frequency::: {datetime_frequency}")
    res_data = None
    if isinstance(data, dict):
        res_data = data.get("data", None)

    if not res_data:
        logger.debug(f"res data == {res_data}")
        return dict(X=res_data)

    if not get_only_X:
        target = data['target'] if task != 'classification' else [str(el) for el in data['target']]

    df = to_dataframe(res_data)

    if not datetime_feature in df.columns:
        logger.debug(f"features availables: {df.columns}")
        raise Exception("The datetime_feature specified doesn't match any features in your data, please check again.")
    df[datetime_feature] = pd.PeriodIndex(df[datetime_feature], freq=datetime_frequency)

    if len(df.columns)==1:
        logger.debug("only datetime feature available - no other covariates")

        if get_only_X:
            return dict(X=None)
        else:
            df["target"] = target
            df.set_index(datetime_feature, inplace=True)
            return dict(y=df, X=None)
    else:
        n_covariates = len(df)
        logger.debug("covariates available: %s" % str(n_covariates))
        df.set_index(datetime_feature, inplace=True)
        if get_only_X:
            return dict(X=df)
        else:
            target = pd.DataFrame(target)
            target.set_index(df.index, inplace=True)
            return dict(y=target, X=df)
