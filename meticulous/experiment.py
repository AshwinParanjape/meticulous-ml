import sys, os, json, datetime
from glob import glob
from git import Repo
from typing import Dict

from meticulous.utils import Tee, ExitHooks
from meticulous.repo import REPO, COMMIT
import atexit
import traceback
import logging
logger = logging.getLogger('meticulous')


ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
class Experiment(object):
    """Class to keep track and store an experiment's configurations, the code version (via git) and the summary results"""

    def __init__(self, args: Dict, default_args:Dict={}, project_directory: str ='', experiments_directory:str ='experiments',
                 experiment_id=None, description:str ='', norecord:bool = False ):
        """Setup the experiment configuration

        1. Find a git repo by looking at the project and its parent directories
        2. Throws an error if the repo is dirty (has uncommitted tracked files)
        3. Creates the experiments directory if it doesn't exist
        4. Extracts metadata from the git repo
        5. If experiment_id is provided sets that as the current experiment
            If such an experiment exists, then checks if it exactly matches the arguments and the git sha.
            If not, throws an error.
            Otherwise, it resumes that experiment by setting it as the current experiment.

        6. Saves experiment info
        7. Redirects stdout and stderr to the experiment directory
        8. Creates the STATUS file inside experiment directory

        Args:
            args (dict): Arguments to the program
            default_args (dict): Default values of the arguments.
                If supplied helps display experiments using differentiating arguments
            project_directory (str): Path to the project directory, should be part of a git repo
            experiments_directory (str): Path to the directory that stores experiments.
                If a relative path is specified then it is relative to the project directory.
                Created if it doesn't exist
            experiment_id: Explicitly specified experiment id used for naming experiment folder.
                If the folder exists (i.e. experiment was run previously), then,
                    checks for matching args and githead-sha before resuming,
                otherwise, creates a new experiment folder
            description (str): Descriptor for the experiment
            norecord (bool): If true, it skips the entire process and does not record the experiment
        """

        self.norecord = norecord
        self.curexpdir='.' #: Doc comment *inline* with attribute
        """str: Path to the directory for the current experiment"""
        if norecord:
            return
        self.project_directory = project_directory
        self._set_repo_directory()

        #Check if the repo is clean
        if self.repo.is_dirty():
            raise DirtyRepoException("There are some tracked but uncommitted files. Please commit them or remove them from git tracking.")

        self._set_experiments_directory(experiments_directory)

        #Store metadata about the repo
        commit = COMMIT
        self.metadata = {}
        """dict: Metadata stored to metadata.json"""
        self.metadata['githead-sha'] = commit.hexsha
        self.metadata['githead-message'] = commit.message
        self.metadata['description'] = description
        self.metadata['start-time'] = datetime.datetime.now().isoformat()
        self.metadata['command'] = sys.argv

        self.curexpdir = None

        if experiment_id:
            self.curexpdir = os.path.join(self.experiments_directory, experiment_id)
            logger.info("Using provided experiment_id: {curexpdir}".format(curexpdir=self.curexpdir))

            if os.path.isdir(self.curexpdir):
                logger.info("Found existing folder with experiment_id: {curexpdir}, attempting to resume.".format(curexpdir=self.curexpdir))
                # The experiment already exists, check if we can resume given the git-sha and program arguments
                with open(os.path.join(self.curexpdir, 'args.json'), 'r') as af:
                    with open(os.path.join(self.curexpdir, 'metadata.json'), 'r') as mf:
                        existing_experiment_args = json.load(af)
                        existing_experiment_fmetadata = json.load(mf)

                        if existing_experiment_args != args:
                            raise MismatchedArgsException("Provided args do not match stored args for the existing experiment,"
                                                          " please specify the correct experiment id or create a new experiment")

                        elif existing_experiment_fmetadata['githead-sha'] != self.metadata['githead-sha']:
                            raise MismatchedCommitException(
                                "Current githead sha ({current_githead_sha}) does not match the githead-sha of "
                                "the existing experiment ({old_githead_sha}), "
                                "please specify the correct experiment id or create a new experiment" \
                                    .format(current_githead_sha=self.metadata['githead-sha'],
                                            old_githead_sha=existing_experiment_fmetadata['githead-sha']),
                            )
                        else:
                            logger.info("Args and githead-sha matches, resuming experiment")
            else:
                os.mkdir(self.curexpdir)

        else:
            # Get existing experiments
            existing_exp = [d.split(os.sep)[-2] for d in glob(self.experiments_directory+'/*/')]

            # Only consider integer experiment ids
            existing_int_exp = []
            for e in existing_exp:
                try:
                    existing_int_exp.append(int(e))
                except ValueError:
                    continue

            # Add one to the largest experiment number
            self.curexpdir = os.path.join(self.experiments_directory, str(max(existing_int_exp+[0,])+1))
            os.mkdir(self.curexpdir)
            logger.info("New experiment at {curexpdir}".format(curexpdir=self.curexpdir))

        #Write experiment info
        with self.open('args.json', 'w') as f:
            json.dump(args, f, indent=4)

        with self.open('default_args.json', 'w') as f:
            json.dump(default_args, f, indent=4)

        with self.open('metadata.json', 'w') as f:
            json.dump(self.metadata, f, indent=4)

        # Tee stdout and stderr to files as well
        self.stdout = Tee("stdout", self.open('stdout', 'a'))
        self.stderr = Tee("stderr", self.open('stderr', 'a'))

        self._set_status_file()

    @staticmethod
    def add_argument_group(parser, project_directory ='', experiments_directory='experiments', experiment_id=None,
                           description='', norecord=False):
        """Add the meticulous arguments to argparse as a separate group

        Args:
            parser: An argparse.ArgumentParser object
            project_directory: default for --project-directory argument
            experiments_directory: default for --experiments-directory argument
            experiment-id: default for --experiment-id argument
            description: default for --description argument
            norecord: default for --norecord argument
        """

        group = parser.add_argument_group('meticulous', 'arguments for initializing Experiment object')
        group.add_argument('--project-directory', action="store", default=project_directory,
                           help='Path to the project directory, should be part of a git repo')
        group.add_argument('--experiments-directory', action="store", default=experiments_directory,
                           help='Path to the directory that stores experiments. '
                                'If a relative path is specified then it is relative to the project directory. ')
        group.add_argument('--experiment-id', action="store", default=experiment_id,
                           help='Explicitly specified experiment id used for naming experiment folder. '
                                'If the folder exists (i.e. experiment was run previously), then,'
                                '   checks for matching args and githead-sha before resuming, '
                                'otherwise, creates a new experiment folder')
        group.add_argument('--description', action="store", default=description, help='A text description for this experiment')
        group.add_argument('--norecord', action="store_true", default=norecord,
                           help='Disable experiment tracking. '
                                'Repo can be dirty and no new experiment folders are created. '
                                'Useful during development and debugging')

    @staticmethod
    def extract_meticulous_args(parser, arg_list = None):
        """
        Extract meticulous specific arguments from argparse parser and return them as a dictionary

        Args:
            parser: An argparse.ArgumentParser object
            arg_list: list of arguments, default is sys.argv[1:]

        Returns:
            Dictionary of meticulous specific arguments

        """
        if arg_list is None:
            arg_list = sys.argv[1:]
        args = parser.parse_args(arg_list)
        meticulous_args = {}
        args = vars(args)
        for arg in ['project_directory', 'experiments_directory', 'experiment_id', 'description', 'resume', 'norecord']:
            if arg in args:
                meticulous_args[arg] = args[arg]
        return meticulous_args


    @classmethod
    def from_parser(cls, parser, arg_list = None, **default_meticulous_args):
        """
        Extract meticulous specific arguments from argparse parser and return an Experiment object

        Args:
            parser: argparse parser
            arg_list: list of arguments, default is sys.argv[1:]
            **meticulous_args: any other args for constructing Experiment object that may not be in the parser

        Returns:
            Experiment object
        """
        if arg_list is None:
            arg_list = sys.argv[1:]
        args = parser.parse_args(arg_list)
        args = vars(args)
        meticulous_args = default_meticulous_args
        for arg in ['project_directory', 'experiments_directory', 'experiment_id', 'description', 'resume', 'norecord']:
            if arg in args:
                meticulous_args[arg] = args[arg]
                del args[arg]
        positional_args = parser._get_positional_actions()
        default_args = parser.parse_args(sys.argv[1:1+len(positional_args)])
        default_args = vars(default_args)
        for arg in ['project_directory', 'experiments_directory', 'experiment_id', 'description', 'resume', 'norecord'] + [a.dest for a in positional_args]:
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
        self.repo = REPO
        logger.debug("Found git repo at {repo}".format(repo=self.repo))

        # Absolute path of the repo
        self.repo_directory = self.repo.working_dir

    def _set_experiments_directory(self, experiments_directory):
        """Creates the experiments directory if it doesn't exit and adds it to .gitignore

        Args:
            experiments_directory (str): The directory to store all experiments

        Returns: None
        """

        # Create the expdir if it doesn't exist
        # joining an absolute experiments_directory path, ignores the project_directory
        self.experiments_directory = os.path.join(self.project_directory, experiments_directory)
        if not os.path.isdir(self.experiments_directory):
            os.mkdir(self.experiments_directory)

        # ignore the experiment directory from git tree if not ignored yet
        try:
            with open(os.path.join(self.repo_directory, '.gitignore'), 'r') as f:
                ignored = os.path.relpath(self.experiments_directory, self.repo_directory) in [os.path.normpath(p.strip()) for p in f.readlines()]
        except FileNotFoundError as e:
            print("Creating local .gitignore")
            ignored = False
        # if the experiment directory is located inside the repo, but not in the .gitignore
        if not ignored and not os.path.relpath(self.experiments_directory, self.repo_directory).startswith(".."):
            print("Adding experiments directory to .gitignore")
            with open(os.path.join(self.repo_directory, '.gitignore'), 'a') as f:
                f.write(os.path.relpath(self.experiments_directory, self.repo_directory)+'\n')
            self.repo.index.add([os.path.join(self.repo_directory, '.gitignore')])
            self.repo.index.commit('Added experiments directory to .gitignore')

    def _set_status_file(self):
        """
        Set exit hook which writes SUCCESS upon successful termination of the experiment to STATUS file.
        If the experiment terminated with an ERROR, it also records the error code or traceback.
        While the experiment is running the STATUS file contains RUNNING
        """
        self.hooks = ExitHooks()
        self.hooks.hook()
        def exit_hook():
            self.metadata['end-time'] = datetime.datetime.now().isoformat()
            with self.open('metadata.json', 'w') as f:
                json.dump(self.metadata, f, indent=4)
            with self.open('STATUS', 'w') as f:
                if self.hooks.exited:
                    f.write("ERROR\nsys.exit({code})".format(code=self.hooks.exit_code))
                elif self.hooks.raised_exception:
                    f.write("ERROR\n")
                    traceback.print_exception(self.hooks.exc_info['exc_type'],
                                              self.hooks.exc_info['exc_value'],
                                              self.hooks.exc_info['exc_traceback'],
                                              file=f)
                    traceback.print_exception(self.hooks.exc_info['exc_type'],
                                              self.hooks.exc_info['exc_value'],
                                              self.hooks.exc_info['exc_traceback'],
                                              file=sys.stderr)
                else:
                    f.write('SUCCESS')
        with self.open('STATUS', 'w') as f:
            f.write('RUNNING')
        self.atexit_hook = exit_hook
        atexit.register(self.atexit_hook)

    def finish(self, status="SUCCESS"):
        self.metadata['end-time'] = datetime.datetime.now().isoformat()
        with self.open('metadata.json', 'w') as f:
            json.dump(self.metadata, f, indent=4)
        with self.open('STATUS', 'w') as f:
            f.write(status)
        atexit.unregister(self.atexit_hook)
        self.stdout.close()
        self.stderr.close()
    
    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        if type is not None:
            self.finish("ERROR\n" + "\n".join(
                traceback.format_exception(type,
                                        value,
                                        tb)
            ))
            traceback.print_exception(type,
                                        value,
                                        tb,
                                        file=sys.stderr)
            return True
        self.finish()


class DirtyRepoException(Exception):
    """Raised when the repo is dirty"""
    pass

class MismatchedArgsException(Exception):
    """Raised when attempting to resume an experiment with different argument values"""
    pass

class MismatchedCommitException(Exception):
    """Raised when attempting to resume an experiment with different git commit"""
    pass
