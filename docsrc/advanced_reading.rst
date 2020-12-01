Programmatic Reading
====================

While all the records are kept in a human-readable format on the file system, there are some convenience functions to help you access it programmatically.

Reading a single experiment
---------------------------
:py:class:`ExperimentReader <meticulous.experiments.ExperimentReader>` takes in the path to the experiment directory
and reads all the stored information as object attributes. Exact attributes can be found in the API docs.

If you are storing any other information for each experiment that you would like to include, you can subclass
:py:class:`ExperimentReader <meticulous.experiments.ExperimentReader>`.

Reading all experiments
-----------------------
:py:class:`Experiments <meticulous.experiments.Experiments>` is a utility class to load the entire experiments folder.
You can point it to a particular ``project_directory`` and an ``experiments_directory``. You can also override the ``reader``
which is used internally to read all the experiments, with a subclassed version of :py:class:`ExperimentReader <meticulous.experiments.ExperimentReader>`.

You can access individual experiments by indexing with the experiment id, as follows::

    exps = Experiments()
    exps['2'].metadata

:py:func:`Experiments.as_dataframe() <meticulous.experiments.Experiments.as_dataframe>`  returns the metadata, args and
summary as a Pandas dataframe upon which you can build custom views. For example

- Filter by start/end times
- Order by summary statistic
- Group by certain args
- Aggregate over many random seeds

This requires some Pandas knowledge. Recipes to put together a dashboard are TBD.
