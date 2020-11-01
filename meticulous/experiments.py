from git import Repo
import sys
from glob import glob
import os
import json
import traceback
import pandas as pd
from pandas.io.json import json_normalize

class ExperimentReader(object):
    """Class to read an experiment folder"""


class ExperimentReader(object):
    def __init__(self, curexpdir, log_vars = [], ignore_args = []):
        self.curexpdir = curexpdir
        self.expid = self.curexpdir.split('/')[-2]
        with self.open('metadata.json', 'r') as f:
            self.metadata = json.load(f)
        self.metadata['command'] = ' '.join(self.metadata['command'])
        self.sha = self.metadata['githead-sha']

        with self.open('args.json', 'r') as f:
            self.all_args = json.load(f)
        for iarg in ignore_args:
            del self.all_args[iarg]

        try:
            with self.open('default_args.json', 'r') as f:
                default_args = json.load(f)
                if default_args is None:
                    raise FileNotFoundError
                self.args = {}
                for k in self.all_args:
                    try:
                        if self.all_args[k] != default_args[k]:
                            self.args[k] = self.all_args[k]
                    except KeyError:
                        self.args[k] = self.all_args[k]

                self.default_args = {k: v for (k, v) in default_args.items() if k not in self.args}

        except FileNotFoundError as e:
            self.args = self.all_args
            self.default_args = {}
        #self.empty = not os.path.exists(os.path.join(self.curexpdir, 'log.json'))
        try:
            self.ts = self.metadata['timestamp']
        except KeyError:
            self.ts = os.path.getctime(os.path.join(self.curexpdir, 'metadata.json'))

        try:
            with self.open('STATUS', 'r') as f:
                ls = list(f)
                self.status = ls[0]
                self.status_message = '' if len(ls) <= 1 else ls[-1]
        except (FileNotFoundError, IndexError):
            self.status = 'UNKNOWN'
            self.status_message = ''

    def open(self, *args, **kwargs):
        """wrapper around the function open to redirect to experiment directory"""
        args = (os.path.join(self.curexpdir, args[0]),)+ args[1:]
        return open(*args, **kwargs)

    @property
    def log(self):
        try:
            return self._log
        except AttributeError:
            self._log = self.read_log_json()
        return self._log

    def read_log_json(self):
        log = []
        with self.open('log.json', 'r') as f:
            logstring = f.read()
            while(len(logstring)>0):
                try:
                    json.loads(logstring)
                    logstring = ''
                except json.JSONDecodeError as e:
                    log.append(json.loads(logstring[:e.pos]))
                    logstring = logstring[e.pos:]
        return log

    def summary(self):
        try:
            return self._summary
        except AttributeError:
            with self.open('summary.json', 'r') as f:
                self._summary = json.load(f)
        return self._summary

    def __repr__(self):
        return self.curexpdir

class Experiments(object):
    """Class to compare and contrast different experiements"""
    def __init__(self, basedir = '', expdir = None, ignore_args = [], display_args = [], ExperimentReader = ExperimentReader):
        self.basedir = basedir
        self.ignore_args = ignore_args
        self.repo = Repo(self.basedir, search_parent_directories=True)
        self.repodir = self.repo.working_dir
        if expdir:
            self.expdir = expdir
        else:
            self.expdir = os.path.join(self.basedir, 'experiments')
        self.ExperimentReader = ExperimentReader
        self.display_args = display_args
        self.refresh()

    def refresh(self):
        experiments = []
        for exp in glob(self.expdir+'/*/'):
            try:
                experimentReader = self.ExperimentReader(exp, ignore_args = self.ignore_args)
                experiments.append(experimentReader)
            except Exception as e:
                print(f"Unable to read {exp}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

            #if not experimentReader.empty:
        self.experiments = {e.expid: e for e in sorted(experiments, key = lambda expReader: expReader.ts)}

    def as_dataframe(self):
        df =  json_normalize(vars(e) for e in self.experiments.values()).set_index('expid')
        max_col_levels = max(len(c.split('.')) for c in df.columns)
        df.columns = pd.MultiIndex.from_tuples(
            [[''] * (max_col_levels - len(level_vals.split('.'))) + level_vals.split('.') for level_vals in
             df.columns])
        return df

    def __getitem__(self, key):
        return self.experiments[key]









