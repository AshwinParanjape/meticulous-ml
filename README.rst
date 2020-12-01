Meticulous-ml
=============
.. image:: https://github.com/AshwinParanjape/meticulous/workflows/tests/badge.svg

Machine learning involves iterating over ideas and running multiple experiments in different configurations.
For research and reproducibility (and perhaps sanity), it is important to keep track of the exact setup and resulting output of each run.
But extensive bookkeeping is only useful if the data is made easily accessible and usable.
Meticulous is a python library to record the setup and the results of experiments in just a few lines of code.
All the data is stored locally on the file system in a human readable format.
It is also made accessible as Python objects and Pandas dataframes.

When an experiment is run using Meticulous, it

1. Creates a new numbered folder to record the experiment.
2. Uses VCS (git) to ensure that the code is committed and records the commit-sha.
3. Extracts (using argparse) and records the arguments passed to the program.
4. Stores a copy of program output (stdout and stderr).
5. Provides a helper function to open files in the experiment directory and to save a json summary.

When an experiment folder is read programmatically using Meticulous, it

1. Reads each experiment into an ``ExperimentReader`` object (subclassable).
2. Creates a Pandas dataframe with all the stored metadata.

Also provided is a handy command-line script (also called ``meticulous``) that provides a quick look at the contents of an experiment folder.

Complete documentation is hosted at `ashwinparanjape.github.io/meticulous-ml/ <https://ashwinparanjape.github.io/meticulous-ml/>`_.

Why meticulous?
---------------
⭐️   **Good defaults**
    Bookkeeping isn't hard, but it takes some effort to get it right.
    Meticulous comes baked in with good defaults and enforces them to avoid common pitfalls.

🙈   **Minimal assumptions**
    Meticulous doesn't make assumptions about where or how you run the experiments.
    The only assumptions are that code is checked into a git repo and you have access to a filesystem

📐   **Minimalist design**
    The featureset is kept minimal. The entire package is 3 Python classes and less than of 400 lines of Python code.

👩‍💻   **Hackable and extensible**
    An advantage of minimal design is that it is very easy to wrap your head around that is happening under the hood.
    Every project has different needs and meticulous can't meet every project's needs.
    But it can empower you by making it easy for you to extend meticulous and to meet them yourself.

🗃   **Local storage**
    There are no servers, signups or subscriptions. You keep all your data.

❤️ ️ **Made by someone like you**
    This project was born out of a need to streamline ML experimentation for research easily, locally and hackably.
    So there's a good chance you'll like it :)

Getting started
===============
Installation
---------------
Simplest way is to use pip

.. code:: bash

  pip install git+https://github.com/ashwinparanjape/meticulous-ml.git


How to record an experiment?
-------------------------------
Meticulous uses git to keep track of code state. If you aren't already using git, create a new local repository and commit your code to it.

First import ``Experiment`` class

.. code:: python

  from meticulous import Experiment

Then let's say you are using argparse and have a parser that takes in some arguments

.. code:: python

  parser = argparse.ArgumentParser()
  parser.add_argument('--batch-size', type=int, default=64, metavar='N',
                        help='input batch size for training (default: 64)')
  ...

You can add meticulous args as an argument group using the ``add_argument_group`` staticmethod as follows

.. code:: python

  Experiment.add_argument_group(parser)

The "meticulous" argparse group provides following options to customise behaviour

.. code:: bash

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


Then create an object using the ``from_parser`` classmethod, which extracts meticulous args separately from the other args. After that you can extract the non-meticulous args as usual.

.. code:: python

  experiment = Experiment.from_parser(parser)
  args = parser.parse_args()

Your experiment will now be recorded!

What exactly is recorded?
-------------------------
The above code will create a directory structure in your project directory as follows

.. code::

  experiments/
  └── 1
      ├── STATUS
      ├── args.json
      ├── default_args.json
      ├── metadata.json
      ├── stderr
      └── stdout

* ``args.json`` contains the args inferred by the argparse.Parser object
* ``default_args.json`` contains the default args as encoded in the argparse.Parser object
* ``metadata.json`` looks like the following

.. code:: json


  {
      "githead-sha": "970d8ad001f5d42a9ecaa5e3791765d65e02292a",
      "githead-message": "Explicitly close stdout and stderr\n",
      "description": "",
      "timestamp": "2020-11-02T12:48:36.150350",
      "command": [
          "training_utils.py"
      ]
  }

* ``STATUS`` file is either RUNNING, SUCCESS, ERROR with the python traceback.
* ``stdout`` and ``stderr`` files contain the two output streams.

How to get a quick summary?
---------------------------
You can run a utility script ``meticulous`` to list all the experiments in the folder with associated metadata

.. code:: shell

    $ meticulous experiments/
                                     curexpdir           begin_time   status status_message
    (, sha)              expid
    970d8ad001f5d42a9... 1      experiments/1/  2020-11-02T12:48...  SUCCESS


Code snippet
------------
Here are all the above modifications to an example script (assumes you are using argparse)

.. code:: diff

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

Documentation
=============
Complete documentation can be found at `ashwinparanjape.github.io/meticulous-ml/ <https://ashwinparanjape.github.io/meticulous-ml/>`_.