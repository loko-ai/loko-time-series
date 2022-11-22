

from sktime.datasets import load_longley, load_airline


_, y = load_longley()
y = y.drop(columns=["UNEMP", "ARMED", "POP"])

print(y)



# step 1: data specification
y = load_airline()
# we create some dummy exogeneous data
X = pd.DataFrame(index=y.index)

# step 2: specifying forecasting horizon
fh = np.arange(1, 37)