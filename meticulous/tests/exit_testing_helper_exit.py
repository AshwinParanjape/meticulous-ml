from mnist_training_utils import build_training_parser, run_training
from meticulous import Experiment

def forced_exit():
    parser = build_training_parser()
    Experiment.add_argument_group(parser)
    experiment = Experiment.from_parser(parser)
    exit(1)
    run_training(parser, experiment)

if __name__ == '__main__':
    forced_exit()