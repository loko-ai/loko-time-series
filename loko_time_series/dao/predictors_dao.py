import shutil
from pathlib import Path

from loko_time_series.config.AppConfig import REPO_PATH

repo = Path(REPO_PATH)

class PredictorDAOException(Exception):
    pass


class PredictorsDAO:

    def __init__(self, path=repo):
        self.path = Path(path)

    def save(self, predictor):
        return "saved"
        # try:
        #     p = self.path / pr.predictor_name
        #     p.mkdir(exist_ok=True)
        #     if pr.model_parameters is not None:
        #         with open(p / BLUEPRINT_FILENAME, 'w') as f:
        #             json.dump(pr.model_parameters, f, indent=2)
        #     else:
        #         models_info = dict(predictor_name=pr.predictor_name, pretrained_model=pr.pretained_model,
        #                            predictor_tag=pr.predictor_tag)
        #         with open(p / BLUEPRINT_FILENAME, 'w') as f:
        #             json.dump(models_info, f, indent=2)
        #
        #     joblib.dump(pr.model_obj, p / pr.predictor_name)
        # except Exception as inst:
        #     logger.exception(inst)
        #     raise PredictorDAOException("Can't save predictor")

    def delete(self, predictor_name):
        shutil.rmtree(self.path / predictor_name)

    def all(self):
        return self.path.glob('*')

    def get(self, predictor_name):
        res = "predictor"
        # try:
        #     with open(self.path / predictor_name / BLUEPRINT_FILENAME, 'r') as f:
        #         blueprint = json.load(f)
        #     # if "model_parameters" in blueprint.
        #     model_obj = joblib.load(self.path / predictor_name / predictor_name)
        #     with open(self.path / predictor_name / BLUEPRINT_FILENAME, 'r') as f:
        #         blueprint = json.load(f)
        #     model_parameters = blueprint.get("top_layer")
        #     # print("mod==========", model_parameters)
        #
        #     # print(blueprint)
        #     # print(model_parameters)
        #     if model_parameters is not None:
        #         # print("modelllllll ",model_parameters)
        #         res = PredictorRequest(predictor_name=blueprint[PREDICTOR_NAME_LBL],
        #                                pretained_model=blueprint[PRETRAINED_MODEL_LBL],
        #                                predictor_tag=blueprint.get(PREDICTOR_TAG_LBL, None),
        #                                model_obj=model_obj, model_parameters=model_parameters)
        #     else:
        #         res = PredictorRequest(predictor_name=blueprint[PREDICTOR_NAME_LBL],
        #                                pretained_model=blueprint[PRETRAINED_MODEL_LBL],
        #                                predictor_tag=blueprint.get(PREDICTOR_TAG_LBL, None),
        #                                )
        # except Exception as inst:
        #     print(inst)
        #     raise PredictorDAOException("Can't load predictor")
        return res
