import pandas as pd
import json
from collections import Counter

df = pd.read_csv("output/input_ae.csv")
ae_count = Counter(df["ae_attendance_count"])

with open("output/ae_count.json", "w") as fp:
    json.dump(ae_count, fp)

hospital_count = Counter(df["hospital_admission_count"])

with open("output/hospital_admission_count.json", "w") as fp:
    json.dump(hospital_count, fp)
