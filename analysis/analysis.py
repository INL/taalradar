import json
import pandas as pd
import matplotlib.pyplot as plt
import os
import errno
import numpy as np

filenames = ['results-sept2018/analyse_task_run.json', 'results-sept2018/herken1_task_run.json']
details = ["gender","age","location"]

def get_df(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)
    df_data = pd.read_json(filename,orient="records")
    return df_data

def is_details(field):
    # Info field should contain all of: gender,age,location
    
    return all(key in field for key in details)

def process_distribution(data, type):
    pass

def analyze_details(info_fields):
    distribution = {}    
    for prop in details:
        distribution[prop] = [d[prop] for d in info_fields]
        if prop=="age":
            data = process_distribution(distribution[prop], type="age")
            plt.hist(data, bins=[0,20,40,60,80,100], facecolor='g')
            plt.xlabel(prop)
            plt.ylabel('# participants')
            plt.title('Histogram of ' + prop)
            #plt.axis([0, 100, 0, 150])
            plt.show()

def main():
    for filename in filenames:
        df = get_df(filename)
        details_fields = df[df['info'].map(is_details)]
        histograms = analyze_details(details_fields['info'])
        

if __name__ == "__main__":
    main()