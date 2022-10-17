import io
import re
import shutil
import time
import traceback

from sanic import Sanic, Blueprint
from sanic_openapi import swagger_blueprint
from sanic_openapi.openapi2 import doc
from sanic_cors import CORS
from urllib.parse import unquote
from pathlib import Path
from sanic.response import raw

# app = Sanic("res")
# swagger_blueprint.url_prefix = "/api"
# app.blueprint(swagger_blueprint)
from ds4biz_time_series.business.form_model import get_form
from ds4biz_time_series.config.AppConfig import REPO_PATH
from ds4biz_time_series.dao.fs_dao import JSONFSDAO
from ds4biz_time_series.model.services_model import FitServiceArgs, PredictServiceArgs, EvaluateServiceArgs
from ds4biz_time_series.utils.core_utils import load_pipeline
from ds4biz_time_series.utils.data_utils import preprocessing_data
from ds4biz_time_series.utils.factory_utils import get_factory
from ds4biz_time_series.utils.logger_utils import logger
from ds4biz_time_series.utils.ppom_utils import get_pom_major_minor
from sanic.exceptions import SanicException, NotFound

import sanic

from ds4biz_time_series.utils.service_utils import check_predictor_existence, load_params, check_existence, train_model, \
    get_prediction, get_model_evaluation
from ds4biz_time_series.utils.serialization_utils import serialize, deserialize
from ds4biz_time_series.utils.service_utils import get_all
from ds4biz_time_series.utils.zip_utils import make_zipfile, import_zipfile

from loko_extensions.business.decorators import extract_value_args

repo_path = Path(REPO_PATH)


def get_app(name):
    app = Sanic(name)
    swagger_blueprint.url_prefix = "/api"
    app.blueprint(swagger_blueprint)
    return app


name = "time_series"
app = get_app(name)
# url_prefix=f"ds4biz/time_series/{get_pom_major_minor()}")
bp = Blueprint("default")
app.config["API_VERSION"] = get_pom_major_minor()
app.config["API_TITLE"] = name
# app.config["REQUEST_MAX_SIZE"] = 20000000000 ## POI TOGLIERE!!
CORS(app)
app.static("/web", "/frontend/dist")

# @bp.post("/")
# def test(request):
#     print("ciao")
#     args = request.json.get('args')
#     print("ARGS",args)
#     json = request.json.get("value")
#     print("JSON",json)
#     return sanic.json(dict(msg="Hello extensions!"))
#
#
# @bp.post("/files")
# def test2(request):
#     file = request.files['file']
#     fname = file.filename
#     print("You have uploaded a file called:",fname)
#     return sanic.json(dict(msg=f"Hello extensions, you have uploaded the file: {fname}!"))


### UTILS ###
@app.post("/utils/forms")
@doc.tag('utils')
@doc.consumes(doc.JsonBody({}), location="body")
async def forms(request):
    res = get_form(request.json)
    res = FormsEncoder().encode(res)
    logger.debug(f'form: {res}')
    return sanic.json(json.loads(res))


#
# @bp.get("/utils/algorithms")
# @doc.tag('utils')
# @doc.summary('Get available forms')
# @doc.consumes(doc.Boolean(name="predict_proba"), location="query")
# @doc.consumes(doc.Boolean(name="partial"), location="query")
# @doc.consumes(doc.String(name="framework", choices=list(IMGS_MAPPING.keys())), location="query")
# @doc.consumes(doc.String(name="task", choices=sorted(tasks)), location="query")
# async def algorithms(request):
#     dparams = dict(task=None, framework=None, partial=False, predict_proba=False)
#     params = {**dparams, **load_params(request.args)}
#     framework = [params['framework']] if params['framework'] else IMGS_MAPPING.keys()
#     del params['framework']
#     res = []
#     for img_name in framework:
#         try:
#             resp = base_request(img_name, 'utils/algorithms', 'GET', **params)
#             res += resp.json()
#             for r in resp.json():
#                 base_request(img_name, 'utils/forms', 'POST', body=json.dumps(r))
#         except:
#             logger.debug('TracebackERROR: \n' + traceback.format_exc() + '\n\n')
#         kill_base(img_name)
#     return sanic.json(res)
### TRANSFORMERS ###

@bp.get("/transformers")
@doc.tag('transformers')
@doc.summary("List objects in 'transformers'")
async def list_transformers(request):
    print("si")
    res = get_all('transformers')
    # save_defaults(repo='transformers')
    return sanic.json(res)


@bp.post("/transformers/<name>")
@doc.tag('transformers')
@doc.summary("Save an object in 'transformers'")
@doc.description('''
    Examples
    --------
    Example 1: 
    obj = {
      "__klass__": "sktime.transformations.compose.TransformerPipeline",
      "steps": [
         {
          "__klass__": "sktime.transformations.series.exponent.ExponentTransformer",
          "power":2
        }
      ]
    }
    ~~~~~~~~~
    Example 2: 
    obj = {
      "__klass__": "sktime.transformations.compose.TransformerPipeline",
      "steps": [
        {
          "__klass__": "sktime.transformations.series.detrend.Deseasonalizer",
          "model": "multiplicative",
          "sp": 12
        },
         {
          "__klass__": "sktime.transformations.series.detrend.Deseasonalizer",
          "model": "additive",
          "sp": 3
        }
      ]
    }
    --------
                  ''')
@doc.consumes(doc.JsonBody({}), location="body")
@doc.consumes(doc.String(name="name"), location="path", required=True)
async def create_transformer(request, name):
    name = unquote(name)

    if not re.search(r'(?i)^[a-z0-9]([a-z0-9_]*[a-z0-9])?$', name):
        raise SanicException('No special characters (except _ in the middle of name) and whitespaces allowed',
                             status_code=400)
    path = repo_path / 'transformers' / name
    path.mkdir(exist_ok=True, parents=True)
    serialize(path, request.json)

    return sanic.json(f"Transformer '{name}' saved")


@bp.get("/transformers/<name>")
@doc.tag('transformers')
@doc.summary("Display object info from 'transformers'")
@doc.consumes(doc.String(name="name"), location="path", required=True)
async def transformers_info(request, name):
    name = unquote(name)

    path = repo_path / 'transformers' / name
    if not path.exists():
        raise SanicException(f"Tranformer '{name}' does not exist!", status_code=400)
    return sanic.json(deserialize(path))


@bp.delete("/transformers/<name>")
@doc.tag('transformers')
@doc.summary("Delete an object from 'transformers'")
@doc.consumes(doc.String(name="name"), location="path", required=True)
async def delete_transformer(request, name):
    name = unquote(name)
    path = repo_path / 'transformers' / name
    if not path.exists():
        raise SanicException(f"Tranformer '{name}' does not exist!", status_code=400)
    shutil.rmtree(path)
    return sanic.json(f"Transformer '{name}' deleted")




### MODELS ###

@bp.get("/models")
@doc.tag('models')
@doc.summary("List objects in 'models'")
async def list_models(request):
    # save_defaults(repo='models')
    return sanic.json(get_all('models'))


@bp.post("/models/<name>")
@doc.tag('models')
@doc.summary("Save an object in 'models'")
@doc.description('''
    Examples
    --------
    obj = {"__klass__": "skt.ARIMA"}
    obj = {"__klass__": "skt.NaiveForecaster",
            "strategy": "mean"
            "window_lenght"=12
            "sp"=3}
           ''')
@doc.consumes(doc.JsonBody({}), location="body")
@doc.consumes(doc.String(name="name"), location="path", required=True)
async def create_model(request, name):
    name = unquote(name)

    if not re.search(r'(?i)^[a-z0-9]([a-z0-9_]*[a-z0-9])?$', name):
        raise SanicException('No special characters (except _ in the middle of name) and whitespaces allowed',
                             status_code=400)

    path = repo_path / 'models' / name
    path.mkdir(exist_ok=True, parents=True)
    serialize(path, request.json)
    return sanic.json(f"Model '{name}' saved")


@bp.get("/models/<name>")
@doc.tag('models')
@doc.summary("Display object info from 'models'")
@doc.consumes(doc.String(name="name"), location="path", required=True)
async def models_info(request, name):
    name = unquote(name)

    path = repo_path / 'models' / name
    if not path.exists():
        raise SanicException(f"Model '{name}' does not exist!", status_code=400)
    return sanic.json(deserialize(path))


@bp.delete("/models/<name>")
@doc.tag('models')
@doc.summary("Delete an object from 'models'")
@doc.consumes(doc.String(name="name"), location="path", required=True)
async def delete_model(request, name):
    name = unquote(name)

    path = repo_path / 'models' / name
    if not path.exists():
        raise SanicException(f"Model '{name}' does not exist!", status_code=400)
    shutil.rmtree(path)
    return sanic.json(f'Model "{name}" deleted')


### PREDICTORS ###

@bp.get("/predictors")
@doc.tag('predictors')
@doc.summary("List objects in 'predictors'")
@doc.consumes(doc.Boolean(name='info'))
async def list_predictors(request):
    predictors = get_all('predictors')
    if not request.args.get('info', False):
        return sanic.json(predictors)
    res = []
    for name in predictors:
        try:
            res_tmp = dict(name=name)
            predictor_path = repo_path / 'predictors' / name
            infos = deserialize(predictor_path)
            dao = JSONFSDAO(predictor_path / 'history')
            infos['history'] = len(dao.all())
            #### TODO: aggiungere vere info
            # res_tmp.update(predictor_details(infos, name, 'development', fitting.all(status='alive'), repo_path))
            res.append(res_tmp)
        except:
            logger.debug('TracebackERROR: \n' + traceback.format_exc() + '\n\n')

    return sanic.json(res)


@bp.post("/predictors/<name>")
@doc.tag('predictors')
@doc.summary("Save an object in 'predictors'")
@doc.description('''
<b>model_id:</b> choose one model (see <b>POST /models/{name}</b>)
<b>transformer_id:</b> choose one transformer (see <b>POST /transformers/{name}</b>) or <i>"none"</i> ''')
@doc.consumes(doc.String(name="transformer_id"), location="query")
@doc.consumes(doc.String(name="model_id"), location="query")
@doc.consumes(doc.String(name="description"), location="query")
@doc.consumes(doc.String(name="name"), location="path", required=True)
async def create_predictor(request, name):
    name = unquote(name)

    if not re.search(r'(?i)^[a-z0-9]([a-z0-9_]*[a-z0-9])?$', name):
        raise SanicException('No special characters (except _ in the middle of name) and whitespaces allowed',
                             status_code=400)

    predictor_path = repo_path / 'predictors' / name

    if check_predictor_existence(predictor_path):
        raise SanicException(f"Predictor '{name}' already exists!", status_code=409)
    ### transformer ###
    transformer_id = request.args.get('transformer_id', 'auto')
    model_id = request.args.get('model_id', 'auto')
    blueprint = request.json
    ### blueprint ###
    if blueprint:
        if blueprint.get('transformer'):
            transf = blueprint['transformer']
            # check_blueprint(transf, step='transformer')
        if blueprint.get('model'):
            mod = blueprint['model']
            # check_blueprint(mod, step='model')
    else:
        if transformer_id == 'auto':
            # transformer = 'auto'
            raise NotImplementedError("Transformer auto not yet supported")
        elif transformer_id == 'none':
            # transformer = {"__klass__": "ds4biz.ct", "transformers": {}, "remainder": "passthrough"}
            raise SanicException("'none' transformer not yet implemented", status_code=501)
        else:
            tpath = repo_path / 'transformers' / transformer_id
            if not check_existence(tpath):
                raise SanicException(f"Transformer '{tpath.name}' doesn't exists!", status_code=404)
            transformer = deserialize(tpath)
        ### model ###
        if model_id == 'auto':
            # mod = 'auto'
            raise NotImplementedError("Model auto not yet supported")
        else:
            mpath = repo_path / 'models' / model_id
            if not check_existence(tpath):
                raise SanicException(f"Model '{mpath.name}' doesn't exists!", status_code=404)
            mod = deserialize(mpath)


    predictor_path.mkdir(exist_ok=True, parents=True)
    predictor_blueprint = dict(id=name,
                               description=request.args.get('description', ''),
                               created_on=time.time() * 1000,
                               # img=request.args.get('img', 'predictor_base'),
                               steps=dict(transformer=transformer, model=mod))
    serialize(predictor_path, predictor_blueprint)
    return sanic.json(f"Predictor '{name}' saved")


@bp.get("/predictors/<name>")
@doc.tag('predictors')
@doc.summary("Display object info from 'predictors'")
@doc.description("""
<b>name:</b> predictor id (see <b>GET /predictors</b>)
<b>details:</b> set to True to get more info
<b>branch:</b> development or master (see /predictors/{name}/release</b>)""")
# @doc.consumes(doc.String(name="branch", choices=['development', 'master']), location="query")
@doc.consumes(doc.Boolean(name="details"), location="query")
@doc.consumes(doc.String(name="name"), location="path", required=True)
async def predictors_info(request, name):
    name = unquote(name)

    path = repo_path / 'predictors' / name
    if not path.exists():
        raise SanicException(f'Predictor "{name}" does not exist!', status_code=400)
    infos = deserialize(path)
    details = request.args.get('details', 'false').capitalize
    if not details:
        return sanic.json(infos['steps'])
    ########### todo: SVILUPPARE PARTE SOTTO#

    # branch = request.args.get('branch', 'development')
    # infos = predictor_details(infos, name, branch, fitting.jobs, repo_path)

    return sanic.json(infos)


@bp.delete("/predictors/<name>")
@doc.tag('predictors')
@doc.summary("Delete an object from 'predictor'")
@doc.consumes(doc.String(name="name"), location="path", required=True)
async def delete_predictor(request, name):
    name = unquote(name)

    path = repo_path / 'predictors' / name
    if not path.exists():
        raise SanicException(f'Predictor "{name}" does not exist!', status_code=400)
    # ##TODO: sviluppare questa parte
    # if name in fitting.all('alive'):
    #     dc = fitting.get_by_id(name)['dc']
    #     cd.kill(dc.name)
    #     msg = 'Killed'
    #     fitting.add(name, msg)
    #     send_message(name, msg)
    #     fitting.remove(name)
    #     logger.debug(f'Fitting {name} Killed')
    # else:
    #     cname = list(filter(lambda x: x.endswith('_'+name), cd.containers.keys()))
    #     if cname:
    #         cd.kill(cname[0])
    #         logger.debug(f'Container {cname[0]} Killed')

    shutil.rmtree(path)

    # testset_dao = get_dataset_dao(repo_path=repo_path)
    # testset_dao.set_coll(name)
    # testset_dao.dropcoll()
    # testset_dao.close()

    return sanic.json(f"Predictor '{name}' deleted")


@bp.post("/predictors/<name>/fit")
@doc.tag('predictors')
@doc.summary('Fit an existing predictor')
@doc.description('''
    Examples
    --------
    data = {"data":[{"Date_Time": "01/03/2010  08:20:40" },
                    {"Date_Time": "01/10/2010  08:20:40"},
                    {"Date_Time": "01/17/2010  08:20:40"},
                    {"Date_Time": "01/24/2010  08:20:40"},
                    {"Date_Time": "01/31/2010  08:20:40"},
                    {"Date_Time": "02/07/2010  08:20:40"},
                    {"Date_Time": "02/14/2010  08:20:40"},
                    {"Date_Time": "02/21/2010  08:20:40"},
                    {"Date_Time": "02/28/2010  08:20:40"},
                    {"Date_Time": "03/07/2010  08:20:40"},
                    {"Date_Time": "03/14/2010  08:20:40"},
                    {"Date_Time": "03/21/2010  08:20:40"}],
     "target":[1509634,1581344, 1614204, 1897725, 1759063,1320022, 1559063, 1659063, 1859063, 1551083, 1819012, 1801029]}
    ...................
               ''')
# @doc.consumes(doc.String(name="fit_params"), location="query")
@doc.consumes(doc.JsonBody({'data': doc.List(doc.Dictionary), 'target': doc.List()}), location="body", required=True)
# @doc.consumes(doc.Integer(name="cv"), location="query")
# @doc.consumes(doc.Boolean(name="partial"), location="query")
@doc.consumes(doc.Float(name="test_size"), location="query")
@doc.consumes(doc.Boolean(name="report"), location="query")
@doc.consumes(doc.String(name="task", choices=['forecasting']), location="query",
              required=True)  # 'classification', 'none'
@doc.consumes(doc.Integer(name="forecasting_horizon"), location="query", required=False)
@doc.consumes(doc.String(name="datetime_feature"), location="query", required=True)
# @doc.consumes(doc.String(name="datetime_frequency", choices=["Years", "Months", "Days", "hours", "minutes", "seconds"]),
#               required=True)
@doc.consumes(doc.String(name="datetime_frequency"),
              required=True)
@doc.consumes(doc.String(name="name"), location="path", required=True)
async def fit(request, name):
    predictor_name = unquote(name)
    fit_params = request.args
    data = request.json
    try:
        train_model(predictor_name, fit_params=fit_params, data=data)
    except Exception as e:
        print("Error::::::: ", e)
        raise e
    return sanic.json(f"Predictor '{predictor_name}' correctly fitted")


@bp.post("/predictors/<name>/predict")
@doc.tag('predictors')
@doc.summary('Use an existing predictor to predict data')
@doc.consumes(doc.JsonBody({'data': doc.List(doc.Dictionary)}), location="body", required=False)
@doc.consumes(doc.Integer(name="forecasting_horizon"), location="query", required=False)
@doc.consumes(doc.String(name="name"), location="path", required=True)
async def predict(request, name):
    predictor_name = unquote(name)
    branch = "development"  # todo: aggiungere a fit e predict parametro branch
    predict_params = {**load_params(request.args)}
    data = request.json
    preds = get_prediction(predictor_name=predictor_name, predict_params=predict_params, branch=branch, data=data)
    return sanic.json(preds)


@bp.post("/predictors/<name>/evaluate")
@doc.tag('predictors')
@doc.summary('Evaluate existing predictors in history')
@doc.consumes(doc.JsonBody({'data': doc.List(doc.Dictionary), 'target': doc.List()}), location="body")
# @doc.consumes(doc.JsonBody({}), location="body", required=False)
# @doc.consumes(doc.Integer(name="forecasting_horizon"), location="query", required=False)
@doc.consumes(doc.String(name="name"), location="path", required=True)
async def evaluate(request, name):
    branch = "development"
    # params = {**load_params(request.args)}
    params = dict()
    params["branch"] = branch
    name = unquote(name)
    body = request.json

    logger.debug("loading predictor pipeline...")
    pipeline = load_pipeline(name, params['branch'], repo_path=repo_path)
    datetime = pipeline.date.strftime('%Y-%m-%d %H:%M:%S.%f')

    logger.debug("pre-processing evaluation data...")
    # y = FACTORY(body['target'])
    try:
        data = preprocessing_data(body, datetime_feature=pipeline.datetime_feature,
                                  datetime_frequency=pipeline.datetime_frequency)
    except Exception as e:
        print(f'----------------------{e}')
    y = data["y"]
    X = data["X"]

    logger.debug("computing forecast report")
    report = pipeline.get_forecast_report(y=y, X=X)
    logger.debug(f"report: {report}")
    res = [{"report_test": report, "datetime": datetime,
            "task": "forecast"}]
    print("res:::", res)
    return sanic.json(res)


@bp.post("/predictors/import")
@doc.tag('predictors')
@doc.summary('Upload existing predictor')
@doc.consumes(doc.File(name="f"), location="formData", content_type="multipart/form-data", required=True)
async def import_predictor(request):
    path = repo_path / 'predictors'
    file = request.files.get('f')
    if file.name.endswith('.zip'):
        import_zipfile(file, path)
    else:
        raise Exception("Error")
    return sanic.json('Predictor correctly imported')


@bp.get("/predictors/<name>/export")
@doc.tag('predictors')
@doc.summary('Download existing predictor')
@doc.consumes(doc.String(name="name"), location="path", required=True)
async def export_predictor(request, name):
    name = unquote(name)

    file_name = name + '.zip'
    path = repo_path / 'predictors' / name
    buffer = io.BytesIO()
    make_zipfile(buffer, path)
    buffer.seek(0)
    headers = {'Content-Disposition': 'attachment; filename="{}"'.format(file_name)}
    return raw(buffer.getvalue(), headers=headers)


##### LOKO SERVICES ########


@bp.post("/loko-services/datasets")
@doc.tag('loko-services')
@doc.summary("Get SkTime datasets")
@doc.consumes(doc.JsonBody({}), location="body")
@extract_value_args(file=False)
async def loko_get_dataset_service(value, args):
    logger.debug(f"fit::: value: {value}  \n \n args: {args}")

    logger.debug("si ci siamo")
    df_name = args.get("dataset", "load_airline")
    logger.debug(f"df:: {df_name}")
    df_module = "sktime.datasets."

    df_fact = dict(__klass__=df_module+df_name)
    logger.debug(f"df fact {df_fact}")
    res = get_factory(df_fact)
    # res = value
    # logger.debug(f"res {res}")
    try:
        return sanic.json(res)
    except Exception as e:
        logger.error(f"error::: {e}")
        raise SanicException(f"error::: {e}", status_code=500)



@bp.post("/loko-services/predictors/fit")
@doc.tag('loko-services')
@doc.summary("...")
@doc.consumes(doc.JsonBody({}), location="body")
@extract_value_args(file=False)
async def loko_fit_service(value, args):
    logger.debug(f"fit::: value: {value}  \n \n args: {args}")
    predictor_name = args["predictor_name"]
    logger.debug(f"pred: {predictor_name}")
    fit_params = FitServiceArgs(**args)
    if not (fit_params.datetime_frequency and fit_params.datetime_feature):
        msg = f"Date-time frequency value is '{fit_params.datetime_frequency}', Date-Time feature value is '{fit_params.datetime_feature}'. Both values need to be specified..."
        logger.error(msg)
        raise SanicException(msg, status_code=400)
    logger.debug("-------------------------------------")
    try:
        train_model(predictor_name, fit_params=fit_params.to_dict(), data=value)
    except Exception as e:
        logger.error(f"Fitting LOG Error... {e}")
        raise SanicException(f"Fitting LOG Error... {e}", status_code=500)
    res = f"Predictor '{predictor_name}' correctly fitted"
    # res = get_all('transformers')
    # save_defaults(repo='transformers')
    return sanic.json(res)





@bp.post("/loko-services/predictors/predict")
@doc.tag('loko-services')
@doc.summary("Use an existing predictor to predict data")
@extract_value_args(file=False)
async def loko_predict_service(value, args):
    logger.debug(f"predict::: value: {value}  \n \n args: {args}")
    if isinstance(value, str):
        value = None
    branch = "development"
    predictor_name = args["predictor_name"]

    logger.debug(f"pred: {predictor_name}")
    predict_params = PredictServiceArgs(**args).to_dict()
    logger.debug(f"predict_params: {predict_params}")
    # print("si")
    # res = get_all('transformers')
    # save_defaults(repo='transformers')
    try:
        res = get_prediction(predictor_name, predict_params, branch=branch, data=value)
    except Exception as e:
        logger.error(f"Prediction LOG err {e}")
        raise e
    return sanic.json(res)


@bp.post("/loko-services/predictors/evaluate")
@doc.tag('loko-services')
@doc.summary("...")
@doc.consumes(doc.JsonBody({}), location="body")
@extract_value_args(file=False)
async def loko_evaluate_service(value, args):
    logger.debug(f"evaluate::: value: {value}  \n \n args: {args}")

    branch = "development"
    # params = {**load_params(request.args)}
    predictor_name = unquote(args["predictor_name"])
    logger.debug(f"pred: {predictor_name}")
    eval_params = EvaluateServiceArgs(**args).to_dict()

    try:
        eval_res = get_model_evaluation(predictor_name=predictor_name, branch=branch, evaluate_params=eval_params,
                                        data=value)
    except Exception as e:
        logger.error(f"Evaluate LOG err: {e}")
        raise SanicException(f"Evaluate LOG Error... {e}")
    return sanic.json(eval_res)

#
# @bp.delete("/loko-service/transformers")
# @doc.tag('loko-services')
# @doc.summary("Delete an object from 'transformers' - service compatible with loko;")
# @extract_value_args(file=False)
# async def loko_delete_transformer(value, args):
#     transformer_name = args.get("del_transformer", None)
#     if not transformer_name:
#         raise SanicException("Transformer name not specified...")
#     transformer_name = unquote(transformer_name)
#     path = repo_path / 'transformers' / transformer_name
#     if not path.exists():
#         raise SanicException(f"Tranformer '{transformer_name}' does not exist!", status_code=400)
#     shutil.rmtree(path)
#     return sanic.json(f"Transformer '{transformer_name}' deleted")
#


#
# @bp.delete("/loko-service/models")
# @doc.tag('loko_service')
# @doc.summary("Delete an object from 'models' - service compatible with loko;")
# @extract_value_args(file=False)
# async def loko_delete_model(value, args):
#     model_name = args.get("del_model", None)
#     if not model_name:
#         raise SanicException("Model name not specified...")
#
#     model_name = unquote(model_name)
#
#     path = repo_path / 'models' / model_name
#     if not path.exists():
#         raise SanicException(f"Model '{model_name}' does not exist!", status_code=400)
#     shutil.rmtree(path)
#     return sanic.json(f'Model "{model_name}" deleted')


#
# @bp.delete("/loko_service/predictors")
# @doc.tag('loko_service')
# @doc.summary("Delete an object from 'predictor'- service compatible with loko;")
# @doc.consumes(doc.String(name="name"), location="path", required=True)
# @extract_value_args(file=False)
# async def loko_delete_predictor(value, args):
#     predictor_name = args.get("del_model", None)
#     if not predictor_name:
#         raise SanicException("Predictor name not specified...")
#
#     predictor_name = unquote(predictor_name)
#
#     path = repo_path / 'predictors' / predictor_name
#     if not path.exists():
#         raise SanicException(f'Predictor "{predictor_name}" does not exist!', status_code=400)
#     # ##TODO: sviluppare questa parte
#     # if name in fitting.all('alive'):
#     #     dc = fitting.get_by_id(name)['dc']
#     #     cd.kill(dc.name)
#     #     msg = 'Killed'
#     #     fitting.add(name, msg)
#     #     send_message(name, msg)
#     #     fitting.remove(name)
#     #     logger.debug(f'Fitting {name} Killed')
#     # else:
#     #     cname = list(filter(lambda x: x.endswith('_'+name), cd.containers.keys()))
#     #     if cname:
#     #         cd.kill(cname[0])
#     #         logger.debug(f'Container {cname[0]} Killed')
#
#     shutil.rmtree(path)
#
#     # testset_dao = get_dataset_dao(repo_path=repo_path)
#     # testset_dao.set_coll(name)
#     # testset_dao.dropcoll()
#     # testset_dao.close()
#
#     return sanic.json(f"Predictor '{predictor_name}' deleted")
#

@bp.post("/loko-services/delete_predictors_objs")
@doc.tag('loko-services')
@doc.summary("Delete an object from 'models', 'transformer' and/or 'predictor' - service compatible with loko;")
@extract_value_args(file=False)
async def loko_delete_predictor_objs(value, args):
    model_name = args.get("del_model", None)
    if not model_name:
        raise SanicException("Model name not specified...", status_code=400)

    model_name = unquote(model_name)

    path = repo_path / 'models' / model_name
    if not path.exists():
        raise SanicException(f"Model '{model_name}' does not exist!", status_code=404)
    shutil.rmtree(path)
    return sanic.json(f'Model "{model_name}" deleted')





@app.exception(Exception)
async def manage_exception(request, exception):
    status_code = getattr(exception, "status_code", None) or 500
    if isinstance(exception, SanicException):
        return sanic.json(dict(error=str(exception)), status=status_code)

    e = dict(error=f"{exception.__class__.__name__}: {exception}")

    if isinstance(exception, NotFound):
        return sanic.json(e, status=404)
    # logger.error(f"status code {status_code}")
    logger.error('TracebackERROR: \n' + traceback.format_exc() + '\n\n', exc_info=True)
    return sanic.json(e, status=status_code)




app.blueprint(bp)

app.run("0.0.0.0", port=8080, auto_reload=False)
