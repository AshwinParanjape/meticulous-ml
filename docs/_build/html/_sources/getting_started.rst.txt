Getting started
===============
Installation
---------------
Simplest way is to use pip

.. code:: bash

  pip install git+https://github.com/ashwinparanjape/meticulous-ml.git


How to recording an experiment?
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
