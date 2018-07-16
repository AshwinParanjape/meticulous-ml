from git import Repo
import sys
from glob import glob
import os
import json
import functools

#class Experiments(object):
#    """Class to compare and contrast different experiements"""

class Experiment(object):
    """Class to keep track of different experiments, their configurations, the code (via git) and the results"""

    def __init__(self, args, repodir = '', expdir = 'experiments', desc = '', resume = False, norecord = False):
        """Setup the experiment configuration"""
        self.norecord = norecord
        if norecord:
            return
        self.repodir = repodir
        self.repo = Repo(self.repodir)


        #Create the expdir if it doesn't exist
        self.expdir = os.path.join(repodir, expdir)
        if not os.path.isdir(self.expdir):
            os.mkdir(self.expdir)

        #ignore the experiment directory from git tree if not ignored yet
        with open(os.path.join(self.repodir, '.gitignore'), 'r') as f:
             ignored = expdir in [p.strip() for p in f.readlines()]
        if not ignored:
            with open(os.path.join(self.repodir, '.gitignore'), 'a') as f:
                f.write(expdir)

        #Check if the repo is clean
        assert not self.repo.is_dirty(), "Repo is dirty, clean it and retry"

        #Store metadata about the repo
        commit = self.repo.commit()
        self.metadata = {}
        self.metadata['githead-sha'] = commit.hexsha
        self.metadata['githead-message'] = commit.message
        self.metadata['description'] = desc


        if resume:
            #Find the lastest existing experiment with the same git head and args
            for exp in glob(self.expdir+'/*/'):
                with open(os.path.join(exp, 'args.json'), 'r') as af:
                    with open(os.path.join(exp, 'metadata.json'), 'r') as mf:
                        if json.load(f) == vars(args) and json.load(mf) == self.metadata:
                            self.curexpdir = exp
                            break


        else:
            existing_exp = [int(d.split('/')[-2]) for d in glob(self.expdir+'/*/')]
            self.curexpdir = os.path.join(self.expdir, str(max(existing_exp+[0,])+1))
            os.mkdir(self.curexpdir)

            #Write experiment info
            with self.open('args.json', 'w') as f:
                json.dump(vars(args), f, indent=4)

            with self.open('metadata.json', 'w') as f:
                json.dump(self.metadata, f, indent=4)
        self.stdout = self.open('out.txt', 'a')
        sys.stdout = self.stdout
        #print = functools.partial(print, file=self.stdout, flush=True)
        print('aha')

    def log(self, score):
        """Takes a dictionary object and appends it to a log in the experiment directory"""
        if self.norecord:
            return
        with self.open('log.json', 'a') as f:
            json.dump(score, f, indent=4)

    def summary(self, dict):
        """Takes a dictionary object score and (over)writes it in the experiment directory"""
        if self.norecord:
            return
        with self.open('summary.json', 'r') as f:
            summary = json.load(f)
        summary.update(dict)
        with self.open('summary.json', 'w') as f:
            json.dump(summary, f, indent=4)


    def open(self, *args, **kwargs):
        """wrapper around the function open to redirect to experiment directory"""
        if not self.norecord:
            args = (os.path.join(self.curexpdir, args[0]),)+ args[1:]
        return open(*args, **kwargs)


