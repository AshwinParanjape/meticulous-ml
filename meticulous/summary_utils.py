import pandas as pd

def informative_cols(dataframe):
    print(dataframe.nunique(dropna=False)>1)
    return [c for c, v in dataframe.nunique(dropna=False).iteritems() if v > 1]

def truncate_constant_cols(dataframe):
    return dataframe[informative_cols(dataframe)]