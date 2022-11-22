import ast
import re
from typing import List

from loko_time_series.model.doc_form_models import DocForm
from loko_time_series.utils.factory_utils import get_factory

def guess_convert(s):
    if s is None:
        return None
    try:
        value = ast.literal_eval(s)
    except Exception:
        return s
    else:
        return value


def clean_type(type: str):
    ##lista graffe
    select_t = []
    if "{" in type:
        for graf in re.findall('(?={).*(?<=})', type):
            g = guess_convert(graf)
            if isinstance(g, set):
                select_t.append(list(g))
        type = re.sub('{.*}', '', type)
    sp = re.split("or|,", "".join(type.split()))
    ret = [str(set(el)) for el in select_t]
    ret += [t for t in sp if t]
    return ret


def get_single_parameter(s: str):
    name_s = re.search('[a-z_0-9 ]+(?= : )', s)
    name = name_s.group().strip(" ") if name_s else ''
    type_match = '(?<= : ).*(?=( \\(| (?<=[^\\(]),|, )+)'
    type_s = re.search(type_match, s)
    type = type_s.group() if type_s else ''
    types_cleaned = clean_type(type)
    if isinstance(types_cleaned, list):
        waste = types_cleaned[1:]
        types_cleaned = types_cleaned[0]
    default_match = "(?<=(default)[=| ]).*(?=(\\)|\\)\n|(?<=[^)])\n)+)"
    default_s = re.search(default_match, s)
    default = default_s.group() if default_s else ''
    default = guess_convert(default)
    # old_description_match='(?<=        ).*'
    # right_description_match = '(((?<=        )|, | \()+)(.|\n.|\r.|\t.|\n[ ].)*'

    description_match = '(((?<=        )|, | \\()+)(.|\n.|\r.|\t.)*'
    description_s = re.search(description_match, s)
    description = s[description_s.start():] if description_s else ''
    description = re.sub('\n[ ]+', '\n', description)
    description = re.sub('^[ ]+', '', description)
    return dict(name=name, types=types_cleaned, default=default, description=description)



def get_default_doc(doc):
    doc_form = DocForm()
    print(doc)
    # print(f"re::: {re.search('Parameters', doc)}")

    parameters_match = re.search('Parameters', doc)
    parameters_match_start, parameters_match_end = parameters_match.start(), parameters_match.end()
    attribute_match = re.search('Attributes', doc)
    if not attribute_match:
        examples_match = re.search('Examples', doc)
        if not examples_match:
            parameters_end = len(doc)-1
        else:
            parameters_end = examples_match.start()
    else:
        parameters_end = attribute_match.start()

    doc_form.description = re.sub('\n[ ]+', '\n', doc[: parameters_match_start])
    # repr(ret[:parameters_start_s])

    s = doc[parameters_match_start:parameters_end]
    while (len(s) > 0):
        r = '[a-z_0-9 ]+ : '
        param_match = re.search(r, s)
        next_param_match = re.search(r, s[param_match.end():])
        param_match_start, param_match_end = param_match.start(), param_match.end()
        if next_param_match:
            next_param_start, next_param_end = param_match_end + next_param_match.start(), param_match_end + next_param_match.end()
            # print('END:', repr(s[(param_end_s - 10):(param_end_e + 10)]))
            param_string = s[param_match_start:next_param_start]
            s = s[next_param_start:]
        else:
            param_string = s[param_match_start:]
            s = ''
        res = get_single_parameter(param_string)
        doc_form.params.append(res)

    return doc_form.__dict__
