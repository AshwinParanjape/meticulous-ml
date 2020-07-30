# Meticulous

Machine learning research involves iterating over ideas and running multiple experiments. It is easy to forget the changes that were made to the code which made the results worse and hard to keep track of all the arguments to the program that made it work. However, it is important to make a note of the exact setup for research and reproducibility. Meticulous is a python library that makes it easy to record the exact setup of an experiment.

When an experiment is run using Meticulous, it
1. Uses Git to ensure that the code is committed and records the commit-sha
2. Extracts the arguments passed to the program using argparse. 
3. Keeps a copy of program output and has sensible helper functions to record json logs and summaries. 
4. Saves of this information in a new folder for every experiment. 

While the core mission of meticulous is to "meticulously" record the setup of an experiment, it opens the door to advanced use cases such as 
* Summarize progress using an automatically generated dashboard
* Gather all hyperparameter tuning runs performed with the same code
* Perform regression tests to ensure code changes didn't worsen previously obtained results

# Usage
## Installation
Simplest way is to use pip

```bash 
pip install meticulous
```

To install from source, clone the repository and in the `meticulous` directory run

```bash 
python setup.py install
```

## Integration
To integrate with your code, follow these steps
1. Meticulous uses argparse to capture the input arguments. If your program doesn't use argparse, the first step would be to capture all arguments using argparse. 
2. Meticulous uses git to keep track of code state. If you aren't already using git, create a new local repository and commit your code to it
3. In your entrypoint to the program, add the following import `from meticulous import Experiment` and after arguments have been parsed, create an experiment object using `experiment = Experiment(parser)`


That's all that is required for all of the basic functionality (code and argument tracking, output redirection and saving in a new folder)

Advanced usage -
* If you want to expose meticulous specific arguments, use `add_argument_group` staticmethod. This would add a an argument group with meticulous specific arguments. 
* You can also use `ArgumentParser` object (perhaps in conjunction with `add_argument_group`) using the classmethod `from_parser` which reads in the required arguments and creates and experiment object. 
* `experiment.open` - Override the default function with `open = experiment.open` to read and write files from the experiment directory. This is useful to save model files for instance
* `experiment.log()` - Takes a dictionary object and appends it to a log file for the experiment




