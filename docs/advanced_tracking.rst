Advanced recording
==================

Using a config file instead of argparse
--------------------------------------
``Experiment`` class can be directly initialized with the experiment's arguments provided as a dictionary. 

.. code:: python

	args = {'batch_size': 10, 'learning_rate': 0.0001}
	experiment = Experiment(args)

It also takes ``default_args`` which come in handy later on to find the runs whose args deviate from defaults. 

Skipping checks during development
----------------------------------
You can skip meticulous check and tracking entirely by setting ``norecord=True``. 
This is useful during development and debugging to not have to commit code for after change. 
And also avoid littering experiments directory from unwanted experiments
 
Running from outside the git repo
---------------------------------
The working directory is assumed to be the project directory by default, but it can be explicitly provided to the ``Experiment`` constructor as follows 

.. code:: python

	experiment = Experiment(project_directory='/home/user/project/repo/')

Saving experiments to a custom directory
----------------------------------------
By default experiments are stored in a new `experiments` directory within the project directory. 
You can provide an explicit directory as well. 
If a relative path is provided, it will be considered relative to the project directory. 

.. code:: python

	experiment = Experiment(experiments_directory='custom_experiments_directory')

Specifying an experiment id
---------------------------
Meticulous assigns the next integer experiment id by default. 
You can override that behaviour by supplying it explicitly and it need not be an integer

.. code:: python

	experiment = Experiment(experiment_id='my_special_experiment')



Overriding argparse defaults
----------------------------



Saving files
------------
You can use the ``experiment`` object to open files in the current experiment's directory. For e.g. 

.. code:: python

  with experiment.open('model.pkl', 'wb') as f:
      pkl.dump(weights, f)
  ...


Saving summary
--------------
You can also store a summary of the experiment so far. This is a json file that gets overwritten everytime ``summary`` is called. This file has a special meaning because it is read and shown by the meticulous reader. 

.. code:: python

  experiment.summary({'loss': loss, 'accuracy': accuracy})


Resuming experiments
--------------------
You can resume an experiment by providing its experiment id. 
You can load the checkpoint by using the ``open`` function that will open files from the folder for that experiment.  
Meticulous will throw an error if the arguments and the commit id have changed. 


