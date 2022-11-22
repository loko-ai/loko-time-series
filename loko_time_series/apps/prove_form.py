import ast
import re
import sys
from typing import List

from loko_time_series.business.form_model import ModelForm
from loko_time_series.model.doc_form_models import DocForm
from loko_time_series.utils.factory_utils import get_factory



# def guess_convert(s):
#     if s is None:
#         return None
#     try:
#         value = ast.literal_eval(s)
#     except Exception:
#         return s
#     else:
#         return value
#
#
# def clean_type(type: str):
#     ##lista graffe
#     select_t = []
#     if "{" in type:
#         for graf in re.findall('(?={).*(?<=})', type):
#             g = guess_convert(graf)
#             if isinstance(g, set):
#                 select_t.append(list(g))
#         type = re.sub('{.*}', '', type)
#     sp = re.split("or|,", "".join(type.split()))
#     ret = [str(set(el)) for el in select_t]
#     ret += [t for t in sp if t]
#     return ret
#
#
# def get_single_parameter(s: str):
#     name_s = re.search('[a-z_0-9]+(?= : )', s)
#     name = name_s.group() if name_s else ''
#     type_s = re.search('(?<= : ).*(?=,)', s)
#     type = type_s.group() if type_s else ''
#     types_cleaned = clean_type(type)
#     default_s = re.search('(?<=default=).*(?=\n)', s)
#     default = default_s.group() if default_s else ''
#     default = guess_convert(default)
#     description_s = re.search('(?<=        ).*', s)
#     description = s[description_s.start():] if description_s else ''
#     description = re.sub('\n[ ]+', '\n', description)
#     description = re.sub('^[ ]+', '', description)
#     return dict(name=name, types=types_cleaned, default=default, description=description)
#
#
#
# def get_default_doc(algorithm_path):
#     doc_form = DocForm()
#     print(algorithm_path)
#
#     kl = dict(__klass__=algorithm_path)
#     kl_inst = get_factory(kl)
#     doc = kl_inst.__doc__
#
#     parameters_start = re.search('Parameters', doc)
#     parameters_start_s, parameters_start_e = parameters_start.start(), parameters_start.end()
#     parameters_end = re.search('Attributes', doc)
#     if not parameters_end:
#         parameters_end = re.search('Examples', doc)
#     parameters_end_s, parameters_end_e = parameters_end.start(), parameters_end.end()
#
#     doc_form.description = re.sub('\n[ ]+', '\n', doc[: parameters_start_s])
#     # repr(ret[:parameters_start_s])
#
#     s = doc[parameters_start_e:parameters_end_s]
#     while (len(s) > 0):
#         r = '[a-z_0-9]+ : '
#         param_start = re.search(r, s)
#         param_end = re.search(r, s[param_start.end():])
#         param_start_s, param_start_e = param_start.start(), param_start.end()
#         if param_end:
#             param_end_s, param_end_e = param_start_e + param_end.start(), param_start_e + param_end.end()
#             # print('END:', repr(s[(param_end_s - 10):(param_end_e + 10)]))
#             param_string = s[param_start_s:param_end_s]
#             s = s[param_end_s:]
#         else:
#             param_string = s[param_start_s:]
#             s = ''
#         res = get_single_parameter(param_string)
#         doc_form.params.append(res)
#
#     return doc


from sktime.transformations.panel.rocket import Rocket

from sktime.forecasting.arima import ARIMA
# print(Rocket.__doc__)

# el = get_factory("sktime.transformations.panel.rocket.Rocket")
from loko_time_series.utils.form_utils import get_default_doc

# kl = dict(__klass__="sktime.transformations.panel.rocket.Rocket")
el = dict(__klass__="sklearn.ensemble.RandomForestClassifier")
# kl = dict(__klass__="sktime.forecasting.arima.ARIMA")

#
# print(el.__doc__)


kl = get_factory(el)
kl_dict = kl.__dict__
doc = kl.__doc__
# res = res.__dict__
# name = obj['__klass__'].split('.')[1]


info = get_default_doc(doc)
### filtriamo parametri ###
info['params'] = [dict(name=params['name'],
                       types=params['types'],
                       description=params['description'],
                       default=kl_dict[params['name']]) for params in info['params'] if params['name'] in kl_dict]

# print(info)

form = ModelForm(el.get("__klass__"))
print("FOOOOOOOOOOOOOORMMMMM-------------------------")
print(form)
