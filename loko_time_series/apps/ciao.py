# from sktime.datasets import generate_example_long_table
# from sktime.datasets import make_multi_index_dataframe
# from sktime.datatypes._panel._convert import (
#     from_3d_numpy_to_nested,
#     from_multi_index_to_3d_numpy,
#     from_nested_to_3d_numpy,
# )
#
#
# X = generate_example_long_table(num_cases=10, series_len=10, num_dims=5)
#
# X_mi = make_multi_index_dataframe(n_instances=50, n_columns=5, n_timepoints=20)
# print(X_mi)
# X_3d = from_multi_index_to_3d_numpy(
#     X_mi, instance_index="case_id", time_index="reading_id"
# )
# print(X_3d)
#
#
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.pipeline import Pipeline
#
# from sktime.classification.compose import ColumnEnsembleClassifier
# from sktime.classification.dictionary_based import BOSSEnsemble
# from sktime.classification.interval_based import TimeSeriesForestClassifier
# # from sktime.classification.shapelet_based import MrSEQLClassifier
# from sktime.datasets import load_basic_motions
# from sktime.transformations.panel.compose import ColumnConcatenator
#
#
# X, y = load_basic_motions(return_X_y=True)
# print(X)
# print(y)
# # X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
# # print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)
# # print(X_train.iloc[0])
#
# # 4 * 6
import pandas as pd
from sktime.datatypes._panel._convert import from_long_to_nested, from_nested_to_long

data = {"data": [{"Date_Time": "01/03/2010  08:00:20", "f1": "a"},
                 {"Date_Time": "01/03/2010  08:00:20", "f1": "b"},
                 {"Date_Time": "01/10/2010  08:00:20", "f1": "b"},
                 {"Date_Time": "01/10/2010  08:00:20", "f1": "a"},
                 {"Date_Time": "01/17/2010  08:00:20", "f1": "a"},
                 {"Date_Time": "01/17/2010  08:00:20", "f1": "b"},
                 {"Date_Time": "01/24/2010  09:00:20", "f1": "a"},
                 {"Date_Time": "01/24/2010  09:00:20", "f1": "b"},
                 {"Date_Time": "01/31/2010  08:20:40", "f1": "b"},
                 {"Date_Time": "01/31/2010  08:20:40", "f1": "a"},
                 {"Date_Time": "02/07/2010  08:20:40", "f1": "a"},
                 {"Date_Time": "02/07/2010  08:20:40", "f1": "b"},
                 {"Date_Time": "02/14/2010  08:20:40", "f1": "b"},
                 {"Date_Time": "02/14/2010  08:20:40", "f1": "a"},
                 {"Date_Time": "02/21/2010  08:20:40", "f1": "a"},
                 {"Date_Time": "02/21/2010  08:20:40", "f1": "b"},
                 {"Date_Time": "02/28/2010  08:20:40", "f1": "a"},
                 {"Date_Time": "02/28/2010  08:20:40", "f1": "b"},
                 {"Date_Time": "03/07/2010  08:20:40", "f1": "a"},
                 {"Date_Time": "03/07/2010  08:20:40", "f1": "b"},
                 {"Date_Time": "03/14/2010  08:20:40", "f1": "a"},
                 {"Date_Time": "03/14/2010  08:20:40", "f1": "b"},
                 {"Date_Time": "03/21/2010  08:20:40", "f1": "b"},
                 {"Date_Time": "03/21/2010  08:20:40", "f1": "a"}
                 ],
        "target": [1509634, 1581344, 1614204, 1897725,
                   1759063, 1320022, 1559063, 1659063,
                   1859063, 1551083, 1819012, 1801029,
                   1509634, 1581344, 1614204, 1897725,
                   1759063, 1320022, 1559063, 1659063,
                   1859063, 1551083, 1819012, 1801029
                   ]}


df = pd.DataFrame(data["data"])
df["Date_Time"] = pd.PeriodIndex(df["Date_Time"], freq="7D" )
df["target"] = data["target"]
df.set_index(["Date_Time", "f1"], inplace=True)
print(df)
# X_nested = from_long_to_nested(df, time_column_name="Date_Time", instance_column_name="target", dimension_column_name="f1", value_column_name="target")
# print(X_nested)
