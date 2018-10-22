
# Set to None to use all rows
SAMPLE_N_ROWS = 10

import pandas as pd
import re
import matplotlib.pyplot as plt

# Tested with concorances and neologismen csv files from neoloog database for the year 2015
DATA_DIR = "data/"
CONCORD_FILE = DATA_DIR + "concordanties.csv"
NEO_FILE = DATA_DIR + "neologismen.csv"
RANDOM_STATE=11

def remove_unfinished_sentences(text):
    # Remove unfinished sentence at end
    # Match string after last .?!, this corresponds to an unfinished sentence
    text = re.sub(pattern=r"(?<=[!?.]\s(?!.*[!?.])).*$", repl="", string=text)
    # Remove unfinished sentence at start:
    # Sentence which starts with lower case letter and ends with .?! (and  a space optionally)
    text = re.sub(pattern=r"^[a-z].*?[\.\?\!]\s*", repl="", string=text)
    return text


    
def read_concordances(concord_file):
    df_concordances = pd.read_csv(concord_file)
    return df_concordances

def add_concordances(df_neo, df_concordances):
    df_neo = df_neo.merge(df_concordances, how="left")

    # Only retain rows which have a non-empty "concordanties" field
    df_neo = df_neo[df_neo["concordanties"] != ""]
    # Remove tag in square brackets at the end (all concordances have this)
    df_neo["concordanties"] = df_neo["concordanties"].str.replace(pat=r"\[(.*?)\]$",repl="", regex=True)
    # Remove rows which contain an unclosed tag
    df_neo = df_neo[~df_neo["concordanties"].str.contains("<|>")]

    return df_neo

def write_pybossa_file(df_content):
    df_content["type"]="task"
    # Add first row with user details
    df_header = pd.DataFrame.from_dict({"type": ["userdetails"]})
    df_comb = df_header.merge(df_content, how="outer")
    filename = "neologismen-tasks15"
    filename += ".csv"
    print(df_comb)
    df_comb.to_csv(filename)

def process_neologisms(neo_file, concord_file):
    categories = [{"name":"Untagged", "state_neo":"f", "state_niet_neo":"f"},
                  {"name":"Neologisms", "state_neo":"t", "state_niet_neo":"f"},
                  {"name":"Non-neologisms", "state_neo":"f", "state_niet_neo":"t"}]
    # Load neologisms
    df_neo = pd.read_csv(neo_file)
    # Filter out erroneous entries, which have an "error comment"
    df_neo = df_neo[df_neo["comment"].isna()]
    # Filter out words with numerals
    df_neo = df_neo[~df_neo["woord"].str.contains("\d")]
    # Filter out declined forms
    df_neo = df_neo[df_neo["lemma"] == df_neo["woord"]]

    df_concordances = read_concordances(concord_file)

    # Create output df
    df_output = pd.DataFrame()
    for cat in categories:
        df_cat = df_neo[(df_neo["neo"]==cat["state_neo"]) & (df_neo["niet_neo"]==cat["state_niet_neo"])]
        df_neo_concord = add_concordances(df_cat, df_concordances)
        df_neo_concord_sample = df_neo_concord.sample(n=5, random_state=RANDOM_STATE)
        df_output = df_output.append(df_neo_concord_sample)
    df_output_shuffle = df_output.sample(frac=1)
    return df_output_shuffle




def main():
    neologisms = process_neologisms(NEO_FILE,  CONCORD_FILE)
    write_pybossa_file(neologisms)

    

if __name__ == "__main__":
    main()
