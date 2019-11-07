import requests
import json
import pandas as pd
import time
import os
from collections import defaultdict
import numpy as np
import random
import csv
import argparse


random.seed(5)

pd.set_option('display.max_columns', None)  
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', -1)



#####################################################################################
### CONFIGURATION ###

LEMMAS= ["obesitas", "overgewicht", "kanker", "hartaanval", "beroerte"]
# Number of results for which GDEX scores are calculated,
# according to which the results are ranked.
# Set this is high as possible, to not miss any good results.
# However, for high GDEXCNT, search times can be long.
# For our search terms (diseases, relatively rare), search times are often reasonable,
# because often there are less results available than the GDEXCNT
GDEXCNT = 10000
# Number of results we want to have. This should be lower than GDEXCNT, to get
# only the n best results.
RESULTS_PER_LEMMA_EXTRACTED = 3000
# Name of the corpus, and the used GDEX configuration
# GDEX configuration should be uploaded in your SE account: https://old.sketchengine.co.uk/auth/gdex/ with exact same name
lang_data = {"corpus_name": "user/carole/anwtest", "gdexconf": "crowdfest_GDEX_NL"}
#####################################################################################

BASE_URL = 'https://api.sketchengine.eu/bonito/run.cgi'
# Timeout after 10 minutes: because of long GDEX processing time
REQUEST_TIMEOUT = 10*60
RETRY_INTERVAL = 30
INTER_REQUEST_INTERVAL = 0.0
OFFLINE=False
OUTPUTS = ["tokens", "enriched"]


# create backup directory
BACKUP_DIR = 'backups'
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def parse_concordances(concordances, lemma, results_per_lemma):
    print("   Parsing")
    lines = concordances["Lines"]
    open("output.txt", "w", encoding="utf-8").write(str(concordances))
    total_tokens = []
    total_tags = []
    total_lemmas = []
    total_toknums = []
    for line in lines:
        line_tokens = []
        line_tags = []
        line_lemmas = []
        for position in ["Left", "Kwic", "Right"]:
            for position_obj in line[position]:
                # Remove <s> and </s> strings
                if position_obj["class"]=="strc":
                    continue
                elif position_obj["class"]=="attr":
                    # Linguistic annotation: lemma and pos
                    annotations_split =position_obj["str"].split("/")
                    annot_lemma = annotations_split[1]
                    annot_pos = annotations_split[2]
                    line_lemmas.append(annot_lemma)
                    line_tags.append(annot_pos)
                else:
                    # Other position is token
                    line_tokens.append(position_obj["str"])
        total_tokens.append(line_tokens)
        total_lemmas.append(line_lemmas)
        total_tags.append(line_tags)
        total_toknums.append(line["toknum"])
    # Arrays to fill dataframe
    tokens_records = []
    tokens_enriched_records = []
    for line_tokens, line_lemmas, line_tags, line_toknum in zip(total_tokens,total_lemmas,total_tags, total_toknums):
        tokens_records.append(["".join(line_tokens), line_toknum])
        # Combine tokens and tags with underscore
        tokens_enriched = [token+"/"+lemma+"/"+tag for token,lemma,tag in zip(line_tokens,line_lemmas,line_tags)]
        tokens_enriched_records.append(["".join(tokens_enriched), line_toknum])
    
    # Create DataFrame
    df_tokens = pd.DataFrame(tokens_records, columns=["sentence", "id"])
    df_tokens["lemma"] = lemma
    df_enriched = pd.DataFrame(tokens_enriched_records, columns=["sentence", "id"])
    df_enriched["lemma"] = lemma # dictionary lemma, not to be confused with lemma (root) annotation per word
    return df_tokens, df_enriched
        
def perform_request(url, data):
    global req_done
    req_done = req_done + 1
    try:
        return requests.get(url, params=data, timeout=REQUEST_TIMEOUT).json()
    except Exception as excp:
        print(f"Request failed with error:\n{excp}.\n\nTry again in {RETRY_INTERVAL} seconds.")
        time.sleep(RETRY_INTERVAL)
        return perform_request(url,data)



def concordances_lemma(lemma, user, key, gdex, results_per_lemma):
    # How to build request? API documentation: https://www.sketchengine.eu/documentation/api-documentation/
    print(" - Issuing query [GDEX " + ("on" if gdex else "off") + ","+ str(results_per_lemma) + " results]...")
    data = {
            'corpname': lang_data["corpus_name"],
            'format': 'json',
            'q': 'q[lemma="%s"]' % (lemma),
            'attrs': 'word,lemma,tag',
            'ctxattrs': 'word,lemma,tag',
            'viewmode': 'kwic', #sen for sentence, or kwic
            'gdex_enabled': "1" if gdex else "0",
            'show_gdex_scores':0,
            'gdexcnt': GDEXCNT,
            'kwicleftctx': '-2:s', # full sentence
            'kwicrightctx': '2:s', # full sentence
            'pagesize': str(results_per_lemma),
            'username': user,
            'api_key': key,
            'structs':'p,g',
            'refs':'=doc.website',
            'iquery': lemma,
            'fromp':1,
            'setattrs':'word,lemma,tag',
            'allpos':'kw',
            'attr_tooltip': 'nott',
            'setstructs':'p',
            'setstructs':'g',
            'setrefs':'=.website',
            'refs_up':0,
            'newctxsize':40,
            'icon_copy':0,
            'multiple_copy':0,
            'use_noflash':0,
            'select_lines':0,
            'line_numbers':0,
            'shorten_refs':1,
            'tbl_template':'none',
            'async': 0
    }
    # If user-made gdexconf supplied, use it
    if "gdexconf" in lang_data:
        gdexconf = lang_data["gdexconf"]
        print("   Using GDEX configuration " + gdexconf)
        data["gdexconf"] = gdexconf
    d = perform_request(BASE_URL + '/view', data=data)
    df_tokens, df_tags = parse_concordances(d, lemma, results_per_lemma)
    
    return df_tokens, df_tags


# Shuffle two lists a and b, which should keep their correspondence
def shuffle(a,b):
    assert len(a) == len(b)
    start_state = random.getstate()
    random.shuffle(a)
    random.setstate(start_state)
    random.shuffle(b)

def main(args):
    global req_done
    req_done = 0

    df = defaultdict(pd.DataFrame)
    
    # retrieve or read data
    if not OFFLINE:
        for lemma in LEMMAS:
            print("Lemma " + lemma)
            tokens_lemma, tags_lemma = concordances_lemma(lemma, args.user, args.key, gdex=True, results_per_lemma=RESULTS_PER_LEMMA_EXTRACTED)
            # TODO: in enriched, immidiatelly eliminate original token and POS-tag, leave only lemma
            # since original tokens are already included in 'tokens' columns
            # then remove triplets code in bad_word_present()
            df["tokens"] = pd.concat([df["tokens"], tokens_lemma], ignore_index=True)
            df["enriched"] = pd.concat([df["enriched"], tags_lemma], ignore_index=True)
            time.sleep(INTER_REQUEST_INTERVAL)
        for output in OUTPUTS:
            df[output].to_csv(os.path.join(BACKUP_DIR, "backup.%s.bkp" % (output)), index=False)


if __name__ =="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', required=True)
    parser.add_argument('--key', required=True)
    args = parser.parse_args()
    main(args)
