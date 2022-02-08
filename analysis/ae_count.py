import pandas as pd
import json
from collections import Counter

df = pd.read_csv("output/input_ae.csv")
count = Counter(df["ae_attendance_count"])

with open("output/ae_count.json", "w") as fp:
    json.dump(count, fp)
