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

    def open(self, *args, **kwargs):
        """wrapper around the function open to redirect to experiment directory"""
        args = (os.path.join(self.curexpdir, args[0]),)+ args[1:]
        return open(*args, **kwargs)

    def __init__(self, curexpdir):
        """
        Read experiment data from curexpdir. Reads metadata.json, args.json, default_args.json, STATUS and summary.json.

        Args:
            curexpdir: The experiment directory to read
        """
        self.curexpdir = curexpdir
        self.expid = self.curexpdir.split('/')[-2]

        # Load metadata
        try:
            with self.open('metadata.json', 'r') as f:
                self.metadata = json.load(f)
        except FileNotFoundError as e:
            self.metadata = {}

        # Extract useful attributes
        self.metadata['command'] = ' '.join(self.metadata.get('command', []))
        self.sha = self.metadata.get('githead-sha', None)
        self.begin_time = self.metadata.get('timestamp', os.path.getctime(self.curexpdir))

        # Load args
        try:
            with self.open('args.json', 'r') as f:
                self.args = json.load(f)
        except FileNotFoundError as e:
            self.args = {}

        # Load default args
        try:
            with self.open('default_args.json', 'r') as f:
                self.default_args = json.load(f)
        except FileNotFoundError as e:
            self.default_args = {}

        # Load status
        self.refresh_status()

        # Load summary
        self.refresh_summary()


    def refresh_status(self):
        """Read STATUS file"""
        try:
            with self.open('STATUS', 'r') as f:
                ls = list(f)
                self.status = ls[0]
                self.status_message = '' if len(ls) <= 1 else ls[-1]
        except (FileNotFoundError, IndexError):
            self.status = 'UNKNOWN'
            self.status_message = ''

    def refresh_summary(self):
        """Read summary.json"""
        try:
            with self.open('summary.json', 'r') as f:
                self.summary = json.load(f)
        except FileNotFoundError:
            self.summary = {}

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









