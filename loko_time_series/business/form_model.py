from abc import abstractmethod
from typing import List

from loko_time_series.utils.factory_utils import get_factory
from loko_time_series.utils.form_utils import guess_convert, get_default_doc
from loko_time_series.utils.logger_utils import logger


class Form:

    def __init__(self, name=""):
        self.name = name
        self.description = ""
        self.args = []
        self.values = {}

    @abstractmethod
    def parse(self, x):
        raise Exception("Not implemented")


class ModelForm(Form):

    def parse(self, params: List):
        try:
            for el in params:
                field = dict()
                t = el.types[0]
                print(t, el.default)

                if "{" in t:
                    if isinstance(el.default, str):
                        el.default = el.default.replace("'", "")
                    ##lista graffe
                    options = list(guess_convert(t))
                    t = "select"

                if t == "bool":
                    field = dict(type="dynamic", parent="__klass__", dynamicType="boolean", name=el.name,
                                 label=el.name.title(),
                                 description=el.description)

                elif any([x in t for x in ["int", "double", "float"]]):
                    field = dict(type="dynamic", parent="__klass__", dynamicType="number",
                                 validation=dict(valueAsNumber=True),
                                 name=el.name,
                                 label=el.name.title(),
                                 description=el.description)
                elif t == "str":
                    if isinstance(el.default, str):
                        el.default = el.default.replace("'", "")
                    field = dict(type="dynamic", parent="__klass__", dynamicType="text", name=el.name,
                                 label=el.name.title(),
                                 description=el.description)

                elif t == "list":
                    field = dict(type="dynamic", parent="__klass__", dynamicType="multiKeyValue", name=el.name, fields=[dict(name="label")],
                                 label=el.name.title(),
                                 description=el.description)

                elif t == "set":
                    field = dict(type="dynamic", parent="__klass__", dynamicType="multiKeyValue", name=el.name,
                                 fields=[dict(name="label")],
                                 label=el.name.title(),
                                 description=el.description)

                elif t == "dict":
                    field = dict(type="dynamic", parent="__klass__", dynamicType="text", name=el.name,
                                 label=el.name.title(),
                                 description=el.description)
                elif t == "select":
                    field = dict(type="dynamic", parent="__klass__", dynamicType='select', options=options,
                                 name=el.name,
                                 label=el.name.title(),
                                 description=el.description)
                else:
                    field = dict(type="dynamic", parent="__klass__", dynamicType="text", name=el.name,
                                 label=el.name.title(),
                                 description=el.description)
                    el.default = None

                if el.default:

                    if t == "list" or t == "set":
                        elements = guess_convert(el.default)
                        self.values[el.name] = [dict(label=x, id=i) for i,x in enumerate(elements)]
                    else:
                        self.values[el.name] = el.default

                else:
                    if any([x in t for x in ["int", "double", "float"]]):
                        self.values[el.name] = None
                    else:
                        self.values[el.name] = ""

                if field:
                    self.args.append(field)

                else:
                    logger.debug(f"unrecognized type {el.type}, param name {el.name}")
                    self.args.append(
                        dict(type="dynamic", parent="__klass__", dynamicType="text", name=el.name,
                             label=el.name.title(),
                             description=el.description))
        except Exception as inst:
            logger.exception(inst)



def get_form(obj):


    kl = get_factory(obj)
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

    form = ModelForm(obj.get("__klass__"))

    # r = ObjectDict(info)
    # form.description = r.description
    # params = [ObjectDict(el) for el in r.params]
    # form.parse(params)
    return form.__dict__



if __name__ == '__main__':
    from _collections import defaultdict


    class ObjectDict(defaultdict):

        def __init__(self, mapping=None):
            if mapping:
                defaultdict.__init__(self, ObjectDict, ObjectDict.convert(mapping))
            else:
                defaultdict.__init__(self, ObjectDict)

        def __setattr__(self, k, v):
            self[k] = ObjectDict.convert(v)

        def __getattr__(self, k):
            return self[k]

        @classmethod
        def convert(cls, obj):
            if type(obj) is dict:
                ret = ObjectDict()
                for k, v in obj.items():
                    ret[k] = ObjectDict.convert(v)
                return ret
            elif type(obj) is list:
                return [ObjectDict.convert(x) for x in obj]
            else:
                return obj


    a = ObjectDict([{"ciao": 1, "casa": [1, 2, 3]}, {"ciao":"be", "casa": [1, 2, 2]}, {"ciao":"jshdgd", "casa": [1, 1, 1]}])
    print(a.casa)