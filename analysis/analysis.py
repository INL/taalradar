import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import errno
import numpy as np
from unidecode import unidecode
from collections import defaultdict, Counter

projects = [{'name':'Blends analysis',
              'runs_filename': 'results-sept2018/analyse_task_run.json',
              'tasks_filename': 'results-sept2018/analyse_task.json',
              'gold_filename': 'results-sept2018/blends-analyse-10.csv',
              'type': 'analyse',
              'question_field': 'lemma'},
             {'name': 'Blends recognition',
              'runs_filename': 'results-sept2018/herken1_task_run.json',
              'tasks_filename': 'results-sept2018/herken1_task.json',
              'gold_filename': 'results-sept2018/blends-herken1-10.csv',
              'type': 'herken1',
              'question_field': 'lemma'}]
details = ["gender","age","location"]

def get_df(json_filename):
    if not os.path.isfile(json_filename):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), json_filename)
    df_data = pd.read_json(json_filename,orient="records")
    return df_data

def get_gold_dict(csv_filename, project):
    df = pd.read_csv(csv_filename)
    gold_dict = {}
    for index,row in df.iterrows():
        if project["type"] == 'analyse':
            key=row[project["question_field"]]
            comp1=row['basiswoord1']
            comp2=row['basiswoord2']
            value=set([comp1,comp2])
        elif project["type"] == 'herken1':
            key=row[project["question_field"]]
            word = row['lemma']
            value = set([word])
        gold_dict[key] = value
    return gold_dict

def is_details(field):
    # Info field should contain all of: gender,age,location
    return all(key in field for key in details)

def is_answer(field):
    return not is_details(field)

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

# def fix_case(value):
#     # Only capitalize first word, leave rest of case as is
#     value_split = value.split(' ')
#     first_word = value_split[0].capitalize()
#     rest = value_split[1:]
#     fixed_word = first_word
#     if len(rest) > 0:
#         fixed_word += " " +  " ".join(rest)
#     return fixed_word
    

def categorical_df(data, dataType, y_label):
    if dataType == "Location":
        data_clean = [value.title() for value in data]
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

    # For gender, we want always same order of bars
    # For location, show descending on frequency
    if dataType=="Gender":
        category_df.sort_values(by=dataType, axis=0, inplace=True)
    return category_df

# Custom comparison function: check if gold standard contains all elements from answer.
# Answer may possibly have more items.
# Compare case-insensitive
def contains_all(gold, answer):
    answer_lc = [unidecode(a.lower().split(' ')[0]) for a in answer]
    gold_lc = [unidecode(g.lower()) for g in gold]
    for el in gold_lc:
        if el not in answer_lc:
            return False
    return True


def get_task_question_from_id(id, df_tasks, proj):
    df = df_tasks[df_tasks["id"]==id]
    return df.iloc[0]["info"][proj["question_field"]]


def barplot(x,y,data,title, plot_width=10):
    plt.subplots(figsize=(plot_width,6))
    ax = sns.barplot(x=x, y=y, data=data)
    ax.set(xlabel=x, ylabel=y)
    plt.title(title)
    plt.savefig(title + " " + x + ".png")
    plt.close()

def distplot(x,y,data,title):
    plt.subplots(figsize=(10,5))
    ax = sns.distplot(data, kde=False, bins=20)
    ax.set(xlabel=x, ylabel=y)
    plt.title(title)
    plt.savefig(title + " " + x + ".png")
    plt.close()

def analyze_details(info_fields, title):
    print(title + " # participants "+ ": " + str(len(info_fields.index)))
    y_label = '# participants'
    for prop in details:
        prop_c = prop.capitalize()
        data = [d[prop] for d in info_fields]
        if prop_c == "Age":
            data_int = convert_to_int(data)
            distplot(x=prop_c, y=y_label, data=data_int, title=title)
        else:
            cat_df = categorical_df(data, prop_c, y_label)
            barplot(x=prop_c, y=y_label, data=cat_df, title=title)
        cat_df.to_csv(title+ " " + prop_c + ".tsv", sep="\t", index=False)

def plot_score(score, title):
    # Convert score dict to df
    score_items = list(score.items())
    x = "word"
    y = "accuracy"
    score_df = pd.DataFrame.from_records(score_items, columns = [x,y])
    labels = score_df[x]
    labels_new =  ["grachtengordel\ndier" if value=='grachtengordeldier' else value for value in labels]
    score_df[x] = labels_new
    barplot(x,y,score_df,title, plot_width=14)    

def analyze_answers(answer_records, df_tasks, gold_dict, project):
    score = defaultdict(float)
    for task_id, runs_per_task in answer_records.groupby('task_id'):
        task_question = get_task_question_from_id(task_id, df_tasks, project)
        correct = 0.0
        total = 0.0
        all_answers = []
        for n,row in runs_per_task.iterrows():
            info = row["info"]
            if isinstance(info, list):
                user_answer = info
            elif(isinstance(info, dict)):
                user_answer = info.values()
            else: # Unrecognized type, probably empty string
                user_answer = []
            if (len(user_answer) == 0) or (all([x=='' for x in user_answer])):
                user_answer = ["Do not know"]
            user_answer_set = set([i.lower().strip() for i in user_answer])
            if contains_all(gold_dict[task_question],user_answer_set):
                correct += 1
            total += 1
            all_answers.append(",".join(user_answer_set))
        counter = Counter(all_answers).most_common(10)
        counter_df = pd.DataFrame.from_records(counter, columns = ["user input", "frequency"])
        counter_df.to_csv(project['type']+"-" +  task_question +".tsv", sep="\t", index=False)
        score[task_question] = correct / total
    plot_score(score, project["name"])


def main():
    for proj in projects:
        # Retrieve runs from file
        df_runs = get_df(proj["runs_filename"])
        df_tasks = get_df(proj["tasks_filename"])
        # Analyze personal details
        details_records = df_runs[df_runs['info'].map(is_details)]
        analyze_details(details_records['info'], proj["name"])

        # Analyze answers
        gold_dict = get_gold_dict(proj["gold_filename"], proj)
        answer_records = df_runs[df_runs['info'].map(is_answer)]
        analyze_answers(answer_records, df_tasks, gold_dict, proj)
        

if __name__ == "__main__":
    main()