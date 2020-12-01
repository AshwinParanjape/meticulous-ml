.. Meticulous documentation master file, created by
   sphinx-quickstart on Sat Nov 28 22:22:49 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

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


.. toctree::
   :maxdepth: 1
   :caption: User guide
   :hidden:

   Introduction <index>
   Getting started <getting_started>
   Advanced options <advanced_tracking>
   Listing on commandline <listing_on_cmd>
   Programmatic reading <advanced_reading>

.. toctree::
   :maxdepth: 1
   :caption: API Documentation
   :hidden:

   meticulous.experiment
   meticulous.experiments
   meticulous script <meticulous_cmd>


..
 Indices and tables
 ==================

..
 * :ref:`genindex`
..
 * :ref:`modindex`
..
 * :ref:`search`
