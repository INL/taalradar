
# Set to None to use all rows
SAMPLE_N_ROWS = 10

import pandas as pd
import re
import matplotlib.pyplot as plt

# Tested with concordances and neologismen csv files from neoloog database for the year 2015 and 2016-2018
CONCORD_FILE_TAGGED = "data/tagged/neo-concordanties-2015.csv"
NEO_FILE_TAGGED = "data/tagged/neo-neologismen-2015.csv"
CONCORD_FILE_UNTAGGED = "data/untagged/neo-concordanties-2016-2018.csv"
NEO_FILE_UNTAGGED = "data/untagged/neo-neologismen-2016-2018.csv"
RANDOM_STATE=11

def remove_unfinished_sentences(text):
    # Remove unfinished sentence at end
    # Match string after last .?!, this corresponds to an unfinished sentence
    text = re.sub(pattern=r"(?<=[!?.]\s(?!.*[!?.])).*$", repl="", string=text)
    # Remove unfinished sentence at start:
    # Sentence which starts with lower case letter and ends with .?! (and a space optionally)
    text = re.sub(pattern=r"^[a-z].*?[\.\?\!]\s*", repl="", string=text)
    return text


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
    print("Writing to file")
    df_content["type"]="task"
    # Add first row with user details
    df_header = pd.DataFrame.from_dict({"type": ["userdetails"]})
    df_comb = df_header.merge(df_content, how="outer")
    filename = "neologismen-tasks"
    filename += ".csv"
    df_comb.to_csv(filename)

def read_concordances(concord_file):
    return pd.read_csv(concord_file, engine="c")

def read_filter_neologisms(neo_file):
    # Load neologisms
    df_neo = pd.read_csv(neo_file, engine="c")
    # Filter out erroneous entries, which have an "error comment"
    df_neo = df_neo[df_neo["comment"].isna()]
    # Filter out words with numerals
    df_neo = df_neo[df_neo["woord"].str.match(r"^[A-Za-z]+[A-Za-z\-]+$")]
    # Filter out declined forms
    df_neo = df_neo[df_neo["lemma"] == df_neo["woord"]]
    return df_neo

def process_neologisms(neo_file_tagged, concord_file_tagged, neo_file_untagged, concord_file_untagged):
    print("Reading files")
    # Read tagged file
    df_neo_tagged = read_filter_neologisms(neo_file_tagged)
    df_concordances_tagged = read_concordances(concord_file_tagged)

    # Read untagged file
    df_neo_untagged = read_filter_neologisms(neo_file_untagged)
    df_concordances_untagged = read_concordances(concord_file_untagged)


    # Define categories: dataframes of neologisms, non-neologisms and untagged, from both files
    categories = [{"name":"Untagged", "df": df_neo_untagged[df_neo_untagged["datum"].str.startswith("2018")], "concord_lookup": df_concordances_untagged},
                  {"name":"Neologisms", "df": df_neo_tagged[df_neo_tagged["neo"]=="t"], "concord_lookup": df_concordances_tagged},
                  {"name":"Non-neologisms", "df": df_neo_tagged[df_neo_tagged["neo"]=="f"], "concord_lookup": df_concordances_tagged}]

    print("Filtering and combining dataframes")
    # Create output df
    df_output = pd.DataFrame()
    for cat in categories:
        df_neo_cat = cat["df"]
        df_concord_lookup_cat = cat["concord_lookup"]
        df_neo_concord = add_concordances(df_neo_cat, df_concord_lookup_cat)
        df_neo_concord_sample = df_neo_concord.sample(n=10, random_state=RANDOM_STATE)
        print(cat["name"])
        df_neo_concord_sample[["woord","datum","concordanties"]].to_csv(cat["name"]+"-test.tsv",sep="\t",index=False)
        df_output = df_output.append(df_neo_concord_sample)
    df_output_shuffle = df_output.sample(frac=1)
    return df_output_shuffle




def main():
    neologisms = process_neologisms(NEO_FILE_TAGGED,  CONCORD_FILE_TAGGED, NEO_FILE_UNTAGGED, CONCORD_FILE_UNTAGGED)
    write_pybossa_file(neologisms)

    

if __name__ == "__main__":
    main()
