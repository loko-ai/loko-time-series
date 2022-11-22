

from sktime.datasets import load_longley, load_airline

_, y = load_longley()
y = y.drop(columns=["UNEMP", "ARMED", "POP"])
# print(y["GNP"].values.tolist())
print(y.index.name)

def get_multioutput_df():
    _, y = load_longley()
    y = y.drop(columns=["UNEMP", "ARMED", "POP"])
    data = dict()
    data["target"] = dict()
    for col in y.columns:
        data["target"][col]= y[col].values.tolist()
    dt_name = y.index.name
    data["data"]= dict()
    data


#
#
#
# # step 1: data specification
# y = load_airline()
# # we create some dummy exogeneous data
# X = pd.DataFrame(index=y.index)
#
# # step 2: specifying forecasting horizon
# fh = np.arange(1, 37)