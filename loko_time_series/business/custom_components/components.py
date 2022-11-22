from loko_extensions.model.components import Component, Input, Output, save_extensions, Select, Arg, Dynamic

predict_service = "loko-services/predictors/predict"
fit_service = "loko-services/predictors/fit"
evaluate_service = "loko-services/predictors/evaluate"


#########################   ARGS     ###########################

##################### Time SERIES MANAGER ###########################



################### TIME SERIES    ########################################

pred_name = Arg(name="predictor_name", label="Predictor Name", type="text",
                helper="Digit the name of the predictor you want to use", required=True)
#### FIT ARGS

fit_group = "Fit Parameters"
# task = Select(name="task", label="Task", options=["Forecasting","Classification"], group="fit")

fh = Arg(name="forecasting_horizon_fit", label="Forecasting Horizon", type="number", group=fit_group)
dt_feature = Arg(name="datetime_feature", label="Datetime Feature", type="text",
                 helper="Name of the feature to use as date-time reference", group=fit_group)
dt_frequency = Arg(name="datetime_frequency", label="Datetime Frequency", type="text",
                   helper="Time frequence required for the model ", group=fit_group)
report = Arg(name="report", label="Compute metrics report", type="boolean", group=fit_group, value="false")
test_size = Dynamic(name="test_size", label="Test Size", parent="report", condition="{parent}===true",
                    dynamicType="number", group=fit_group, value=30)

fit_args = [dt_feature, dt_frequency, fh, report, test_size]
#### PREDICT ARGS

pred_group = "Predict Parameters"
fh_pred = Arg(name="forecasting_horizon", label="Forecasting Horizon", type="number", group=pred_group, value=1)

# Arg(name= , label= , type= , group= "predict" )

predict_args = [fh_pred]
#### EVALUATE ARGS

eval_group = "Evaluate parameters"

report_eval = Arg(name="save_eval_report", label="Save metrics report", type="boolean", group=eval_group, value=False)
eval_fname = Dynamic(name='eval_fname', label='Evaluation file name', parent="save_eval_report", dynamicType="text", condition='{parent}===true',
                     # helper="ciao",
                     # description='Type the file name in which you want to store evaluation metrics.',# It will be automatically saved in the path \"data/prediction evaluations\" with extension \".eval\".',
                     group=eval_group)
evaluate_args = [report_eval, eval_fname]

args_list = [pred_name] + fit_args + predict_args + evaluate_args
#########################   INPUT   ###########################
inp = [Input(id="fit", label="fit", to="fit", service=fit_service),
       Input(id="predict", label="predict", service=predict_service, to="predict"),
       Input(id="evaluate", label="evaluate", to="evaluate", service=evaluate_service)]


#########################   OUTPUT   ###########################

out = [Output(id="fit", label="fit"), Output(id="predict", label="predict"), Output(id="evaluate", label="evaluate")]



#########################   COMPONENT   ###########################

time_series_component = Component(name="TimeSeries", description="###TimeSeries components", inputs=inp,
               outputs=out, args=args_list, configured=False, icon="RiFundsBoxFill")



