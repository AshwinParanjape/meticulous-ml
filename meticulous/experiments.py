from git import Repo
import sys
from glob import glob
import os
import json
from collections import defaultdict, OrderedDict
import time
from io import StringIO
import re
from tabulate import tabulate
import traceback
#import matplotlib.pyplot as plt
#import pandas as pd
#from IPython.core.display import display, HTML
#from pandas.io.json import json_normalize

class pretty_dict(dict):
    def __str__(self):
        def helper(root):
            return {k:round(v,2) if isinstance(v,float) else (helper(v) if isinstance(v, dict)  else v) for k,v in root.items()}

        return str(helper(self))

def revisionAncestor(repo, exp1, exp2):
    return repo.is_ancestor(exp1.sha, exp2.sha)

def revisionEqual(exp1, exp2):
    return exp1.sha == exp2.sha

def argEqual(a, b, ignore_keys):
    ka = set(a).difference(ignore_keys)
    kb = set(b).difference(ignore_keys)
    return ka == kb and all(a[k] == b[k] for k in ka)


class ExperimentReader(object):
    def __init__(self, curexpdir, log_vars = [], ignore_args = []):
        self.curexpdir = curexpdir
        self.log_vars = log_vars
        self.expid = self.curexpdir.split('/')[-2]
        with self.open('metadata.json', 'r') as f:
            self.metadata = json.load(f)
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
        if not hasattr(self, '_log'):
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
        with self.open('summary.json', 'r') as f:
            s = pretty_dict(json.load(f))
        return s

    def __repr__(self):
        return self.curexpdir

class Experiments(object):
    """Class to compare and contrast different experiements"""
    def __init__(self, basedir = '', expdir = 'experiments', ignore_args = [], log_vars = [], display_args = [], ExperimentReader = ExperimentReader):
        self.basedir = basedir
        self.ignore_args = ignore_args
        self.log_vars = log_vars
        self.repo = Repo(self.basedir, search_parent_directories=True)
        self.repodir = self.repo.working_dir
        self.expdir = expdir
        self.ExperimentReader = ExperimentReader
        self.display_args = display_args
        self.refresh()

    def refresh(self):
        experiments = []
        for exp in glob(self.expdir+'/*/'):
            try:
                experimentReader = self.ExperimentReader(exp, ignore_args = self.ignore_args, log_vars = self.log_vars)
                self.experiments.append(experimentReader)
            except Exception as e:
                print(f"Unable to read {exp}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

            #if not experimentReader.empty:
        self.experiments = {e.expid: e for e in sorted(self.experiments, key = lambda expReader: expReader.ts)}

    # TODO express this as sql
    def gather_changes(self):
        self._code_change = {}
        self.arg_change = defaultdict(set)
        self.repeat_experiment = defaultdict(set)
        for exp1 in self.experiments:
            for exp2 in self.experiments:
                if exp1 == exp2:
                    print(exp1, exp2)
                    continue
                if revisionEqual(exp1, exp2):
                    sha = exp1.sha
                    if not argEqual(exp1.args, exp2.args, ignore_args):
                        self.arg_change[sha].add(exp1)
                        self.arg_change[sha].add(exp2)
                    else:
                        self.repeat_experiment[sha].add(exp1)
                        self.repeat_experiment[sha].add(exp2)
                elif revisionAncestor(self.repo, exp1, exp2) and argEqual(exp1.args, exp2.args, ignore_args):
                    self._code_change[(exp1.expid, exp2.expid)]  = CodeChange(self.repo, exp1, exp2)

    def __getitem__(self, key):
        return self.experiments[key]

    # Rewrite as sql query
    def group_by_commits(self, last=None, experiment_list = None):
        if last is None:
            last = len(self.experiments)
        if experiment_list is None:
            experiment_list = self.experiments[-last:]
        groups = defaultdict(list)
        for e in experiment_list:
            groups[e.sha].append(e)
        groups = {k: sorted(v, key=lambda e: e.ts, reverse=True) for k, v in groups.items()}
        groups_with_ts = []
        for i in groups.items():
            try:
                groups_with_ts.append((i, self.repo.commit(i[0]).committed_datetime))
            except ValueError:
                print('sha: '+i[0] + ' missing', file=sys.stderr)

        groups_with_ts = [o[0] for o in sorted(groups_with_ts, key=lambda o: o[1], reverse=True)]
        commit_groups = OrderedDict(groups_with_ts)
        return commit_groups

    # Group by sql query
    def display_commit_groups(self, display_args = None, last=None, experiment_list=None):
        if display_args is None:
            display_args = self.display_args
        commit_groups = self.group_by_commits(last=last, experiment_list=experiment_list)
        for k, v in commit_groups.items():
            print(k[:7], self.repo.commit(k).message.strip())
            arg_val_set = defaultdict(set)
            all_non_default_keys = set()
            for e in v:
                for k in e.args:
                    all_non_default_keys.add(k)
            for e in v:
                for k in all_non_default_keys:
                    arg_val_set[k].add(str(e.all_args[k]))
            #print(arg_val_set)
            different_keys = set([k for (k, v) in arg_val_set.items() if len(v)>1])
            common_args = {k: v.pop() for (k, v) in arg_val_set.items() if len(v) == 1}
            print(common_args)
            df = pd.DataFrame(json_normalize([{'id':e.expid, 'status': e.status, 'ts':time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(e.ts)), 'args': {k:e.all_args[k] for k in e.all_args if k in different_keys} ,'score': e.summary()} for e in v], sep='\n')).set_index('id')
            def color_status(row):
                if row['status'] == 'RUNNING':
                    return ['background-color: #F0FFFF' for r in row]
                if row['status'] == 'ERROR':
                    return ['background-color: #FFE4E1' for r in row]
                if row['status'] == 'SUCCESS':
                    return ['background-color: #F0FFF0' for r in row]
                else:
                    return ['' for r in row]
            df_styler = df.style.apply(color_status, axis=1)
            display(HTML(df_styler.render()))
            #for e in v:
            #    print('*',  )

        #commits = set([e.sha for e in self.experiments])
        #ordered_commits = sorted(commits, key = lambda c: self.repo.commit(c).committed_time, reverse=True)

def tabulate_experiments(experiments, display_args=False):
    if display_args:
        all_args = []
        for exp in experiments:
            for arg in exp.args.keys():
                if arg not in all_args:
                    all_args.append(arg)

        return tabulate([(exp.curexpdir, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp.ts)), exp.sha[:7], exp.status, *[exp.args.get(arg, '') for arg in all_args]) for exp in experiments], ("Path", "Timestamp", "Commit", "Status", *all_args), tablefmt='pretty')
    else:
        return tabulate([(exp.curexpdir, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp.ts)), exp.sha[:7], exp.status) for exp in experiments], ("Path", "Timestamp", "Commit", "Status"), tablefmt='pretty')




