# Meticulous
![tests](https://github.com/AshwinParanjape/meticulous/workflows/tests/badge.svg)

Machine learning research involves iterating over ideas and running multiple experiments. And it is important to make a note of the exact setup for research and reproducibility. Meticulous is a python library that makes it easy to record the exact setup of an experiment.

When an experiment is run using Meticulous, it
1. Uses Git to ensure that the code is committed and records the commit-sha
2. Extracts (using argparse) and records the arguments passed to the program.
3. Keeps a copy of program output and has sensible helper functions to record a json summary for the experiment. 
4. Saves all of this information in a new folder for every experiment. 

Why should you use it over anything else - 
1. It has only one purpose, that is to meticulously record your experiments. It has an intentionally small featureset. It does one thing and does it right.
2. It is a very lightweight python script, what you see is what you get. And that makes it hackable, so if it isn't good enough you can adapt it to your usecase.
3. It doesn't make any assumptions about where and how you run/schedule your experiments.
4. It uses git, argparse, pandas and works directly from the terminal. All things you are likely familiar with and like already.

What it doesn't do and won't do - 
1. It won't create nice plots or expose a web-ui. Each researcher, each experiment has different needs and the stregth of meticulous is to support you to roll out your own code on top to suit your needs. 

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
* `experiment.summary()` - Takes a dictionary object and writes it to summary.json




