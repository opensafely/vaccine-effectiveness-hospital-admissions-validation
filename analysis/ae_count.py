import pandas as pd
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


df["between_1_2"] = df["ae_attendance_second_date"] - df["ae_attendance_first_date"]
df["between_2_3"] = df["ae_attendance_third_date"] - df["ae_attendance_second_date"]
df["between_3_4"] = df["ae_attendance_fourth_date"] - df["ae_attendance_third_date"]
df["between_4_5"] = df["ae_attendance_fifth_date"] - df["ae_attendance_fourth_date"]
same = len(
    df.loc[
        df["ae_attendance_first_covid_status"]
        == df["ae_attendance_second_covid_status"],
        :,
    ]
)

with open("output/same_count.json", "w") as fp:
    json.dump({"same_count": same}, fp)

plt.hist(df["between_1_2"].astype(str))
plt.savefig("output/hist.jpeg")
