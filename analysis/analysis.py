import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import errno
import numpy as np
from collections import defaultdict, Counter

filenames = [('Blends analysis', 'results-sept2018/analyse_task_run.json'), ('Blends recognition', 'results-sept2018/herken1_task_run.json')]
details = ["gender","age","location"]

def get_df(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)
    df_data = pd.read_json(filename,orient="records")
    return df_data

def is_details(field):
    # Info field should contain all of: gender,age,location
    
    return all(key in field for key in details)

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def convert_to_int(data):
    return_dist = []
    for value in data:
        if is_number(value):
            return_dist.append(int(value))
    return return_dist

def fix_case(value):
    # Only capitalize first word, leave rest of case as is
    value_split = value.split(' ')
    first_word = value_split[0].capitalize()
    rest = value_split[1:]
    fixed_word = first_word
    if len(rest) > 0:
        fixed_word += " " +  " ".join(rest)
    return fixed_word
    

def categorical_df(data, dataType, y_label):
    if dataType == "Location":
        data_clean = [fix_case(value) for value in data]
        print(data_clean)
        # Replace '' by not_given
        data_clean =  ["Not given" if value=='' else value for value in data_clean]
        category_items = list(Counter(data_clean).most_common(10))
    elif dataType == "Gender":
        mapping = {"Man":"Male",
                   "Vrouw": "Female",
                   "Anders": "Other",
                   "Zeg ik niet": "Not given"}
        data_clean = [mapping[value] for value in data]
        category_dict = Counter(data_clean)
        category_items = list(category_dict.items())
    print(category_items)
    category_df = pd.DataFrame.from_records(category_items, columns = [dataType,y_label])
    print(category_df)

    return category_df

    


def analyze_details(info_fields, title):
    y_label = '# participants'
    for prop in details:
        prop_c = prop.capitalize()
        data = [d[prop] for d in info_fields]
        plt.subplots(figsize=(10,5))
        if prop_c == "Age":
            data_int = convert_to_int(data)
            ax = sns.distplot(data_int, kde=False, bins=20)
        else:
            cat_df = categorical_df(data, prop_c, y_label)
            ax = sns.barplot(x=prop_c, y=y_label, data=cat_df)
        ax.set(xlabel=prop_c, ylabel=y_label)
        plt.title(title)
        plt.show()

def main():
    for (proj,filename) in filenames:
        df = get_df(filename)
        details_fields = df[df['info'].map(is_details)]
        analyze_details(details_fields['info'], proj)
        

if __name__ == "__main__":
    main()