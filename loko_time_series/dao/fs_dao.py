import json
import os
from pathlib import Path

# from ds4biz_predictor_core.utils.history_utils import history_parse, History
#

class FileSystemDAO:

    def __init__(self, path, history=False, **kwargs):
        if not isinstance(path, Path):
            path = Path(path)
        self.path = path
        # self.history = history

    def save(self):
        raise Exception("not implemented")

    def update(self):
        raise Exception("not implemented")

    def all(self, files=True):
        if files:
            lista = []
            for root, dirs, files in os.walk(self.path):
                for file in files:
                    lista.append(os.path.join(root,file))
            # if self.history:
            #     return history_parse(lista)
            return lista
        if os.path.exists(self.path):

            return os.listdir(self.path)

        return []

    def get_by_id(self):
        raise Exception("not implemented")

    def remove(self):
        raise Exception("not implemented")

class JSONFSDAO(FileSystemDAO):

    def __init__(self, *args,**kwargs):
        self.date = kwargs.get('date')
        self.time = kwargs.get('time') or self.date
        super().__init__(*args,**kwargs)

    def save(self,d, name):
        os.makedirs(self.path, exist_ok=True)
        # if self.history:
        #     h = History(date=self.date, time=self.time)
        #
        #     name = h.historify(name)
        #     d.update(h.json())
        #     del h
        with open(self.path/name, "w") as file:
            json.dump(d,file, indent=2)

    def get_by_id(self, name):
        with open(name, "r") as file:
            return json.load(file)