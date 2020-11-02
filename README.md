# Meticulous
![tests](https://github.com/AshwinParanjape/meticulous/workflows/tests/badge.svg)

Machine learning research involves iterating over ideas and running multiple experiments. And it is important to make a note of the exact setup for research and reproducibility. Meticulous is a python library that makes it easy to record the exact setup of an experiment.

When an experiment is run using Meticulous, it
1. Creates a new numbered folder to record the experiment. 
2. Uses VCS (git) to ensure that the code is committed and records the commit-sha
3. Extracts (using argparse) and records the arguments passed to the program
4. Keeps a copy of program output (stdout and stderr)
5. Provides a helper function to open files in the experiment directory and to save a json summary

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

# Design

ML practioners have very different workflows, with different environments, schedulers and dashboards. And for a good reason, because everyone has different needs. Keeping that in mind, meticulous has the following goals

## Goals 
* Record experiments and setup accurately
* Recorded experiments and setup should be easy to read and access
* Make minimal assumptions about the workflow and work well with other tools
* Be easy to customize and extend according to individual needs
* Encourage best practices by provide opinionated but sensible defaults

Keeping these goals in mind, following choices were made. 

## Choices
* Use git and argparse, which are widely used, to capture the setup.
* Organize experiments using the filesystem in human readable file formats.
* Terminal based script to quickly read and show all experiment data from filesystem.
* Depend only on filesystem and git. No other assumptions about how your experiment is run. 
* Support storing and reading summary metrics which are crucial for knowing which experiments were successful.
* Restrict the featureset to minimize footprint and maximize code readability/extensibility. 
* Doesn't run a server in the background, doesn't have a web UI and doesn't create plots.
* Provide all experiment data as a pandas dataframe and each experiment as a Python object, so that you can write your own code on top on top of it.


# Backstory

As an NLP PhD student I run lots of ML experiments. There is no standard way of keeping track of experiments. Initially I would concatenate all arguments in a single string. Then I moved on to using random 4 letter folder names for each experiment. Then by the time I would meet with my advisor, I would have forgotten which model change caused the results to improve, because that's part of the model and not the arguments. A couple of years ago (2018) I started writing a python script to automate the "keeping track of experiments". 

But then I found myself browsing through the filesystem to find which was the best configuration. So I built a fancy dashboard for myself using a Jupyter notebook. But then I moved to a different project and the project specific dashboard would work no more. So I kept whittling the featureset until I was left with a core that was minimal, which meant it worked across all the different projects and setups. And easily extensible, which meant it satisfied individual needs without much effort. 

Meanwhile many other experiment tracking and management systems were being developed and I was hopeful I could use instead. [Comet.ml](https://www.comet.ml/site/), [Weights & Biases](https://docs.wandb.com) are cloud based (or self hosted with a server, but still needs a running server). A lot of times I was doing more complex things than graphing the validation loss over epochs and the web UI seemed claustrophobic compared to the freedom I had when I could simply read some files into a dataframe. Others like [Kubeflow](https://www.kubeflow.org), [codalab](https://codalab.org) seemed heavy and imposed restrictions on how and where I ran my code. 

In my opinion, a one stop solution doesn't exist, which is what these tools are trying to do (and sell). People need different graphs, complex filters and have differing privacy and collaboration requirements. And plus ML practioners are typically good at and don't need help manipulating data and plotting graphs. With meticulous I had something that was lightweight (no server), collaborative yet private (comes free with the filesystem), readable (human readable file format) and extensible (experiments as Python objects). A major aspect was defining a standardized specification for what gets stored and where. So I decided to put some weekends into re-examining all the design decisions, cleaning up code, adding basic tests and preparing to release (or rather publicize) meticulous. 






