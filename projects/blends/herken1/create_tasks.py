N_WORDS = 10

import argparse
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--input_file", default="OpenTaal-210G-basis-gekeurd.txt")
parser.add_argument("--output_file", default="opentaal_tasks.csv")
args = parser.parse_args()

# Read file
df = pd.read_csv(args.input_file, index_col=None,header=None)
df.columns = ["word"]

# Sample n rows
df = df.sample(n=N_WORDS)

df["question"] = "Geef een synoniem voor het volgende woord:"
df["type"] = "task"

details_row = pd.DataFrame([{"type":"userdetails"}])
df = pd.concat([details_row,df], ignore_index=True)

# Write to file
df.to_csv(args.output_file, index=False)

