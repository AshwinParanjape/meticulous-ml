import sys, os, json, datetime
from glob import glob
from git import Repo
from typing import Dict

from meticulous.utils import Tee, ExitHooks
import atexit
import traceback
import logging
logger = logging.getLogger('meticulous')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class DirtyRepoException(Exception):
    """Raised when the repo is dirty"""
    pass
class Experiment(object):
    """Class to keep track and store an experiment's configurations, the code version (via git) and the summary results"""

    def __init__(self, args, default_args={}, project_directory ='', experiments_directory ='experiments', experiment_id=None, description ='', resume = False, norecord = False ):
        """Setup the experiment configuration

        1. Find a git repo by looking at the project and its parent directories
        2. Throws an error if the repo is dirty (has uncommitted tracked files)
        3. Creates the experiments directory if it doesn't exist
        4. Extracts metadata from the git repo
        5. If resume=True, tries to find an experiment that exactly matches the arguments and the git sha.
            If it finds one, sets that as the current experiment directory.
            So the program can then resume by using any intermediate saved state
        6. If experiment_id is provided sets that as the current experiment
            reusing the existing experiment directory if it exists

        7. Saves experiment info
        8. Redirects stdout and stderr to the experiment directory
        9. Creates the STATUS file inside experiment directory

        Args:
            args (dict): Arguments to the program
            default_args (dict): Default values of the arguments. If supplied helps display experiments using differentiating arguments
            project_directory (str): The directory containing the project. It should have a git repo.
            experiments_directory (str): The directory containing experiments (is expected to be inside project_directory). Created if it doesn't exist
            experiment_id:
            description (str): Descriptor for the experiment
            resume (str): if True it looks for an existing experiment, with matching gitsha and args to resume
            norecord (str): If true, it skips the entire process and does not record the experiment
        """

        self.norecord = norecord
        self.curexpdir='.'
        if norecord:
            return
        self.project_directory = project_directory
        self._set_repo_directory()

        #Check if the repo is clean
        if self.repo.is_dirty():
            raise DirtyRepoException

        self._set_experiments_directory(experiments_directory)

        #Store metadata about the repo
        commit = self.repo.commit()
        self.metadata = {}
        self.metadata['githead-sha'] = commit.hexsha
        self.metadata['githead-message'] = commit.message
        self.metadata['description'] = description
        self.metadata['timestamp'] = datetime.datetime.now().isoformat()
        self.metadata['command'] = sys.argv

        self.curexpdir = None

        # Asked to resume, check if we can resume given the git-sha and program arguments
        if resume:
            #Find the lastest existing experiment with the same git head and args
            for exp in glob(self.experiments_directory+'/*/'):
                with open(os.path.join(exp, 'args.json'), 'r') as af:
                    with open(os.path.join(exp, 'metadata.json'), 'r') as mf:
                        fargs = json.load(af)
                        fmetadata = json.load(mf)
                        #print(exp, fargs, vars(args), fmetadata, self.metadata)
                        if  fargs == args and fmetadata['githead-sha'] == self.metadata['githead-sha']:
                            logger.info(f"Resuming existing experiment from {exp}")
                            self.curexpdir = exp
                            break
            else:
                logger.info(f"Could not find existing experiment")

        if experiment_id:
            self.curexpdir = os.path.join(self.experiments_directory, experiment_id)
            logger.info(f"Using provided experiment_id {self.curexpdir}")

        # self.curexpdir contains experiment dir if resume was requested and was possible
        if self.curexpdir is None:
            # Get existing experiments (the assumption is that they are integers
            existing_exp = [int(d.split('/')[-2]) for d in glob(self.experiments_directory+'/*/')]

            # Add one to the largest experiment number
            self.curexpdir = os.path.join(self.experiments_directory, str(max(existing_exp+[0,])+1))
            logger.info(f"New experiment at {self.curexpdir}")

        if not os.path.isdir(self.curexpdir):
            os.mkdir(self.curexpdir)
        else:
            print("Experiment directory exists! reusing it")

        #Write experiment info
        with self.open('args.json', 'w') as f:
            json.dump(args, f, indent=4)

        with self.open('default_args.json', 'w') as f:
            json.dump(default_args, f, indent=4)

        with self.open('metadata.json', 'w') as f:
            json.dump(self.metadata, f, indent=4)

        # Tee stdout and stderr to files as well
        self.stdout = Tee(sys.stdout, self.open('stdout', 'a'))
        sys.stdout = self.stdout
        self.stderr = Tee(sys.stderr, self.open('stderr', 'a'))
        sys.stderr = self.stderr

        self._set_status_file()

    @staticmethod
    def add_argument_group(parser):
        """Add the meticulous arguments to argparse as a separate group"""

        group = parser.add_argument_group('meticulous', 'arguments for initializing Experiment object')
        group.add_argument('--project-directory', action="store", default='',
                           help='Project directory. Need not be the same as repo directory, but should be part of a git repo')
        group.add_argument('--experiments-directory', action="store", default='experiments',
                           help='A directory to store experiments, should be in the project directory')
        group.add_argument('--experiment-id', action="store", default=None,
                           help='explicitly specified experiment id')
        group.add_argument('--description', action="store", default='', help='A description for this experiment')
        group.add_argument('--resume', action="store_true",
                           help='Resumes an existing experiment with same arguments and git sha. If no such experiment is found, starts a new one')
        group.add_argument('--norecord', action="store_true",
                           help='Override meticulous recording of the experiment. Does not enforce that the repo be clean and can be used during development and debugging of experiment')

    @classmethod
    def from_parser(cls, parser, **meticulous_args):
        """
        Extract meticulous specific arguments from argparse parser and return an Experiment object
        Args:
            parser: argparse parser
            **meticulous_args: any other args for constructing Experiment object that may not be in the parser

        Returns:
            Experiment object
        """
        args = parser.parse_args()
        args = vars(args)
        meticulous_args = {}
        for arg in ['project_directory', 'experiments_directory', 'experiment_id', 'description', 'resume', 'norecord']:
            if arg in args:
                meticulous_args[arg] = args[arg]
                del args[arg]

        default_args = parser.parse_args([])
        default_args = vars(default_args)
        for arg in ['project_directory', 'experiments_directory', 'experiment_id', 'description', 'resume', 'norecord']:
            if arg in default_args:
                del default_args[arg]

        return cls(args, default_args=default_args, **meticulous_args)

    def summary(self, summary_dict: Dict):
        """Takes a dictionary object score and (over)writes it in the experiment directory"""
        if self.norecord:
            return
        try:
            with self.open('summary.json', 'r') as f:
                summary = json.load(f)
        except FileNotFoundError:
            summary = {}
        summary.update(summary_dict)
        with self.open('summary.json', 'w') as f:
            json.dump(summary, f, indent=4)


    def open(self, *args, **kwargs):
        """wrapper around the function open to redirect relative paths to  experiment directory"""
        if not self.norecord:
            path = args[0] if os.path.isabs(args[0]) else os.path.join(self.curexpdir, args[0])
            args = (path,)+ args[1:]
        return open(*args, **kwargs)

    def _set_repo_directory(self):
        """Finds a git repo by searching the project and its parent directories and sets self.repo_directory"""
        self.repo = Repo(self.project_directory, search_parent_directories=True)
        logger.debug(f"Found git repo at {self.repo}")

        # Absolute path of the repo
        self.repo_directory = self.repo.working_dir

    def _set_experiments_directory(self, experiments_directory):
        """Creates the experiments directory if it doesn't exit and adds it to .gitignore

        Args:
            experiments_directory (str): The directory to store all experiments

        Returns: None
        """

        # Create the expdir if it doesn't exist
        self.experiments_directory = os.path.join(self.project_directory, experiments_directory)
        if not os.path.isdir(self.experiments_directory):
            os.mkdir(self.experiments_directory)

        # ignore the experiment directory from git tree if not ignored yet
        try:
            with open(os.path.join(self.repo_directory, '.gitignore'), 'r') as f:
                ignored = os.path.relpath(self.experiments_directory, self.repo_directory) in [p.strip() for p in f.readlines()]
        except FileNotFoundError as e:
            print("Creating local .gitignore")
            ignored = False
        if not ignored:
            print("Adding experiments directory to .gitignore")
            with open(os.path.join(self.repo_directory, '.gitignore'), 'a') as f:
                f.write(os.path.relpath(self.experiments_directory, self.repo_directory)+'\n')
            self.repo.index.add([os.path.join(self.repo_directory, '.gitignore')])
            self.repo.index.commit('Added experiments directory to .gitignore')

    def _set_status_file(self):
        """
        Set exit hook which writes SUCCESS upon successful termination of the experiment to STATUS file.
        If the experiment terminated with an error, it writes the error message.
        While the experiment is running the STATUS file contains RUNNING
        """
        self.hooks = ExitHooks()
        self.hooks.hook()
        def exit_hook():
            with self.open('STATUS', 'w') as f:
                if self.hooks.exited:
                    f.write(f"ERROR\nsys.exit({self.hooks.exit_code})" )
                elif self.hooks.raised_exception:
                    traceback.print_exception(self.hooks.exc_info['exc_type'],
                                              self.hooks.exc_info['exc_value'],
                                              self.hooks.exc_info['exc_traceback'],
                                              file=f)
                else:
                    f.write('SUCCESS')
        with self.open('STATUS', 'w') as f:
            f.write('RUNNING')
        atexit.register(exit_hook)
