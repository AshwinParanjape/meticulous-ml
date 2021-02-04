import setuptools

long_description = """
Machine learning involves iterating over ideas and running multiple experiments in different configurations. For research and reproducibility (and perhaps sanity), it is important to keep track of the exact setup and resulting output of each run. But extensive bookkeeping is only useful if the data is made easily accessible and usable. Meticulous is a python library to record the setup and the results of experiments in just a few lines of code. All the data is stored locally on the file system in a human readable format. It is also made accessible as Python objects and Pandas dataframes.

When an experiment is run using Meticulous, it

    Creates a new numbered folder to record the experiment.
    Uses VCS (git) to ensure that the code is committed and records the commit-sha.
    Extracts (using argparse) and records the arguments passed to the program.
    Stores a copy of program output (stdout and stderr).
    Provides a helper function to open files in the experiment directory and to save a json summary.

When an experiment folder is read programmatically using Meticulous, it

    Reads each experiment into an ExperimentReader object (subclassable).
    Creates a Pandas dataframe with all the stored metadata.

Also provided is a handy command-line script (also called meticulous) that provides a quick look at the contents of an experiment folder.

Complete documentation is hosted at ashwinparanjape.github.io/meticulous-ml/.
"""
setuptools.setup(
        name = "meticulous",
        version = "0.0.1",
        author = "Ashwin Paranjape",
        author_email = "ashwing.2005@gmail.com",
        description = "Lightweight experiment tracking for Machine Learning",
        long_description = long_description,
        url = "https://github.com/AshwinParanjape/meticulous",
        packages = setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        install_requires=[
            "gitpython",
            "pandas",
            "tabulate"
        ],
        tests_require=[
            'pytest',
        ],
        extras_require={
            'dev': [
                "sphinx",
                "libsass",
            ],
        },
        test_suite='pytest',
        scripts=['bin/meticulous'],
        )
