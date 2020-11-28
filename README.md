# Meticulous-ml
![tests](https://github.com/AshwinParanjape/meticulous/workflows/tests/badge.svg)

Machine learning research involves iterating over ideas and running experiments multiple times. 
For research, reproducibility and perhaps sanity, it is important to keep track of the exact setup and resulting output for each run. 
But is only useful if it is stored in an accessible and usable manner. 
Meticulous is a python library to record the setup and the results of experiments in just a few lines of code.
All the data is stored locally, on the file system, in a human readable format and made further accessible as a Python objects and also a Pandas dataframe. 

When an experiment is run using Meticulous, it
1. Creates a new numbered folder to record the experiment. 
2. Uses VCS (git) to ensure that the code is committed and records the commit-sha.
3. Extracts (using argparse) and records the arguments passed to the program.
4. Keeps a copy of program output (stdout and stderr).
5. Provides a helper function to open files in the experiment directory and to save a json summary.

When an experiment folder is read in Python using Meticulous, 
1. Reads each experiment into an `ExperimentReader` object (subclassable). 
2. Creates a Pandas dataframe with all the stored metadata.

Also provided is a handy command-line script (also called `meticulous`) that provides a quick look at the contents of an experiment folder.

# Getting started
## Installation
Simplest way is to use pip

```bash 
pip install git+https://github.com/ashwinparanjape/meticulous-ml.git
```

## Suggest usage
To integrate with your code, follow these steps
Meticulous uses git to keep track of code state. If you aren't already using git, create a new local repository and commit your code to it.

First import `Experiment` class
```python
from meticulous import Experiment 
```

Then let's say you are using argparse and have a parser that takes in some arguments
```python
parser = argparse.ArgumentParser()
parser.add_argument('--batch-size', type=int, default=64, metavar='N',
                        help='input batch size for training (default: 64)')
...
```

You can add meticulous args as an argument group using the `add_argument_group` staticmethod as follows
```python
Experiment.add_argument_group(parser)
```
The "meticulous" argparse group provides following options to customise behaviour
```
meticulous:
  arguments for initializing Experiment object

  --project-directory PROJECT_DIRECTORY
                        Project directory. Need not be the same as repo
                        directory, but should be part of a git repo
  --experiments-directory EXPERIMENTS_DIRECTORY
                        A directory to store experiments, should be in the
                        project directory
  --experiment-id EXPERIMENT_ID
                        explicitly specified experiment id
  --description DESCRIPTION
                        A description for this experiment
  --resume              Resumes an existing experiment with same arguments and
                        git sha. If no such experiment is found, starts a new
                        one
  --norecord            Override meticulous recording of the experiment. Does
                        not enforce that the repo be clean and can be used
                        during development and debugging of experiment
```

Then create an object using the `from_parser` classmethod, which extracts meticulous args separately from the other args. After that you can extract the non-meticulous args as usual.
```
experiment = Experiment.from_parser(parser)
args = parser.parse_args()
```

This will create a directory structure in your project directory as follows
```
experiments/
└── 1
    ├── STATUS
    ├── args.json
    ├── default_args.json
    ├── metadata.json
    ├── stderr
    └── stdout
```
* `args.json` contains the args inferred by the argparse.Parser object
* `default_args.json` contains the default args as encoded in the argparse.Parser object
* `metadata.json` looks like the following
```json
{
    "githead-sha": "970d8ad001f5d42a9ecaa5e3791765d65e02292a",
    "githead-message": "Explicitly close stdout and stderr\n",
    "description": "",
    "timestamp": "2020-11-02T12:48:36.150350",
    "command": [
        "training_utils.py"
    ]
}
```
* `STATUS` file is either `RUNNING`, `SUCCESS`, `ERROR` or the python traceback.
* `stdout` and `stderr` files contain the two output streams. 

You can use the `experiment` object to open files in the current experiment's directory. For e.g. 
```python
with experiment.open('model.pkl', 'wb') as f:
    pkl.dump(weights, f)
...
```

You can also store a summary of the experiment so far. This is a json file that gets overwritten everytime `summary` is called. This file has a special meaning because it is read and shown by the meticulous reader. 
```python
experiment.summary({'loss': loss, 'accuracy': accuracy})
```

Here are all the above modifications to an example script (assumes you are using argparse)
```patch
+ from meticulous import Experiment 

  parser = argparse.ArgumentParser()
  parser.add_argument('--batch-size', type=int, default=64, metavar='N',
                        help='input batch size for training (default: 64)')
  ...

+ # Adds the "meticulous" argument group to your script
+ Experiment.add_argument_group(parser)

+ # Creates experiment object using original experiment args and "meticulous" args
+ experiment = Experiment.from_parser(parser)
  args = parser.parse_args()
  ...
 
+ # Overwrites summary.json in experiment directory
+ experiment.summary({'loss': loss, 'accuracy': accuracy})  
  
+ # Writes model file to the experiment directory
- with open('model.pkl', 'wb') as f:
+ with experiment.open('model.pkl', 'wb') as f:
    pkl.dump(weights, f)
  ...
```

## Overriding defaults
You can provide your own `experiments-directory` and `experiment-id` to override the defaults. 

# Design

ML practioners have very different workflows, with different environments, schedulers and dashboards. And for a good reason, because everyone has different needs. Keeping that in mind, meticulous has the following goals

## Goals 
* Record experiments and setup accurately
* Recorded experiments and setup should be easy to read and access
* Make minimal assumptions about the workflow and work well with other tools
* Be easy to customize and extend according to individual needs
* Encourage best practices by provide opinionated but sensible defaults

Keeping these goals in mind, following choices were made. 

## Choices
* Use git and argparse, which are widely used, to capture the setup.
* Organize experiments using the filesystem in human readable file formats.
* Terminal based script to quickly read and show all experiment data from filesystem.
* Depend only on filesystem and git. No other assumptions about how your experiment is run. 
* Support storing and reading summary metrics which are crucial for knowing which experiments were successful.
* Restrict the featureset to minimize footprint and maximize code readability/extensibility. 
* Doesn't run a server in the background, doesn't have a web UI and doesn't create plots.
* Provide all experiment data as a pandas dataframe and each experiment as a Python object, so that you can write your own code on top on top of it.


# Backstory

As an NLP PhD student I run lots of ML experiments. There is no standard way of keeping track of experiments. Initially I would concatenate all arguments in a single string. Then I moved on to using random 4 letter folder names for each experiment. Then by the time I would meet with my advisor, I would have forgotten which model change caused the results to improve, because that's part of the model and not the arguments. A couple of years ago (2018) I started writing a python script to automate the "keeping track of experiments". 

But then I found myself browsing through the filesystem to find which was the best configuration. So I built a fancy dashboard for myself using a Jupyter notebook. But then I moved to a different project and the project specific dashboard would work no more. So I kept whittling the featureset until I was left with a core that was minimal, which meant it worked across all the different projects and setups. And easily extensible, which meant it satisfied individual needs without much effort. 

Meanwhile many other experiment tracking and management systems were being developed and I was hopeful I could use them instead. [Comet.ml](https://www.comet.ml/site/), [Weights & Biases](https://docs.wandb.com) are cloud based (or self hosted with a server, but still needs a running server). A lot of times I was doing more complex things than graphing the validation loss over epochs and the web UI seemed claustrophobic compared to the freedom I had when I could simply read some files into a dataframe. Others like [Kubeflow](https://www.kubeflow.org), [codalab](https://codalab.org) seemed heavy and imposed restrictions on how and where I ran my code. 

In my opinion, a one stop solution doesn't exist, which is what these tools are trying to do (and sell). People need different graphs, complex filters and have differing privacy and collaboration requirements. And plus ML practioners are typically good at and don't need help manipulating data and plotting graphs. With meticulous I had something that was lightweight (no server), collaborative yet private (comes free with the filesystem), readable (human readable file format) and extensible (experiments as Python objects). A major aspect was defining a standardized specification for what gets stored and where. So I decided to put some weekends into re-examining all the design decisions, cleaning up code, adding basic tests and preparing to release (or rather publicize) meticulous. 






