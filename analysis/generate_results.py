import pandas as pd
import numpy as np
from datetime import datetime, timedelta

ae_events = pd.read_feather("output/ae_events.feather")
ae_events["max_satisfying_date"] = pd.to_datetime(ae_events["date"]) + timedelta(
    days=14
)


hospital_events = pd.read_feather("output/hospital_events.feather")
hospital_events["min_satisfying_date"] = pd.to_datetime(
    hospital_events["date"]
) - timedelta(days=14)


for i in range(hospital_events.shape[0]):
    row = hospital_events.iloc[i, :]

    if (
        (ae_events["patient_id"] == row["patient_id"])
        & (pd.to_datetime(ae_events["date"]) > row["min_satisfying_date"])
        & (pd.to_datetime(ae_events["date"]) < row["date"])
    ).any():

        hospital_events.loc[i, "ae_attendance_in_range"] = 1

    else:
        hospital_events.loc[i, "ae_attendance_in_range"] = 0

for i in range(ae_events.shape[0]):
    row = ae_events.iloc[i, :]

    if (
        (hospital_events["patient_id"] == row["patient_id"])
        & (pd.to_datetime(hospital_events["date"]) < row["max_satisfying_date"])
        & (pd.to_datetime(hospital_events["date"]) > row["date"])
    ).any():

        ae_events.loc[i, "hospital_attendance_in_range"] = 1

    else:
        ae_events.loc[i, "hospital_attendance_in_range"] = 0


neg = len(hospital_events[hospital_events["ae_attendance_in_range"] == 0])

# all
ae_events["predicted_inclusive"] = 1

ae_events["predicted_resp"] = np.where((ae_events["resp_status"] == 1), 1, 0)

ae_events["predicted_cov"] = np.where((ae_events["covid_status"] == 1), 1, 0)

ae_events["predicted_prim_care_inclusive"] = np.where(
    ((ae_events["cov_prim_care"] == 1) | (ae_events["suspected_cov_prim_care"] == 1)),
    1,
    0,
)

ae_events["predicted_prim_care_probable"] = np.where(
    (ae_events["cov_prim_care"] == 1), 1, 0
)

ae_events["predicted_testing"] = np.where((ae_events["recent_test"] == 1), 1, 0)

for i in [
    "predicted_inclusive",
    "predicted_resp",
    "predicted_cov",
    "predicted_prim_care_inclusive",
    "predicted_prim_care_probable",
    "predicted_testing",
]:

    predicted = list(ae_events[i]) + ([0] * neg)
    actual = list(ae_events["hospital_attendance_in_range"]) + ([1] * neg)

    pd.crosstab(
        pd.Series(actual, name="actual"), pd.Series(predicted, name="predicted")
    ).to_csv(f"output/results_{i}.csv")
