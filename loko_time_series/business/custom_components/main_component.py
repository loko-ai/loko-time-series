from loko_time_series.business.custom_components.components import time_series_component
from loko_time_series.business.custom_components.datasets_components import df_component
from loko_extensions.model.components import save_extensions
from loko_time_series.business.custom_components.ts_manager_components import ts_manager_component

if __name__ == '__main__':
    save_extensions([time_series_component, df_component, ts_manager_component], path="../extensions")
    #     "url": "http://localhost:9999/routes/ds4biz-time-series/transformers"
