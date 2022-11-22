import shutil
from pathlib import Path
from typing import List
import json
from urllib.parse import unquote

from sanic.exceptions import SanicException

from loko_time_series.business.training import training_pipeline
from loko_time_series.config.AppConfig import REPO_PATH, PREDICTOR_EVALUATE_FOLDER, EVALUATE_FILES_EXTENSION, \
    ORCHESTRATOR
from loko_time_series.dao.fs_dao import FileSystemDAO
from loko_time_series.utils.core_utils import load_pipeline
from loko_time_series.utils.data_utils import preprocessing_data
from loko_time_series.utils.files_utils import save_eval_file
from loko_time_series.utils.logger_utils import logger
from loko_time_series.utils.serialization_utils import deserialize, serialize

repo_path = Path(REPO_PATH)

def get_all(repo: str) -> List[str]:
    path = repo_path / repo
    fsdao = FileSystemDAO(path)
    return sorted(fsdao.all(files=False))


def check_predictor_existence(path:Path):
    if path.exists():
        return True
    else:
        return False

def check_existence(path:Path):
    if path.exists():
        return True
    else:
        return False


def load_params(params):
    res = dict()
    for k in params:
        v = params.get(k)
        if v == 'none':
            res[k] = None
        else:
            try:
                res[k] = json.loads(params.get(k))
            except:
                res[k] = params.get(k)
    return res

# def get_dataset(name):

def train_model(predictor_name, fit_params:dict, data:dict):
    predictor_path = repo_path / 'predictors' / predictor_name
    print("predictor: ", predictor_path)
    logger.debug(f"predictor{predictor_path}")
    if not check_predictor_existence(predictor_path) or predictor_name=="":
        raise SanicException(f"Predictor '{predictor_name}' doesn't exists", status_code=404)
    try:
        predictor_blueprint = deserialize(predictor_path)

    except FileNotFoundError as notfound:
        logger.error("predictor corrupt")
        raise SanicException(f"Predictor '{predictor_name}' doesn't exists or corrupt...", status_code=404)

    dparams = dict(test_size=.2,
                   forecasting_horizon=None,
                   datetime_frequency="s",
                   # partial=False,
                   fit_params=dict(),
                   # cv=0,
                   report=False,
                   # history_limit=0,
                   task='forecasting',
                   # save_dataset=False
                   )
    params = {**dparams, **load_params(fit_params)}
    params["datetime_frequency"] = params["datetime_frequency"]
    predictor_blueprint["datetime_feature"] = params["datetime_feature"]
    predictor_blueprint["datetime_frequency"] = params["datetime_frequency"]
    predictor_blueprint["status"] = "Training"
    serialize(predictor_path, predictor_blueprint)
    pred_blueprint_copy = predictor_blueprint.copy()
    data = data

    training_pipeline(predictor_path=predictor_path,predictor_blueprint=pred_blueprint_copy, data=data, **params)
    predictor_blueprint["status"] = "Fitted"
    # # predictor_blueprint["fitted"] = "Training"
    serialize(predictor_path, predictor_blueprint)
    logger.debug("training done...")

def get_prediction(predictor_name, predict_params:dict, branch:str="development",  data:dict=None):
    """
    It loads the pipeline, preprocesses the data, and then predicts

    :param predictor_name: the name of the predictor you want to use
    :param predict_params: a dictionary with the following keys:
    :type predict_params: dict
    :param branch: The branch of the predictor you want to use, defaults to development
    :type branch: str (optional)
    :param data: the data to be predicted
    :type data: dict
    :return: The prediction is being returned.
    """
    path = repo_path / 'predictors' / predictor_name
    logger.debug(f"name: {predictor_name}")
    if not check_predictor_existence:
        logger.debug(f"Predictor {predictor_name} doesn't exists")
        raise Exception(f"Predictor {predictor_name} doesn't exists")
    if path / branch not in list(path.glob('*')):
        logger.debug(f"path {path} + {branch} not found...")
        raise Exception(f'Predictor "{predictor_name}" is not fitted')
    pipeline = load_pipeline(predictor_name, branch, repo_path=repo_path)
    data = preprocessing_data(data, datetime_feature=pipeline.datetime_feature,
                              datetime_frequency=pipeline.datetime_frequency, get_only_X=True)
    logger.debug("data transformed...")
    logger.debug(f'forecast horizon {type(predict_params["forecasting_horizon"])}')
    try:
        preds = pipeline.predict(X=data["X"],
                                 horizon=predict_params["forecasting_horizon"])  # , include_probs=params['include_probs'])
    except Exception as e:
        print("eeeee", e)
        logger.debug(f"predict error {e}")
        raise e
    # if params['include_probs']:
    #     preds = [[[c,float(p)] for c,p in el] for el in preds]
    # else:
    #     preds = preds.tolist()

    return preds



def get_model_evaluation(predictor_name, branch, evaluate_params: dict=None, data:dict=None):

    logger.debug("loading predictor pipeline...")
    path = repo_path / 'predictors' / predictor_name

    if not check_predictor_existence:
        logger.debug(f"Predictor {predictor_name} doesn't exists")
        raise Exception(f"Predictor {predictor_name} doesn't exists")
    if path / branch not in list(path.glob('*')):
        logger.debug(f"path {path} + {branch} not found...")
        raise Exception(f'Predictor "{predictor_name}" is not fitted')
    pipeline = load_pipeline(predictor_name, branch, repo_path=repo_path)
    datetime = pipeline.date.strftime('%Y-%m-%d %H:%M:%S.%f')

    logger.debug("pre-processing evaluation data...")
    # y = FACTORY(body['target'])

    data = preprocessing_data(data, datetime_feature=pipeline.datetime_feature,
                                  datetime_frequency=pipeline.datetime_frequency)


    y = data["y"]
    X = data["X"]



    logger.debug("computing forecast report")
    report = pipeline.get_forecast_report(y=y, X=X)
    logger.debug(f"report: {report}")
    res = [{"results": report, "datetime": datetime,
            "task": "forecast"}]
    if evaluate_params["save_eval_report"]:
        save_eval_file(eval_fname=evaluate_params["eval_fname"], data=res[0])
    return res



def delete_model(model_name):
    if not model_name:
        raise SanicException("Model name not specified...", status_code=400)
    model_name = unquote(model_name)

    path = repo_path / 'models' / model_name
    if not path.exists():
        raise SanicException(f"Model '{model_name}' does not exist!", status_code=404)
    shutil.rmtree(path)
    return f'Model "{model_name}" deleted'



def delete_transformer(transformer_name):
    if not transformer_name:
        raise SanicException("Transformer name not specified...", status_code=400)
    transformer_name = unquote(transformer_name)
    path = repo_path / 'transformers' / transformer_name
    if not path.exists():
        raise SanicException(f"Tranformer '{transformer_name}' does not exist!", status_code=404)
    shutil.rmtree(path)
    return f"Transformer '{transformer_name}' deleted"

def delete_predictor(predictor_name):
    if not predictor_name:
        raise SanicException("Predictor name not specified...", status_code=400)
    predictor_name = unquote(predictor_name)

    path = repo_path / 'predictors' / predictor_name
    if not path.exists():
        raise SanicException(f'Predictor "{predictor_name}" does not exist!', status_code=404)
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

    return f"Predictor '{predictor_name}' deleted"

