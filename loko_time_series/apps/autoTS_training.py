from sktime.datasets import load_arrow_head
from sklearn.model_selection import train_test_split
from autots import AutoTS, load_daily


# sample datasets can be used in either of the long or wide import shapes
df = load_daily(long=False)
model = AutoTS(
    forecast_length=21,
    frequency='infer',
    prediction_interval=0.9,
    ensemble=None,
    model_list="superfast",  # "superfast", "default", "fast_parallel"
    transformer_list="superfast",  # "superfast",
    drop_most_recent=1,
    max_generations=4,
    num_validations=2,
    validation_method="backwards"
)

long = False
model = model.fit(
    df,
    date_col='datetime' if long else None,
    value_col='value' if long else None,
    id_col='series_id' if long else None,
)
prediction = model.predict()

prediction.plot(model.df_wide_numeric,
                series=model.df_wide_numeric.columns[0],
                start_date="2019-01-01")