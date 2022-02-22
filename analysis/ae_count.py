import pandas as pd
import numpy as np
import json
from collections import Counter
import matplotlib.pyplot as plt

df = pd.read_csv(
    "output/input_ae.csv",
    parse_dates=[
        "ae_attendance_first_date",
        "ae_attendance_second_date",
        "ae_attendance_third_date",
        "ae_attendance_fourth_date",
        "ae_attendance_fifth_date",
    ],
)
ae_count = Counter(df["ae_attendance_count"])
ae_count_stripped = {"5+": 0}
for key, value in ae_count.items():
    if int(key) < 5:
        ae_count_stripped[key] = value

    else:
        ae_count_stripped["5+"] += value

with open("output/ae_count.json", "w") as fp:
    json.dump(ae_count_stripped, fp)

hospital_count = Counter(df["hospital_admission_count"])
hospital_count_stripped = {"5+": 0}
for key, value in hospital_count.items():
    if int(key) < 5:
        hospital_count_stripped[key] = value

    else:
        hospital_count_stripped["5+"] += value

with open("output/hospital_admission_count.json", "w") as fp:
    json.dump(hospital_count_stripped, fp)

emergency_hospital_count = Counter(df["emergency_primary_hospital_admission_count"])
emergency_hospital_count_stripped = {"5+": 0}
for key, value in emergency_hospital_count.items():
    if int(key) < 5:
        emergency_hospital_count_stripped[key] = value

    else:
        emergency_hospital_count_stripped["5+"] += value

with open("output/emergency_hospital_admission_count.json", "w") as fp:
    json.dump(emergency_hospital_count_stripped, fp)
