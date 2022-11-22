from typing import List, Union


class FitServiceArgs():
    def __init__(self, datetime_feature, datetime_frequency, task="forecasting", forecasting_horizon_fit=None, report=False, test_size=0.2, **kwargs):
        self.task = task
        self.forecasting_horizon = forecasting_horizon_fit
        self.report = report
        self.test_size = test_size
        self.datetime_feature = datetime_feature
        self.datetime_frequency = datetime_frequency

    def to_dict(self):
        return self.__dict__


class PredictServiceArgs():
    def __init__(self, forecasting_horizon: Union[int, List[int]], **kwargs):
        fh = forecasting_horizon
        if isinstance(forecasting_horizon, str):
            fh = eval(forecasting_horizon)
            if isinstance(fh, list):
                fh = [eval(v) for v in fh]
        self.forecasting_horizon = fh

    def to_dict(self):
        return self.__dict__


class EvaluateServiceArgs():
    def __init__(self, save_eval_report, eval_fname=None, **kwargs):
        self.save_eval_report = save_eval_report
        self.eval_fname = eval_fname

    def to_dict(self):
        return self.__dict__

if __name__ == '__main__':

    es = dict(datetime_feature="ciao", datetime_frequency="7d", task="forecasting", forecasting_horizon=2, report=True, test_size=2, miao="b", cane="d")
    fs = FitServiceArgs(**es).to_dict()
    print(fs)