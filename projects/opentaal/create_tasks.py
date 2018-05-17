N_WORDS = 20

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

df["question"] = "Geef een synoniem voor dit woord:"

# Write to file
df.to_csv(args.output_file, index=False)

