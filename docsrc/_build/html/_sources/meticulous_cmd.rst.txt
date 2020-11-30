Meticulous script
=================
The script takes few more optional arguments:

positional arguments:
  :directory:            Directory with stored experiments

optional arguments:
  -h, --help            show this help message and exit
  --args {none,truncated,non-default,all}
                        Display args:
                            :none: don't display args
                            :truncated: removes all values which stay constant across experiments
                            :non-default: shows arguments that modify default values
                            :all: all arguments
  --summary             Show experiment summary

Running the script with ``--args all --summary`` produces::

    $meticulous experiments/ --args all --summary
                                                                                                      args                                                                                   summary
                                     curexpdir           start_time   status status_message batch_size test_batch_size epochs   lr gamma no_cuda dry_run   seed log_interval save_model val_loss
    (, sha)              expid
    64decb56b912b1190... 1      experiments/1/  2020-11-30T00:56...  SUCCESS                        64            1000     14  1.0   0.7   False   False      1           10      False   0.4828
                         2      experiments/2/  2020-11-30T00:58...  SUCCESS                        64            1000     14  0.1   0.7   False   False      1           10      False   0.4853
                         3      experiments/3/  2020-11-30T00:58...  SUCCESS                        64            1000     14  1.0   0.7   False   False  98789           10      False   0.3863

Running the script with ``--args **truncated** --summary`` removes the args which are common to all experiments and declutters the output::

    $meticulous experiments/ --args truncated --summary
                                                                                                args         summary
                                     curexpdir           start_time   status status_message   lr   seed val_loss
    (, sha)              expid
    64decb56b912b1190... 1      experiments/1/  2020-11-30T00:56...  SUCCESS                 1.0      1   0.4828
                         2      experiments/2/  2020-11-30T00:58...  SUCCESS                 0.1      1   0.4853
                         3      experiments/3/  2020-11-30T00:58...  SUCCESS                 1.0  98789   0.3863

