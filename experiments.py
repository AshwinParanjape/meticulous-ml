from git import Repo
import sys
from glob import glob
import os
import json
import functools
from collections import defaultdict
import time
from io import StringIO
from functools import partial
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.core.display import display, HTML


def revisionAncestor(repo, exp1, exp2):
    return repo.is_ancestor(exp1.sha, exp2.sha)

def revisionEqual(exp1, exp2):
    return exp1.sha == exp2.sha

def argEqual(a, b, ignore_keys):
    ka = set(a).difference(ignore_keys)
    kb = set(b).difference(ignore_keys)
    return ka == kb and all(a[k] == b[k] for k in ka)

def quote_html(s):
    '''Quote html special chars and replace space with nbsp'''
    def repl_quote_html(m):
        tokens = []
        quote_dict = {
            ' ': '&nbsp;',
            '<': '&lt;',
            '>': '&gt;',
            '&': '&amp;',
            '"': '&quot;',
        }
        for c in m.group(0):
            tokens.append(quote_dict[c])
        return ''.join(tokens)
    return re.sub('[ &<>"]', repl_quote_html, s)


def diff2HTML(lines, title=None, encoding=sys.getdefaultencoding()):
    s = StringIO()
    p = partial(print, file=s)
    q = quote_html
    p('<?DOCTYPE html?>')
    p('<html>')
    p('<head>')
    p('<meta http-equiv="Content-Type" content="text/html; charset={}">'
            .format(q(encoding)))
    if title is not None:
        p('<title>{}</title>'.format(q(title)))
    p('''
        <style>
            span.diffcommand { color: teal; }
            span.removed     { color: red; }
            span.inserted    { color: green; }
            span.linenumber  { color: purple; }
        </style>
    ''')
    p('</head>')
    lines = lines.split('\n')
    p('<h4>{}</h4>'.format(q(title)))

    for line in lines:
        if line.startswith('+++'):
            p(q(line))
        elif line.startswith('---'):
            p(q(line))
        elif line.startswith('+'):
            p('<span class="inserted">{}</span>'.format(q(line)))
        elif line.startswith('-'):
            p('<span class="removed">{}</span>'.format(q(line)))
        elif line.startswith('diff'):
            p('<span class="diffcommand">{}</span>'.format(q(line)))
        else:
            m = re.match(r'^@@.*?@@', line)
            if m:
                num = m.group(0)
                rest = line[len(num):]
                p('<span class="linenumber">{}</span>{}'
                            .format(q(num), q(rest)))
            else:
                p(q(line))
        p('<br />')
    p('</body>')
    p('</html>')
    return s.getvalue()

class ExperimentReader(object):
    def __init__(self, curexpdir, log_vars = [], ignore_args = []):
        self.curexpdir = curexpdir
        self.log_vars = log_vars
        self.expid = self.curexpdir.split('/')[-2]
        with self.open('metadata.json', 'r') as f:
            self.metadata = json.load(f)
        self.sha = self.metadata['githead-sha']

        with self.open('args.json', 'r') as f:
            self.args = json.load(f)
        for iarg in ignore_args:
            del self.args[iarg]
        self.empty = not os.path.exists(os.path.join(self.curexpdir, 'log.json'))
        try:
            self.ts = self.metadata['timestamp']
        except KeyError:
            self.ts = os.path.getctime(os.path.join(self.curexpdir, 'metadata.json'))

    def open(self, *args, **kwargs):
        """wrapper around the function open to redirect to experiment directory"""
        args = (os.path.join(self.curexpdir, args[0]),)+ args[1:]
        return open(*args, **kwargs)

    @property
    def log(self):
        if not hasattr(self, '_log'):
            self._log = []
            with self.open('log.json', 'r') as f:
                logstring = f.read()
                while(len(logstring)>0):
                    try:
                        json.loads(logstring)
                        logstring = ''
                    except json.JSONDecodeError as e:
                        self.log.append(json.loads(logstring[:e.pos]))
                        logstring = logstring[e.pos:]
        return self._log



    def plot(self, ys=None, x=None, interactive = True, strict=True, ax = None, prefix_labels=False, **kwargs):
        if ys==None:
            ys=self.log_vars
        if interactive:
            plt.ion()
        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)
        for y in ys:
            kwargs_ = kwargs.copy()
            self.plot_ys(y=y, x=x, interactive = interactive, strict=strict, ax = ax, prefix_labels=prefix_labels, **kwargs_)
        ax.legend()
        return ax

    def plot_ys(self, y, x=None, interactive = True, strict=True, ax = None, prefix_labels=False, **kwargs):
        """Plot variables from log file"""
        """Strict implies all entries in the log must have the specified x and y headers"""
        if interactive:
            plt.ion()
        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)
        #x_data = []
        #y_data = []
        #for p in self.log:
        #    try:
        #        if x is not None:
        #            x_p = p[x]
        #        y_p = [p[y] for y in ys]
        #    except KeyError as e:
        #        if strict:
        #            raise e
        #    x_data.append(x_p)
        #    y_data.append(y_p)

        #y_data = np.array(y_data)

        d = [dp for dp in self.log if y in dp and (x is None or x in dp)]
        d = pd.DataFrame.from_dict(d)
        if prefix_labels:
            labels = y if label not in kwargs else kwargs['label']
            if isinstance(labels, string):
                labels = self.expid +'_'+ labels
            else:
                raise NotImplementedError
            kwargs['label'] = labels

        if x is None:
            ax.plot(y, data=d, **kwargs)
        else:
            ax.plot(x, y, data=d, **kwargs)
        if interactive:
            plt.ioff()
        return ax

    def __repr__(self):
        return self.curexpdir

class CodeChange(object):
    def __init__(self, repo, exp1, exp2):
        self.repo = repo
        self.exp1 = exp1
        self.exp2 = exp2

    @property
    def diff(self):
        if not hasattr(self, '_diff'):
            self._diff = self.repo.commit(self.exp1.sha).diff(self.exp2.sha, create_patch=True)
        return self._diff

    def graphLogs(self, figsize = (10,8), **kwargs):
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        self.exp1.plot(ax=ax, **kwargs)
        self.exp2.plot(ax=ax, **kwargs)
        #ax.set_yscale("log", nonposy='clip')
        ax.legend()
        return ax

    def htmlDiff(self):
        s = ''
        for d in self.diff:
            print(d.a_path)
            s+=diff2HTML(d.diff.decode('utf-8'), title=d.a_path)
        display(HTML(s))

    def _ipython_display_(self):
        self.htmlDiff()
        self.graphLogs()

    def __repr__(self):
        return self.exp1.__repr__()+'|'+self.exp1.metadata['githead-message']+'->'+ self.exp2.__repr__() + '| '+self.exp2.metadata['githead-message']



class Experiments(object):
    """Class to compare and contrast different experiements"""
    def __init__(self, repodir = '', expdir = 'experiments', ignore_args = [], log_vars = []):
        self.repodir = repodir
        self.repo = Repo(self.repodir)
        self.expdir = expdir
        self.experiments = []
        self.experiments_dict = {}
        for exp in glob(self.expdir+'/*/'):
            experimentReader = ExperimentReader(exp, ignore_args = ignore_args, log_vars = log_vars)
            if not experimentReader.empty:
                self.experiments.append(experimentReader)
                self.experiments_dict[experimentReader.expid] = experimentReader
        self.experiments = sorted(self.experiments, key = lambda expReader: expReader.ts)

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
        return self.experiments_dict[key]

    def code_change(self, pair):
        if pair in self._code_change:
            return self._code_change[pair]
        else:
            self._code_change[pair]  = CodeChange(self.repo, self.experiments_dict[pair[0]], self.experiments_dict[pair[1]])
            return self._code_change[pair]



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
        self.metadata['timestamp'] = time.time()

        self.curexpdir = None

        if resume:
            #Find the lastest existing experiment with the same git head and args
            for exp in glob(self.expdir+'/*/'):
                with open(os.path.join(exp, 'args.json'), 'r') as af:
                    with open(os.path.join(exp, 'metadata.json'), 'r') as mf:
                        fargs = json.load(af)
                        fmetadata = json.load(mf)
                        print(exp, fargs, vars(args), fmetadata, self.metadata)
                        if  fargs == vars(args) and fmetadata == self.metadata:
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
        print(self.curexpdir)
        self.stdout = self.open('stdout', 'a')
        sys.stdout = self.stdout
        self.stderr = self.open('stderr', 'a')
        sys.stderr = self.stderr
        #print = functools.partial(print, flush=True)

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
        try:
            with self.open('summary.json', 'r') as f:
                summary = json.load(f)
        except FileNotFoundError:
            summary = {}
        summary.update(dict)
        with self.open('summary.json', 'w') as f:
            json.dump(summary, f, indent=4)


    def open(self, *args, **kwargs):
        """wrapper around the function open to redirect to experiment directory"""
        if not self.norecord:
            args = (os.path.join(self.curexpdir, args[0]),)+ args[1:]
        return open(*args, **kwargs)


