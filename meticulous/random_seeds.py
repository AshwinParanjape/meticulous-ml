"""
Module for generating and logging random seeds.
Parts of this code are inspired by https://github.com/IDSIA/sacred/blob/master/sacred/randomness.py
"""
import random
import sys


def _set_numpy_random_seed(seed):
    # check for numpy
    if "numpy" in sys.modules:
        import numpy.random as npr
        npr.seed(seed)

def _set_torch_random_seed(seed):
    # check for torch
    if "torch" in sys.modules:
        import torch
        torch.manual_seed(seed)
def _set_tensorflow_random_seed(seed):
    # check for tensorflow
    if "tensorflow" in sys.modules:
        import tensorflow as tf
        tf.random.set_seed(seed)
def _set_mxnet_random_seed(seed):
    pass
def _set_cntk_random_seed(seed):
    pass


def set_random_seed(seed):
    random.seed(seed)
    _set_numpy_random_seed(seed)
    _set_torch_random_seed(seed)
    _set_tensorflow_random_seed(seed)

def generate_random_seed():
    """Generate a new random seed. Also set this seed for a number of common machine learning frameworks, if they are available in the current python process. So make sure you import the tool you use before initializing the experiment."""
    seed = random.getrandbits(32)
    set_random_seed(seed)
    return seed