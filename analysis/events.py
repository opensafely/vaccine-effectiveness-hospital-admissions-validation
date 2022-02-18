import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

ae_attendance_vars = ["ae_attendance_first_date", "ae_attendance_second_date", "ae_attendance_third_date", "ae_attendance_fourth_date", "ae_attendance_fifth_date"]
emergency_covid_hospitalisation_vars = ["emergency_covid_hospital_admission_first_date", "emergency_covid_hospital_admission_second_date", "emergency_covid_hospital_admission_third_date", "emergency_covid_hospital_admission_fourth_date", "emergency_covid_hospital_admission_fifth_date"]
emergency_primary_covid_hospitalisation_vars = ["emergency_primary_covid_hospital_admission_first_date", "emergency_primary_covid_hospital_admission_second_date", "emergency_primary_covid_hospital_admission_third_date", "emergency_primary_covid_hospital_admission_fourth_date", "emergency_primary_covid_hospital_admission_fifth_date"]

df = pd.read_csv('output/input.csv')
df['ae_attendance_dates']= df.loc[:, ae_attendance_vars].values.tolist()
df['emergency_covid_hospital_dates'] = df.loc[:, emergency_covid_hospitalisation_vars].values.tolist()
df['emergency_primary_covid_hospital_dates'] = df.loc[:, emergency_primary_covid_hospitalisation_vars].values.tolist()

convert_dict = {
    0: "first",
    1: "second",
    2: "third",
    3: "fourth",
    4: "fifth"
}



ae_event_data = []
hosp_event_data = []

def get_event(row, ae_or_hosp):
    
    if ae_or_hosp == "ae":
        dates = row["ae_attendance_dates"]
    
        for i, date in enumerate(dates):
            if pd.notnull(date):

                patient_id= row["patient_id"]
                covid_status = row[f"ae_attendance_{convert_dict[i]}_covid_status"]
                resp_status = row[f"ae_attendance_{convert_dict[i]}_respiratory_status"]
                covid_prim_care = row[f"ae_attendance_{convert_dict[i]}_covid_primary_care_status"]
                suspected_covid_prim_care = row[f"ae_attendance_{convert_dict[i]}_suspected_covid_primary_care_status"]
                recent_test = row[f"positive_covid_test_before_ae_attendance_{convert_dict[i]}"]

                new_row = {"patient_id": patient_id, "date": date,"covid_status": covid_status, "resp_status": resp_status,"cov_prim_care": covid_prim_care, "suspected_cov_prim_care": suspected_covid_prim_care,"recent_test": recent_test}

                ae_event_data.append(new_row)
        
    elif ae_or_hosp == "hosp":
        dates = row["emergency_covid_hospital_dates"]
    
        for i, date in enumerate(dates):
            if pd.notnull(date):

                patient_id= row["patient_id"]

                new_row = {"patient_id": patient_id, "date": date}

                hosp_event_data.append(new_row)
    else:
        pass
    
    
df.apply(lambda row: get_event(row, "ae"), axis=1)
df.apply(lambda row: get_event(row, "hosp"), axis=1)

ae_events = pd.DataFrame(ae_event_data)
hospital_events = pd.DataFrame(hosp_event_data)

ae_events.to_feather("output/ae_events.feather")
hospital_events.to_feather("output/hospital_events.feather")