Meticulous-ml
=============
.. image:: https://github.com/AshwinParanjape/meticulous/workflows/tests/badge.svg

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

1. Reads each experiment into an ``ExperimentReader`` object (subclassable). 
2. Creates a Pandas dataframe with all the stored metadata.

Also provided is a handy command-line script (also called ``meticulous``) that provides a quick look at the contents of an experiment folder.

