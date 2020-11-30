Programmatic Reading
====================

While all the records are kept in a human-readable format on the file system, there are some convenience functions to help you access it programmatically.

:py:class:`ExperimentReader <meticulous.experiments.ExperimentReader>` takes in the path to the experiment directory
and reads all the stored information as object attributes. Exact attributes can be found in the API docs.

If you are storing any other information for each experiment and you want to read it as well, you can customize
:py:class:`ExperimentReader <meticulous.experiments.ExperimentReader>` by subclassing it and reading the extra information.

py:class:`ExperimentReader <meticulous.experiments.Experiments>` is a utility class to load the entire experiments folder.
You can point it to a particular ``project_directory`` and an ``experiments_directory``. If you using a subclassed version
of :py:class:`ExperimentReader <meticulous.experiments.ExperimentReader>`, you can provide the class the a parameter
``reader`` which is internally used to read all the experiments.

You can access individual experiments by indexing with the experiment id, as follows::

    exps = Experiments()
    exps['2'].metadata

:py:func:`Experiments.as_dataframe <meticulous.experiments.Experiments.as_dataframe>`  returns the metadata, args and
summary as a Pandas dataframe upon which you can build custom views. For example

- Filter by start/end times
- Order by summary statistic
- Group by certain args
- Aggregate over many random seeds

This requires some Pandas knowledge. Recipes to put together a dashboard are TBD.
