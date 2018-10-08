import json
import pandas as pd
import matplotlib.pyplot as plt

projects = ['analyse', 'herken1']

def get_df(project):
    filename = project + "_task_run.json"
    df_data = pd.read_json(filename,orient="records")
    return df_data

def is_details(field):
    # Info field should contain all of: gender,age,location
    details = ["gender","age","location"]
    return all(key in field for key in details)

def analyze_details(info_fields):
    genders = [d['gender'] for d in info_fields]
    ages = [d['age'] for d in info_fields]
    locations = [d['location'] for d in info_fields]
    plt.hist(x=ages, bins=[20,30,40,65])
    plt.show()

def main():
    for proj in projects:
        df = get_df(proj)
        details_fields = df[df['info'].map(is_details)]
        print(details_fields)
        histograms = analyze_details(details_fields['info'])
        

if __name__ == "__main__":
    main()