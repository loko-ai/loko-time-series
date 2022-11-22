import os

import urllib
from abc import ABC
from collections import defaultdict
import time
from datetime import datetime
from functools import lru_cache
from pathlib import Path
import hashlib
from tempfile import NamedTemporaryFile
from typing import List
from urllib.parse import urlparse

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble._gradient_boosting import csr_matrix

from loko_time_series.business.ts_pipeline import TSPipeline
from loko_time_series.utils.factory_utils import get_factory
from loko_time_series.utils.history_utils import History
from loko_time_series.utils.logger_utils import logger
from loko_time_series.utils.serialization_utils import deserialize


class Status:
    """
    It takes a function as an argument, and returns a function that wraps the original function in a try/except block

    :param f: the function that we are decorating
    :return: A function
    """
    def __init__(self, fname, content):
        self.fname = fname
        self.content = content
        self.hash = hashlib.md5(str.encode(str(content))).hexdigest()

class Commit:
    def __init__(self, content: List[Status]):
        dt = datetime.now()
        h = hashlib.md5(str.encode(str(dt))).hexdigest()
        date = dt.strftime("%Y-%m-%d_%H-%M-%S")
        self.content = content
        self.date = date
        self.hash = h

class VersionControl(ABC):
    def __init__(self):
        pass

    def commit(self):
        pass

    def checkout(self):
        pass

    def tag(self):
        pass

    def push(self):
        pass

    def pull(self):
        pass


def lock_resource(f):
    def check(*args):
        try:
            for count in range(1000):
                self = args[0]
                if not os.path.exists(os.path.join(self.path, '.' + self.branch + '.lock')):
                    self.lock()
                    res = f(*args)
                    self.unlock()
                    break
                else:
                    logger.debug('Branch is locked, retry %s' % str(count + 1))
                    time.sleep(1)
            return res
        except Exception as e:
            import traceback
            logger.debug('FSystemERROR: \n' + traceback.format_exc() + '\n\n')
            self.unlock()

    return check


# It's a wrapper around a file system that allows you to save and load files, and to keep track of the history of the
# saved files
class FileSystemVC(VersionControl):

    def __init__(self, path: Path, history_limit=0, save_date=True):
        """
        This function initializes a new instance of the `FileHistory` class

        :param path: The path to the file you want to save to
        :type path: Path
        :param history_limit: The number of trained models to keep in the history. If set to 0, no history is kept, defaults to 0
        (optional)
        :param save_date: If True, the date will be appended to the filename, defaults to True (optional)
        """
        self.path = path
        self.branch = 'development'
        print("si")
        try:
            print(self.path / self.branch)
            (self.path / self.branch).mkdir(exist_ok=True)
        except Exception as e:
            print("ops")
        print("no")
        self.commits = defaultdict(list)
        self.branches = set([x.name for x in self.path.glob('*') if x.is_dir()])
        self.history_limit = history_limit
        self.save_date = save_date
        self.date = None

    def create_branch(self, branch):
        """
        It creates a branch.

        :param branch: The name of the branch to create
        """
        os.makedirs(os.path.join(self.path, branch), exist_ok=True)
        self.branches.add(branch)
        self.commits[branch] = self.commits[self.branch]
        self.checkout(branch)

    def status(self):
        p = os.path.join(self.path, self.branch)
        old_status = []
        for fname in os.listdir(p):
            old_status.append(Status(fname=fname, content=joblib.load(os.path.join(p, fname))))
        new_status = self.latest()
        old_status_dict = {el.fname: el for el in old_status}
        new_status_dict = {el.fname: el for el in new_status.content}
        res = []
        for fname in new_status_dict:
            new = new_status_dict[fname].__dict__
            old = old_status_dict[fname].__dict__ if fname in old_status_dict else {}
            if new != old:
                res.append(fname)
        return res

    def commit(self, status_list, date=None):
        self.date = date
        status_list = [Status(**status) for status in status_list]
        print("status:", status_list)
        self.commits[self.branch].append(Commit(status_list))

    def history(self):
        for commit in self.commits.get(self.branch, []):
            yield commit

    def merge(self, branch):
        self.commits[self.branch] = self.commits[branch][-1]

    def checkout(self, branch):
        # if self.branch in self.commits:
        #     raise Exception('Esistono commit non pushati!')
        print("bbb:", branch)
        if branch in self.branches:
            self.branch = branch
        else:
            raise Exception('Branch %s does not exist' % branch)

    def latest(self):
        res = list(self.history())
        if res:
            return res[-1]
        raise Exception('No commits in history')

    def save_history(self):
        dt = self.date or datetime.now()
        p = os.path.join(self.path, self.branch, '.history')
        os.makedirs(p, exist_ok=True)
        if self.history_limit:
            h = hashlib.md5(str.encode(str(dt))).hexdigest()
            date = dt.strftime("%Y-%m-%d_%H-%M-%S")
            joblib.dump(list(self.history()), os.path.join(p, date + '__' + str(h)))
            saved_histories = os.listdir(p)
            if len(saved_histories) > self.history_limit:
                dates_list = [datetime.strptime(h.split('__')[0], '%Y-%m-%d_%H-%M-%S') for h in saved_histories]
                idx = dates_list.index(min(dates_list))
                logger.debug('history to remove: ' + str(saved_histories[idx]))
                os.remove(os.path.join(p, saved_histories[idx]))

    @lock_resource
    def push(self):
        print("psuhing")
        if self.save_date:
            h = History(date=self.date)

        self.save_history()
        p = self.path / self.branch
        print("branch p", p)
        p.mkdir(exist_ok=True)
        last_commit = self.latest()
        for obj in last_commit.content:
            print("here")
            base_path = p / obj.fname
            if self.save_date:
                print("saving date")
                ### remove last obj ###
                old_fname = [f for f in p.glob(f'{obj.fname}*')]
                if old_fname:
                    old_fname = old_fname[0]
                    os.remove(old_fname)

                fname = h.historify(base_path)
            else:
                fname = base_path
            joblib.dump(obj.content, fname)
        self.commits[self.branch] = [self.latest()]

    @lock_resource
    def pull(self, fname):
        base_path = self.path / self.branch
        rfname = [f for f in base_path.glob(f'{fname}*')]
        if not rfname:
            raise Exception(f"FileNotFoundError: No such file in branch {self.branch}: '{fname}'")
        rfname = rfname[0]
        obj = joblib.load(rfname)
        if self.save_date:
            ### aggiorniamo data ###
            h = History()
            self.date = h.get_time_parsed(rfname)
        return obj

    def revert(self, fname):
        dt = "_".join(fname.split("_")[1:])

    def lock(self):
        with open(os.path.join(self.path, '.' + self.branch + '.lock'), 'w') as f:
            f.write('')

    def unlock(self):
        p = os.path.join(self.path, '.' + self.branch + '.lock')
        if os.path.exists(p):
            os.remove(p)

    def unlock_all_branches(self):
        for branch in self.branches:
            self.branch = branch
            self.unlock()
        self.branch = 'master'

    def get_history(self):
        p = os.path.join(self.path, self.branch, '.history')
        return os.listdir(p)

    @lock_resource
    def pull_from_history(self, id: str):
        p = os.path.join(self.path, self.branch, '.history')
        res = joblib.load(os.path.join(p, id))[-1]
        if self.save_date:
            ### aggiorniamo data ###
            h = History()
            self.date = h.get_time_parsed(id.split('__')[0], format="%Y-%m-%d_%H-%M-%S")
        return res.content

    def get_last_fit(self):
        p = os.path.join(self.path, self.branch)
        lf = [f for f in os.listdir(p) if not f.startswith('.')]
        ### old version ###
        if lf:
            if lf[0] not in ['model', 'transformer']:
                h = History()
                return h.get_time_parsed(lf[0])
            else:
                return True
        else:
            return None


def save_pipeline(pipeline, branch, history_limit, repo_path, dao=None):
    path = repo_path / "predictors" / pipeline.id
    fsvc = FileSystemVC(path, history_limit) if not dao else dao(path)
    if branch in fsvc.branches:
        fsvc.checkout(branch)
    else:
        fsvc.create_branch(branch)
    status_list = [dict(fname=fname, content=step) for fname, step in pipeline.steps]
    fsvc.commit(status_list, date=pipeline.date)
    fsvc.push()




@lru_cache(maxsize=1)
def load_pipeline(model_id,
                  branch,
                  load_from_blueprint = False,
                  im_dao=None,
                  repo_path=None,
                  factory=None,
                  dao=None):
    logger.debug(f"loading pipeline {model_id}")
    path = repo_path / "predictors" / model_id
    logger.debug(f"path:: {path}")
    bp = deserialize(path)
    logger.debug(f"bp:: {bp}")
    steps = bp.pop('steps')
    pipeline = TSPipeline(**bp)
    logger.debug(f"pipeline ok::: {pipeline}")
    if load_from_blueprint:
        for k, v in steps.items():
            logger.debug("core_utils....")
            step_eval = get_factory(v)
            logger.debug(f"value {v} step eval:: {step_eval.__dict__}")
            pipeline.add([k, factory(step_eval)])
        logger.debug('MODEL IS NOT FITTED')
        return pipeline

    if im_dao and model_id in im_dao.objs:
        pipeline = im_dao.get_by_id(model_id)
        ### CHECK!! ###
        objs = [obj for name,obj in pipeline.steps if obj]
        if len(objs)==2:
            logger.debug('Model already in memory')
            return pipeline
        else:
            logger.debug('EMPTY MODEL!!')

    logger.debug('MODEL IS FITTED')
    fsvc = FileSystemVC(path) if not dao else dao(path)
    logger.debug(f"branch:: {branch}")
    fsvc.checkout(branch)
    for el in ['transformer', 'model']:
        print(el)
        pipeline.add((el, fsvc.pull(el)))
    pipeline.date = fsvc.date
    ### se non lo ha ancora in memoria, lo carica
    if im_dao:
        im_dao.load(model_id, pipeline)
    print("pipeline loaded")
    return pipeline

def is_url(object):
    if not isinstance(object, str):
        return False
    try:
        result = urlparse(object)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def to_dataframe(data, **kwargs):
    """Transforms different kinds of data in a pandas DataFrame"""
    if is_url(data):
        with NamedTemporaryFile() as o:
            urllib.request.urlretrieve(data, o.name)
            return pd.read_csv(o, **kwargs)

    if isinstance(data, pd.DataFrame):
        return data

    if isinstance(data, csr_matrix):
        return pd.DataFrame(data.toarray(), **kwargs)

    # if isinstance(data, list) and isinstance(data[0], dict):
        # temp = defaultdict(list)
        # columns = set()
        # for el in data:
        #     columns.update(el.keys())
        # columns = sorted(list(columns))
        # for el in data:
        #     for k in columns:
        #         temp[k].append(el.get(k))
        # return pd.DataFrame(temp, columns=columns, **kwargs)
    return pd.DataFrame(data, **kwargs).fillna(np.nan)


