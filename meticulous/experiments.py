from git import Repo
import sys
from glob import glob
import os
import json
import traceback
import pandas as pd

# Use the deprecated import as the new one fails with Python 3.5
try: 
    from pandas import json_normalize
except: 
    from pandas.io.json import json_normalize

class ExperimentReader(object):
    """Class to read an experiment folder"""

    def __init__(self, curexpdir:str):
        """
        Read experiment data from curexpdir. Reads metadata.json, args.json, default_args.json, STATUS and summary.json.

        Args:
            curexpdir: The experiment directory to read
        """
        self.curexpdir = curexpdir
        """str: Path to the directory for the current experiment"""

        self.expid = self.curexpdir.split(os.sep)[-2]
        """str: experiment id"""

        # Load metadata
        self.metadata = {}
        """dict: loaded from metadata.json"""
        try:
            with self.open('metadata.json', 'r') as f:
                self.metadata = json.load(f)
        except FileNotFoundError as e:
            pass

        # Extract useful attributes
        self.metadata['command'] = ' '.join(self.metadata.get('command', []))
        self.sha = self.metadata.get('githead-sha', None)
        self.start_time = self.metadata.get('start-time', os.path.getctime(self.curexpdir))

        # Load args
        #: dict: loaded from args.json
        self.args = {}
        try:
            with self.open('args.json', 'r') as f:
                self.args = json.load(f)
        except FileNotFoundError as e:
            pass

        # Load default args
        #: dict: loaded from default_args.json
        self.default_args = {}
        try:
            with self.open('default_args.json', 'r') as f:
                self.default_args = json.load(f)
        except FileNotFoundError as e:
            pass

        # Load status
        self.status = 'UNKNOWN' # First line of STATUS file
        self.status_message = '' # Last line of STATUS file (usually contains the Python error)
        self.refresh_status()

        # Load summary
        #: dict: loaded from summary.json
        self.summary = {}
        self.refresh_summary()


    def open(self, *args, **kwargs):
        """wrapper around the function open to redirect to experiment directory"""
        args = (os.path.join(self.curexpdir, args[0]),)+ args[1:]
        return open(*args, **kwargs)

    def refresh_status(self):
        """Read STATUS file"""
        try:
            with self.open('STATUS', 'r') as f:
                ls = list(f)
                self.status = ls[0]
                self.status_message = '' if len(ls) <= 1 else ls[-1]
        except (FileNotFoundError, IndexError):
            pass

    def refresh_summary(self):
        """Read summary.json"""
        try:
            with self.open('summary.json', 'r') as f:
                self.summary = json.load(f)
        except FileNotFoundError:
            pass

    def __repr__(self):
        return self.curexpdir

class Experiments(object):
    """Class to load an experiments folder"""
    def __init__(self, project_directory:str = '', experiments_directory:str = None, reader = ExperimentReader):
        """
        Load the repo from project_directory and experiments from expdir using ExperimentReader class.

        Args:
            project_directory: Path to the project directory, should be part of a git repo.
            experiments_directory: Path to the directory that stores experiments. If a relative path is specified then it is relative to the project directory. Created if it doesn't exist.
            reader: To allow overriding with a user defined version of ExperimentReader class.
        """
        self.project_directory = project_directory
        self.repo = Repo(self.project_directory, search_parent_directories=True)
        self.repodir = self.repo.working_dir
        if experiments_directory:
            self.experiments_directory = experiments_directory
        else:
            self.experiments_directory = os.path.join(self.project_directory, 'experiments')
        self.reader = reader
        self.experiments = {}
        """Dict[ExperimentReader]: experiment ids mapped to respective ExperimentReader objects """
        self.refresh_experiments()

    def refresh_experiments(self):
        """Read experiments from the file system"""
        experiments = []
        for exp in glob(self.experiments_directory+'/*/'):
            try:
                experimentReader = self.reader(exp)
                experiments.append(experimentReader)
            except Exception as e:
                print("Unable to read {exp}".format(exp=exp), file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

        self.experiments = {e.expid: e for e in sorted(experiments, key = lambda expReader: expReader.start_time)}


    def as_dataframe(self):
        """Returns all experiment data as a pandas dataframe"""
        if len(self.experiments.values()) > 0:
            df = json_normalize([vars(e) for e in self.experiments.values()]).set_index('expid')

            # Convert json_normalized columns into multilevel columns for ease of use and nicer printing
            max_col_levels = max(len(c.split('.')) for c in df.columns)
            df.columns = pd.MultiIndex.from_tuples(
                [[''] * (max_col_levels - len(level_vals.split('.'))) + level_vals.split('.') for level_vals in
                 df.columns])
            return df
        else:
            raise IndexError("Unable to load any experiments")

    def __getitem__(self, key):
        return self.experiments[key]









