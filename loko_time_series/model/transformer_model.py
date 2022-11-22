

class TimeSeriesTransformer():
    def __init__(self, transformer, t_name=None):
        self.transformer = transformer
        self.t_name = t_name if t_name else self.transformer.__class__.__name__


