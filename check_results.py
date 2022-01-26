import pandas as pd
import json
import pathlib
import os

def check_for_empties(evallist):
    if len(evallist)==0:
        return(True)
    else:
        return(False)

script_path = pathlib.Path(__file__).parent.absolute()
results_path = os.path.join(script_path,'results/')
results_file = os.path.join(results_path,'altmetric_annotations.json')

with open(results_file,'r') as inputfile:
    jsoninfo = pd.read_json(inputfile)

jsoninfo['is_empty?'] = jsoninfo.apply(lambda row: check_for_empties(row['evaluations']),axis=1)
print("sample data: ")
print(jsoninfo.head(n=2))
print("number of entries: ",len(jsoninfo))

null_vals = jsoninfo.loc[jsoninfo['is_empty?']==True]
print("empty evals: ",len(null_vals))