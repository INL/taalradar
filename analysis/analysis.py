import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import errno
import numpy as np
from collections import defaultdict, Counter

projects = [{'name':'Blends analysis',
              'runs_filename': 'results-sept2018/analyse_task_run.json',
              'gold_filename': 'results-sept2018/blends-analyse-10.csv',
              'type': 'analyse'},
             {'name': 'Blends recognition',
              'runs_filename': 'results-sept2018/herken1_task_run.json',
              'gold_filename': 'results-sept2018/blends-herken1-10.csv',
              'type': 'herken1'}]
details = ["gender","age","location"]

def get_runs_df(json_filename):
    if not os.path.isfile(json_filename):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), json_filename)
    df_data = pd.read_json(json_filename,orient="records")
    return df_data

def get_gold_dict(csv_filename, data_type):
    df = pd.read_csv(csv_filename)
    gold_dict = {}
    for index,row in df.iterrows():
        if data_type == 'analyse':
            key=row['lemma']
            comp1=row['basiswoord1']
            comp2=row['basiswoord2']
            value=[comp1,comp2]
        elif data_type == 'herken1':
            key=row['voorbeeld1']
            word = row['lemma']
            value = [word]
        gold_dict[key] = value
    return gold_dict

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
    category_df = pd.DataFrame.from_records(category_items, columns = [dataType,y_label])

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
        plt.savefig(title + " " + prop_c + ".png")

def main():
    for proj in projects:
        # Retrieve runs from file
        df = get_runs_df(proj["runs_filename"])
        # Analyze personal details
        details_fields = df[df['info'].map(is_details)]
        analyze_details(details_fields['info'], proj["name"])

        # Analyze answers
        gold_dict = get_gold_dict(proj["gold_filename"], data_type=proj["type"])
        answer_fields = df[df['info'].map(not is_details)]
        print(answer_fields["info"])
        

if __name__ == "__main__":
    main()