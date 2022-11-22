import sktime.datasets
from loko_extensions.model.components import Component, Input, Output, save_extensions, Select, Arg, Dynamic

sktime_df = es = [x for x in sktime.datasets.__all__ if x.startswith("load") ]


load_df_service = "loko-services/datasets"
# load_df_service = "loko-services/predictors/predict"
args = Select(name="dataset", label="Dataset", options=sktime_df)
args_list = [args]

##################### Time SERIES MANAGER ###########################
df_inputs = [Input(id="load_df", label="Get DF", to="load_df", service=load_df_service)]


##################### Time SERIES MANAGER ###########################
df_outputs = [Output(id="load_df", label="Get DF")]

df_component = Component(name="TS Dataset", description="Components that get example of dataset for TimeSeries task", inputs= df_inputs, outputs=df_outputs, args=args_list)


