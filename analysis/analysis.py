import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import errno
import numpy as np
from unidecode import unidecode
from collections import defaultdict, Counter
import textwrap

pd.set_option('display.max_columns', 500)

ROUND = 2

if ROUND == 1:
    projects = [{'name':{'en':'Blends analysis', 'nl':'Analyse blends'},
                'runs_filename': 'results-sept2018/analyse_task_run.json',
                'tasks_filename': 'results-sept2018/analyse_task.json',
                'gold_filename': 'results-sept2018/blends-analyse-10.csv',
                'type': 'analyse',
                'question_in_run': False,
                'question_field': 'lemma',
                'answer_fields': ['component1', 'component2']},
                {'name': {'en':'Blends recognition', 'nl':'Herkennen blends'},
                'runs_filename': 'results-sept2018/herken1_task_run.json',
                'tasks_filename': 'results-sept2018/herken1_task.json',
                'gold_filename': 'results-sept2018/blends-herken1-10.csv',
                'type': 'herken1',
                'question_in_run': False,
                'question_field': 'lemma',
                'answer_fields': None}]
if ROUND == 2:
    projects = [{'name':{'en':'New words', 'nl':'Nieuwe woorden'},
                'runs_filename': 'results-drongo-until20190102/nieuwewoorden_task_run.json',
                'tasks_filename': 'results-drongo-until20190102/nieuwewoorden_task_local.json',
                'type': 'nieuwewoorden',
                'question_in_run': True,
                'question_field': 'woord',
                'answer_fields': ['houdbaar', 'divers']},
                {'name': {'en':'Language variation', 'nl':'Taalvariatie'},
                'runs_filename': 'results-drongo-until20190102/taalvariatie_task_run.json',
                'tasks_filename': 'results-drongo-until20190102/taalvariatie_task.json',
                'type': 'taalvariatie',
                'question_in_run': True,
                'question_field': 'question',
                'answer_fields': ['word1', 'word2']}]

details = [("gender","geslacht"),("age","leeftijd"),("location","woonplaats")]
details_languagevariation = [("province", "provincie"), ("city","woonplaats"), ("motherTongue", "moedertaal"), ("age", "leeftijd"), ("gender", "geslacht"), ("education", "opleiding")]

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
    # Info field should contain all of normal details (gender/age/location)
    # or all of language variation detatils
    # Use English details key as ID
    return all(key_en in field for key_en,_ in details) or all(key_en in field for key_en,_ in details_languagevariation)


# Return the details array that corresponds to this record:
# normal details (gender/age/location) or language variation detatils
def get_details_array(field):
    for details_array in [details, details_languagevariation]:
        if all(key_en in field for key_en,_ in details_array):
            return details_array



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
    
def categorical_df(data, dataType, proj_type, x_label, y_label, lang="en"):
    data = [v for v in data if v is not None]
    if dataType == "Location" or dataType == "City":
        data_clean = [value.title() for value in data]
        # Replace '' by not_given
        if lang=="en":
            data_clean =  ["Not given" if value=='' else value for value in data_clean]
        elif lang=="nl":
            data_clean =  ["Onbekend" if value=='' else value for value in data_clean]
        category_items = list(Counter(data_clean).most_common(10))
    elif dataType == "Age" and (proj_type=="analyse" or proj_type=="herken1" or proj_type=="nieuwewoorden"):
        # For age data from blends projects: first create histogram
        hist, bin_edges = np.histogram(data,bins=np.linspace(0,100,11))
        # Convert NP histogram to items list, suitable for dataframe
        category_items = []
        for i,cur_edge in enumerate(bin_edges):
            if i > 0:
                # Create interval label: eg. 0-10
                interval = "{:.0f}".format(bin_edges[i-1])+"-" + "{:.0f}".format(cur_edge)
                # Save right value to dict
                category_items.append( (interval,hist[i-1]) )
    else:
        # For all other data types: create normal categorical bar graph
        if (dataType == "Gender" and lang== "en"):
            mapping = {"Man":"Male",
                    "Vrouw": "Female",
                    "Anders": "Other",
                    "Zeg ik niet": "Not given"}
            data = [mapping[value] for value in data]
        category_dict = Counter(data)
        category_items = list(category_dict.items())
    category_df = pd.DataFrame.from_records(category_items, columns = [x_label,y_label])
    # For gender, we want always same order of bars
    # For location, show descending on frequency
    if dataType=="Gender":
        category_df.sort_values(by=x_label, axis=0, inplace=True)
    else:
        category_df.sort_values(by=y_label, axis=0, ascending=False, inplace=True)
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
    print(df.iloc[0]["info"])
    return df.iloc[0]["info"][proj["question_field"]]


def barplot(x,y,data,title, lang="en", plot_width=14):
    # Get x labels, wrap them, and put them back in data fram
    data_plot = data.copy()
    labels = data_plot[x]
    labels = wrap(labels, width=15)
    data_plot[x] = labels

    plt.subplots(figsize=(plot_width,8.5))
    ax = sns.barplot(x=x, y=y, data=data_plot)
    ax.set(xlabel=x, ylabel=y)
    plt.title(title)
    title_us = "_".join(title.split())
    plt.savefig(title_us + "-" + x + "-" + lang +".png")
    plt.close()

'''def distplot(x,y,data,title, lang="en"):
    plt.subplots(figsize=(10,5))
    ax = sns.distplot(data, kde=False, bins=20)
    ax.set(xlabel=x, ylabel=y)
    plt.title(title)
    title_us = "_".join(title.split())
    plt.savefig(title_us + "-" + x + "-" + lang + ".png")
    plt.close()'''

def analyze_details(info_fields, title, proj_type):
    title_en = title["en"]
    print(title_en + " # participants "+ ": " + str(len(info_fields.index)))
    y_label_en = '# participants'
    y_label_nl = 'aantal deelnemers'
    # Infer details from data: we do not know which type it is, normal or language variation
    cur_details = get_details_array(info_fields.iloc[0])
    for (prop_en, prop_nl) in cur_details:
        # Use English prop as ID
        prop_en_c = prop_en.capitalize()
        prop_nl_c = prop_nl.capitalize()
        data = [d[prop_en] for d in info_fields]
        if prop_en_c == "Age" and (proj_type=="analyse" or proj_type=="herken1" or proj_type=="nieuwewoorden"):
            data = convert_to_int(data)
        
        # English barplot
        cat_df_en = categorical_df(data, dataType=prop_en_c, proj_type=proj_type, x_label=prop_en_c, y_label=y_label_en)
        barplot(x=prop_en_c, y=y_label_en, data=cat_df_en, title=title_en, lang="en")
        # Dutch barplot
        cat_df_nl = categorical_df(data, dataType=prop_en_c, proj_type=proj_type, x_label=prop_nl_c, y_label=y_label_nl, lang="nl")
        barplot(x=prop_nl_c, y=y_label_nl, data=cat_df_nl, title=title["nl"], lang="nl")
        # Only English table
        cat_df_en.to_csv(title_en+ "_" + prop_en_c + ".tsv", sep="\t", index=False)

def plot_score(score, x, y, title, lang="en"):
    # Convert score dict to df
    score_items = list(score.items())
    score_df = pd.DataFrame.from_records(score_items, columns = [x,y])
    labels = score_df[x]
    labels_new = wrap(labels, width=15)
    print(labels_new)
    score_df[x] = labels_new
    barplot(x,y,score_df,title, lang, plot_width=14)

# Remove a prefix for every item in an array
def remove_affixes(prefixes, suffixes, array):
    for prefix in prefixes:
        array = [s[len(prefix):] if s.startswith(prefix) else s for s in array]
    for suffix in suffixes:
        array = [s[:-len(suffix)] if s.endswith(suffix) else s for s in array]
    return array

def wrap(string_array, width):
    # Always wrap on dash, regardless of width
    string_array = [s.replace("-","-\n") for s in string_array]
    # Also wrap line if it exceeds width
    return ["\n".join(textwrap.wrap(s,width=width)) for s in string_array]

# Remove items from array, if available
def remove_items(items, array):
    for item in items:
        array = [f for f in array if f != item]
    return array

def analyze_neologisms(answer_records, df_tasks, project):
    # Appply pd.Series to unpack dict in column to multiple columns
    answer_info = answer_records["info"].apply(pd.Series)
    print(answer_info)
    tasks_info = df_tasks["info"].apply(pd.Series)
    tasks_info = tasks_info[tasks_info["type"]=="task"]
    print(tasks_info)
    merged = answer_info.merge(tasks_info, how="outer", on=["woord", "id"])
    ### Analyze per task_type (untagged/neo/nonneo), and then per word
    word_stats_cat = defaultdict(list)
    word_stats_df = {}
    for task_type, df_task in list(merged.groupby('task_type'))+ [("general", merged)]:
        for woord, df_word in df_task.groupby('woord'):
            record = create_word_record(df_word, woord)
            word_stats_cat[task_type].append(record)
        print(task_type)
        word_stats_df[task_type] = pd.DataFrame.from_records(word_stats_cat[task_type], columns=["woord", "n_sustainable", "n_diverse", "n_total", "perc_sustainable", "perc_diverse", "task_type"])

        print("Most sustainable")
        most_sustainable = sort_df(word_stats_df[task_type], prop="sustainable", title=task_type)
        print(most_sustainable)
        print("Most diverse")
        most_diverse = sort_df(word_stats_df[task_type], prop="diverse", title=task_type)
        print(most_diverse)

def clean(all_answers):
    all_answers = [s.strip('.,!?- ') for s in all_answers]
    all_answers = remove_affixes(prefixes=['een ', 'de ', 'het '], suffixes=[], array=all_answers)
    all_answers = remove_items(items=[''], array=all_answers)
    all_answers = [w.lower() for w in all_answers]
    return all_answers

def analyze_langvar(answer_records, details_records, project):
    # Appply pd.Series to unpack dict in column to multiple columns
    answer_records_expand = pd.concat([answer_records.drop(['info'], axis=1), answer_records['info'].apply(pd.Series)], axis=1)
    
    details_records_expand = pd.concat([details_records[["user_ip", "user_id"]], details_records['info'].apply(pd.Series)], axis=1)

    # Add user details to answers
    merged = answer_records_expand.merge(details_records_expand, how="outer", on=["user_ip", "user_id"])
    
    ### Analyze per question
    for question, df_question in merged.groupby('question'):
        #answers_question = {}
        df_question_answers = pd.DataFrame()
        provinces = []
        for province, df_province in list(df_question.groupby('province')) + [("Overall", df_question)]:
            provinces.append(province)
            all_answers = list(df_province["word1"]) + list(df_province["word2"])
            all_answers = clean(all_answers)
            counter = list(Counter(all_answers).items())
            df_counter_province = pd.DataFrame.from_records(counter, columns = ["user input", province])
            df_counter_province = df_counter_province.set_index("user input")
            df_question_answers = pd.concat([df_question_answers, df_counter_province], axis=1, sort=False)
        df_question_answers = df_question_answers.sort_values(by="Overall", ascending=False)
        df_sum = df_question_answers.sum()
        df_question_answers_rel = df_question_answers / df_sum.replace({0:np.nan})
        # Compute per country
        provinces_vlg = ["Antwerpen", "Limburg (BE)", "Vlaams-Brabant", "West-Vlaanderen"]
        provinces_nl = ["Drenthe", "Flevoland", "Friesland", "Gelderland", "Limburg (NL)", "Noord-Brabant", "Noord-Holland", "Overijssel", "Utrecht", "Zuid-Holland"]
        df_country = pd.DataFrame()
        df_country["Flanders"] = df_question_answers[provinces_vlg].sum(axis=1)
        df_country["The Netherlands"] = df_question_answers[provinces_nl].sum(axis=1)
        #df_country = df_country.sort_values(by="The Netherlands", ascending=False)
        df_country_sum = df_country.sum()
        df_country_rel = df_country / df_country_sum.replace({0:np.nan})

        #print(df_country_rel["Flanders"].argmax(), df_country_rel["The Netherlands"].argmax())

        # Write
        write_csv(df_question_answers, path = os.path.join("Language variation/","absolute"), filename=question+".tsv", float_format="%.0f")
        write_csv(df_question_answers_rel, path = os.path.join("Language variation/","relative"), filename=question+".tsv")
        write_csv(df_sum, path = os.path.join("Language variation/","total"), filename=question+".tsv", float_format="%.0f")
        write_csv(df_country, path = os.path.join("Language variation/","country"), filename=question+".tsv", float_format="%.0f")
        write_csv(df_country_rel, path = os.path.join("Language variation/","country-relative"), filename=question+".tsv")
        write_csv(df_country_sum, path = os.path.join("Language variation/","country-sum"), filename=question+".tsv", float_format="%.0f")

def write_csv(df, path, filename, float_format="%.2f"):
    if not os.path.exists(path):
        os.makedirs(path)
    path_file = os.path.join(path, filename)
    df.to_csv(path_file, sep="\t", index=True, float_format=float_format)
        

def create_word_record(df_word, woord):
    n_sustainable = df_word["houdbaar"].value_counts()[True]
    n_diverse = df_word["divers"].value_counts()[True]
    n_total = len(df_word)
    perc_sustainable = n_sustainable / n_total
    perc_diverse = n_diverse / n_total
    record = {"woord": woord, "n_sustainable": n_sustainable, "n_diverse": n_diverse, "n_total": n_total, "perc_sustainable": perc_sustainable, "perc_diverse": perc_diverse, "task_type": df_word["task_type"].iloc[0] }
    return record

def sort_df(df, prop, title):
    #cols = ["woord", "n_"+prop, "n_total" ,"perc_"+prop]
    sdf = df.sort_values(by="perc_"+prop, ascending=False)
    sdf.to_csv("taalradar-" + title+"-" +  prop +".tsv", sep="\t", index=False, float_format="%.3f")
    return sdf

def analyze_answers(answer_records, df_tasks, gold_dict, project):
    score = defaultdict(float)
    title_en = project["name"]["en"]
    title_nl = project["name"]["nl"]
    for task_id, runs_per_task in answer_records.groupby('task_id'):
        if not project["question_in_run"]:
            # Extract question from task
            task_question = get_task_question_from_id(task_id, df_tasks, project)
        # Else: extract question from task run, we do this in next loop
        correct = 0.0
        total = 0.0
        all_answers = []
        for _,row in runs_per_task.iterrows():
            info = row["info"]
            # Extract question from task run
            task_question = info[project["question_field"]]
            # If all answers are not saved as dict structure, but on the highest level
            if project["answer_fields"] is None:
                if isinstance(info, list):
                    user_answer = info
                else: # Unrecognized type, probably empty string
                    user_answer = []
                if (len(user_answer) == 0) or (all([x=='' for x in user_answer])):
                    user_answer = ["Do not know"]
                user_answer_set = set([i.lower().strip() for i in user_answer])
            # If answers saved in dictionary structure
            else:
                user_answer = {k:v for k,v in info.items() if k in project["answer_fields"]}
                #if project["type"] is "nieuwewoorden":
                #    user_answer_set = str(user_answer["houdbaar"])
                #else:
                user_answer_values = user_answer.values()
                user_answer_set = set([i.lower().strip() for i in user_answer_values])
                user_answer_set.discard('')
            if gold_dict:
                if contains_all(gold_dict[task_question],user_answer_set):
                    correct += 1
                total += 1
            if project["type"] is "herken1" or project["type"] is "analyse":
                all_answers.append(",".join(user_answer_set))
            elif project["type"] is "taalvariatie":
                # Treat multiple options users give as separate answers
                all_answers += user_answer_set
            #elif project["type"] is "nieuwewoorden":
            #    all_answers.append(user_answer_set)
        if project["type"] is "taalvariatie":
            all_answers = remove_affixes(prefixes=['een ', 'de ', 'het '], suffixes=['.', ',', '!', '?', ' ', '-'], array=all_answers)
            all_answers = remove_items(items=[''], array=all_answers)
        counter = Counter(all_answers).most_common(10)
        counter_df = pd.DataFrame.from_records(counter, columns = ["user input", "frequency"])
        counter_df.to_csv(title_en+"-" +  task_question +".tsv", sep="\t", index=False)
        if gold_dict:
            score[task_question] = correct / total
        else:
            barplot(x=counter_df.columns[0], y=counter_df.columns[1], data=counter_df, title=title_en+"-" +  task_question, lang="en")
    if gold_dict:
        # Plot EN
        plot_score(score, x="word", y="accuracy", title=title_en, lang="en")
        # Plot NL
        plot_score(score, x="woord", y="nauwkeurigheid", title=project["name"]["nl"], lang="nl")


def main():
    for proj in projects:
        # Retrieve runs from file
        df_runs = get_df(proj["runs_filename"])
        df_tasks = get_df(proj["tasks_filename"])
        # Analyze personal details
        details_records = df_runs[df_runs['info'].map(is_details)]
        analyze_details(details_records['info'], proj["name"], proj["type"])

        # Analyze answers, round 1
        answer_records = df_runs[df_runs['info'].map(is_answer)]
        if ROUND==1:
            gold_dict = get_gold_dict(proj["gold_filename"], proj)
            analyze_answers(answer_records, df_tasks, gold_dict, proj)
        elif ROUND ==2:
            if proj["type"] == "nieuwewoorden":
                continue
                analyze_neologisms(answer_records, df_tasks, project=proj)
            elif proj["type"] == "taalvariatie":
                analyze_langvar(answer_records, details_records, project=proj)
            else: # this should not happen in principle
                analyze_answers(answer_records, df_tasks, gold_dict=None, project=proj)

if __name__ == "__main__":
    main()