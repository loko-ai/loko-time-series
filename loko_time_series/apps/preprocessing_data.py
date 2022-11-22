import pandas as pd

data = {"data":[{"Date_Time": "01/03/2010 08:00:20" },
       {"Date_Time": "01/10/2010 08:00:20"},
       {"Date_Time": "01/17/2010  08:00:20"},
       {"Date_Time": "01/24/2010  09:00:20"},
       {"Date_Time": "01/31/2010  08:20:40"}],
     "target":[1509634,1581344, 1614204, 1897725, 1759063]}



data = {"data":[{"Date_Time": 1 },
                {"Date_Time": 2},
                {"Date_Time": 3},
                {"Date_Time": 4},
                {"Date_Time": 5},
                {"Date_Time": 6},
                {"Date_Time": 7},
                {"Date_Time": 8},
                {"Date_Time": 9},
                {"Date_Time": 10},
                {"Date_Time": 11},
                {"Date_Time": 12}],
 "target":[1509634,1581344, 1614204, 1897725, 1759063,1320022, 1559063, 1659063, 1859063, 1551083, 1819012, 1801029]}

#
#
# data = {"data":[{"Date_Time": 1961 },
#                 {"Date_Time": 1962},
#                 {"Date_Time": 1963},
#                 {"Date_Time": 1964},
#                 {"Date_Time": 1965},
#                 {"Date_Time": 1966},
#                 {"Date_Time": 1967},
#                 {"Date_Time": 1968},
#                 {"Date_Time": 1969},
#                 {"Date_Time": 1970},
#                 {"Date_Time": 1971},
#                 {"Date_Time": 1972}],
#  "target":[1509634,1581344, 1614204, 1897725, 1759063,1320022, 1559063, 1659063, 1859063, 1551083, 1819012, 1801029]}

df = pd.DataFrame(data["data"])
df["Date_Time2"] = pd.to_datetime(df["Date_Time2"])

# df["Date_Time2"] = pd.PeriodIndex(df["Date_Time"], freq="y")
print(df)

# if len(df.columns)==1:
#     dt_feature = df.columns[0]
#     df["target"] = data["target"]
#     df.set_index(dt_feature, inplace=True)
#     print(df)