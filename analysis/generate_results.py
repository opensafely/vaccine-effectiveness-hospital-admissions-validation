import pandas as pd
import numpy as np
from collections import Counter
import math
import json


df = pd.read_csv('output/input_descriptives.csv')


#emergency hospitalisation

num_patients = len(df['patient_id'].unique())
num_patients_hosp = len(df[df['hospital_admission'].notna()]['patient_id'].unique())
num_patients_hosp_emergency = len(df[df['emergency_hospital_admission'].notna()]['patient_id'].unique())
num_patients_hosp_prim_covid = len(df[df['primary_covid_hospital_admission'].notna()]['patient_id'].unique())
num_patients_hosp_emergency_prim_covid = len(df[df['emergency_primary_covid_hospital_admission'].notna()]['patient_id'].unique())
num_patients_hosp_covid = len(df[df['covid_hospital_admission'].notna()]['patient_id'].unique())
num_patients_hosp_emergency_covid = len(df[df['emergency_covid_hospital_admission'].notna()]['patient_id'].unique())

emergency_hospitalisation_dict = {
    "hospital_admission": num_patients_hosp,
    "emergency_hospital_admission": num_patients_hosp_emergency,
    "admisssion_primary_covid": num_patients_hosp_prim_covid,
    "admission_secondary_covid": num_patients_hosp_covid,
    "emergency_admission_primary_covid": num_patients_hosp_emergency_prim_covid,
    "emergency_admission_secondary_covid": num_patients_hosp_emergency_covid,
}

with open('output/emergency_hospitalisation.json', 'w') as fp:
    json.dump(emergency_hospitalisation_dict, fp)


# a&e attendance in emergency primary covid hospital admissions
num_patients_attended_ae = len(df[(df['emergency_primary_covid_hospital_admission'].notna() & df['ae_attendance_any_discharge']==1)]['patient_id'].unique())
num_patients_attended_ae_with_discharge = len(df[(df['emergency_primary_covid_hospital_admission'].notna() & df['ae_attendance_with_discharge']==1)]['patient_id'].unique())
num_patients_attended_ae_cov = len(df[(df['emergency_primary_covid_hospital_admission'].notna() & df['ae_attendance_covid_status']==1)]['patient_id'].unique())
num_patients_attended_ae_resp = len(df[(df['emergency_primary_covid_hospital_admission'].notna() & df['ae_attendance_respiratory_status']==1)]['patient_id'].unique())
num_patients_attended_ae_cov_pc = len(df[(df['emergency_primary_covid_hospital_admission'].notna() & df['covid_primary_care_before_ae_attendance']==1)]['patient_id'].unique())
num_patients_attended_ae_pos_test = len(df[(df['emergency_primary_covid_hospital_admission'].notna() & df['positive_covid_test_before_ae_attendance']==1)]['patient_id'].unique())
num_patients_attended_ae_pos_test_month = len(df[(df['emergency_primary_covid_hospital_admission'].notna() & df['positive_covid_test_month_before_ae_attendance']==1)]['patient_id'].unique())

ae_dict = {
    "attended_ae": num_patients_attended_ae,
    "attended_ae_with_discharge": num_patients_attended_ae_with_discharge,
    "attended_ae_cov": num_patients_attended_ae_cov,
    "attended_ae_resp": num_patients_attended_ae_resp,
    "attended_ae_cov_pc": num_patients_attended_ae_cov_pc,
    "attended_ae_pos_test": num_patients_attended_ae_pos_test,
    "attended_ae_pos_test_month": num_patients_attended_ae_pos_test_month,
}

with open('output/ae.json', 'w') as fp:
    json.dump(ae_dict, fp)

# discharge destination in those with primary cov in emergency hosp admissions (who went to ae)

prim_cov_ae_discharge = df[(df['emergency_primary_covid_hospital_admission'].notna() & df['ae_attendance_any_discharge']==1)]['discharge_destination']
missing = prim_cov_ae_discharge.isna().sum()
destination_dict = Counter(prim_cov_ae_discharge[prim_cov_ae_discharge.notnull()])
destination_dict['missing'] = missing

discharge_dict = {1066341000000100:"Ambulatory Emergency Care", 19712007: "Patient Transfer", 183919006: "Other", 1066361000000104: "High dependency unit", 305398007: "Mortuary", 1066381000000108: "Other", 1066331000000109: "Emergency department short stay ward", 306705005: "Other", 306706006:"Ward", 306689006: "Home", 306694006: "Nursing Home", 306691003: "Residential Home", 1066351000000102: "Other", 1066401000000108: "Other", 1066371000000106: "Coronary Care Unit", 50861005: "Other", 1066391000000105: "ICU", "missing": "missing"}
percent_dict = {}
data = []
total = 0

other_count=0
drop_keys=[]
#Drop dictionary pairs if value <10
for key, value in destination_dict.items():
    if value <10:
        other_count +=value
        drop_keys.append(key)
        
for key in drop_keys:
    del destination_dict[key]
    
destination_dict["Other"] = other_count

for key, value in destination_dict.items():
    total+=value

for key, value in destination_dict.items():
    if key=="Other":
        pass
    else:
        percent = (value/total) * 100
        row = [discharge_dict[key], value, percent]
        data.append(row)

discharge_destination_df = pd.DataFrame(data, columns=["Discharge Destination", "Number", "%"])
discharge_destination_df.to_csv('output/discharge_destination.csv')



#models
df = pd.read_csv('output/input.csv')

positive_covid_patients_sus = df[df['emergency_primary_covid_hospital_admission'].notna()]
negative_covid_patients_sus = df[~df['emergency_primary_covid_hospital_admission'].notna()]

# model_a

positive_covid_patients_a = df[(df['ae_attendance_any_discharge']==1) & ((df['ae_attendance_covid_status']==1) | (df['positive_covid_test_before_ae_attendance'] ==1) | (df['covid_primary_care_before_ae_attendance'] ==1))]
negative_covid_patients_a = df[(df['ae_attendance_any_discharge']==0) | ((df['ae_attendance_any_discharge']==1) & ((df['ae_attendance_covid_status']==0) & (df['positive_covid_test_before_ae_attendance'] ==0) & (df['covid_primary_care_before_ae_attendance'] ==0)))]


sus_patients_positive = set(list(positive_covid_patients_sus['patient_id']))
model_a_patients_positive = set(list(positive_covid_patients_a['patient_id']))

sus_patients_negative = set(list(negative_covid_patients_sus['patient_id']))
model_a_patients_negative = set(list(negative_covid_patients_a['patient_id']))


sus_pos_ecds_pos = len(list(set(sus_patients_positive) & set(model_a_patients_positive)))
sus_pos_ecds_neg = len(list(set(sus_patients_positive) & set(model_a_patients_negative)))
sus_neg_ecds_pos = len(list(set(sus_patients_negative) & set(model_a_patients_positive)))
sus_neg_ecds_neg = len(list(set(sus_patients_negative) & set(model_a_patients_negative)))

sensitivity_a = (sus_pos_ecds_pos/(sus_pos_ecds_pos + sus_pos_ecds_neg))*100
specificity_a = (sus_neg_ecds_neg/(sus_neg_ecds_pos + sus_neg_ecds_neg))*100
PPV_a = (sus_pos_ecds_pos/(sus_pos_ecds_pos + sus_neg_ecds_pos))*100
NPV_a = (sus_neg_ecds_neg/(sus_neg_ecds_neg + sus_pos_ecds_neg))*100
MCC_a = ((sus_pos_ecds_pos * sus_neg_ecds_neg)-(sus_neg_ecds_pos * sus_pos_ecds_neg))/math.sqrt((sus_pos_ecds_pos + sus_neg_ecds_pos)*(sus_pos_ecds_neg+sus_neg_ecds_neg)*(sus_pos_ecds_pos + sus_pos_ecds_neg)*(sus_neg_ecds_pos+sus_neg_ecds_neg))
output = pd.DataFrame([[sus_pos_ecds_pos, sus_neg_ecds_pos, (sus_pos_ecds_pos + sus_neg_ecds_pos)], [sus_pos_ecds_neg, sus_neg_ecds_neg, (sus_pos_ecds_neg + sus_neg_ecds_neg)], [(sus_pos_ecds_pos+sus_pos_ecds_neg), (sus_neg_ecds_pos+sus_neg_ecds_neg), (sus_pos_ecds_pos + sus_pos_ecds_neg + sus_neg_ecds_pos + sus_neg_ecds_neg)]], columns=["SUS-positive", "SUS-negative", "Total"], index=["ECDS-positive", "ECDS-negative", "Total"])
output.to_csv('output/model_a.csv')

# model_b

positive_covid_patients_b = df[(df['ae_attendance_hosp_discharge']==1) & ((df['ae_attendance_covid_status']==1) | (df['positive_covid_test_before_ae_attendance'] ==1) | (df['covid_primary_care_before_ae_attendance'] ==1))]
negative_covid_patients_b = df[df['ae_attendance_hosp_discharge']==0 | ((df['ae_attendance_hosp_discharge']==1) & ((df['ae_attendance_covid_status']==0) & (df['positive_covid_test_before_ae_attendance'] ==0) & (df['covid_primary_care_before_ae_attendance'] ==0)))]


model_b_patients_positive = set(list(positive_covid_patients_b['patient_id']))
model_b_patients_negative = set(list(negative_covid_patients_b['patient_id']))


sus_pos_ecds_pos = len(list(set(sus_patients_positive) & set(model_b_patients_positive)))
sus_pos_ecds_neg = len(list(set(sus_patients_positive) & set(model_b_patients_negative)))
sus_neg_ecds_pos = len(list(set(sus_patients_negative) & set(model_b_patients_positive)))
sus_neg_ecds_neg = len(list(set(sus_patients_negative) & set(model_b_patients_negative)))

sensitivity_b = (sus_pos_ecds_pos/(sus_pos_ecds_pos + sus_pos_ecds_neg))*100
specificity_b = (sus_neg_ecds_neg/(sus_neg_ecds_pos + sus_neg_ecds_neg))*100
PPV_b = (sus_pos_ecds_pos/(sus_pos_ecds_pos + sus_neg_ecds_pos))*100
NPV_b = (sus_neg_ecds_neg/(sus_neg_ecds_neg + sus_pos_ecds_neg))*100
MCC_b = ((sus_pos_ecds_pos * sus_neg_ecds_neg)-(sus_neg_ecds_pos * sus_pos_ecds_neg))/math.sqrt((sus_pos_ecds_pos + sus_neg_ecds_pos)*(sus_pos_ecds_neg+sus_neg_ecds_neg)*(sus_pos_ecds_pos + sus_pos_ecds_neg)*(sus_neg_ecds_pos+sus_neg_ecds_neg))
output = pd.DataFrame([[sus_pos_ecds_pos, sus_neg_ecds_pos, (sus_pos_ecds_pos + sus_neg_ecds_pos)], [sus_pos_ecds_neg, sus_neg_ecds_neg, (sus_pos_ecds_neg + sus_neg_ecds_neg)], [(sus_pos_ecds_pos+sus_pos_ecds_neg), (sus_neg_ecds_pos+sus_neg_ecds_neg), (sus_pos_ecds_pos + sus_pos_ecds_neg + sus_neg_ecds_pos + sus_neg_ecds_neg)]], columns=["SUS-positive", "SUS-negative", "Total"], index=["ECDS-positive", "ECDS-negative", "Total"])
output.to_csv('output/model_b.csv')

#model_c

positive_covid_patients_c = df[(df['ae_attendance_hosp_discharge']==1) & ((df['ae_attendance_covid_status']==1) | (df['ae_attendance_respiratory_status']==1) | (df['positive_covid_test_before_ae_attendance'] ==1) | (df['covid_primary_care_before_ae_attendance'] ==1))]
negative_covid_patients_c = df[df['ae_attendance_hosp_discharge']==0 | ((df['ae_attendance_hosp_discharge']==1) & ((df['ae_attendance_covid_status']==0) & (df['ae_attendance_respiratory_status']==1) & (df['positive_covid_test_before_ae_attendance'] ==0) & (df['covid_primary_care_before_ae_attendance'] ==0)))]


model_c_patients_positive = set(list(positive_covid_patients_c['patient_id']))
model_c_patients_negative = set(list(negative_covid_patients_c['patient_id']))


sus_pos_ecds_pos = len(list(set(sus_patients_positive) & set(model_c_patients_positive)))
sus_pos_ecds_neg = len(list(set(sus_patients_positive) & set(model_c_patients_negative)))
sus_neg_ecds_pos = len(list(set(sus_patients_negative) & set(model_c_patients_positive)))
sus_neg_ecds_neg = len(list(set(sus_patients_negative) & set(model_c_patients_negative)))

sensitivity_c = (sus_pos_ecds_pos/(sus_pos_ecds_pos + sus_pos_ecds_neg))*100
specificity_c = (sus_neg_ecds_neg/(sus_neg_ecds_pos + sus_neg_ecds_neg))*100
PPV_c = (sus_pos_ecds_pos/(sus_pos_ecds_pos + sus_neg_ecds_pos))*100
NPV_c = (sus_neg_ecds_neg/(sus_neg_ecds_neg + sus_pos_ecds_neg))*100
MCC_c = ((sus_pos_ecds_pos * sus_neg_ecds_neg)-(sus_neg_ecds_pos * sus_pos_ecds_neg))/math.sqrt((sus_pos_ecds_pos + sus_neg_ecds_pos)*(sus_pos_ecds_neg+sus_neg_ecds_neg)*(sus_pos_ecds_pos + sus_pos_ecds_neg)*(sus_neg_ecds_pos+sus_neg_ecds_neg))

output = pd.DataFrame([[sus_pos_ecds_pos, sus_neg_ecds_pos, (sus_pos_ecds_pos + sus_neg_ecds_pos)], [sus_pos_ecds_neg, sus_neg_ecds_neg, (sus_pos_ecds_neg + sus_neg_ecds_neg)], [(sus_pos_ecds_pos+sus_pos_ecds_neg), (sus_neg_ecds_pos+sus_neg_ecds_neg), (sus_pos_ecds_pos + sus_pos_ecds_neg + sus_neg_ecds_pos + sus_neg_ecds_neg)]], columns=["SUS-positive", "SUS-negative", "Total"], index=["ECDS-positive", "ECDS-negative", "Total"])
output.to_csv('output/model_c.csv')
# dictionary of model results

performance_dict = {
    "A": {
        "sensitivity": sensitivity_a,
        "specificity": specificity_a,
        "ppv": PPV_a,
        "npv": NPV_a,
        "mcc": MCC_a
    },
    "B": {
        "sensitivity": sensitivity_b,
        "specificity": specificity_b,
        "ppv": PPV_b,
        "npv": NPV_b,
        "mcc": MCC_b
    },
    "C": {
        "sensitivity": sensitivity_c,
        "specificity": specificity_c,
        "ppv": PPV_c,
        "npv": NPV_c,
        "mcc": MCC_c
    }
}

with open('output/model_performance.json', 'w') as fp:
    json.dump(performance_dict, fp)

#sensitivity
sensitivity_dict = {}

# drop cov ae
positive_covid_patients = df[(df['ae_attendance_hosp_discharge']==1) & ((df['positive_covid_test_before_ae_attendance'] ==1) | (df['covid_primary_care_before_ae_attendance'] ==1))]
negative_covid_patients = df[(df['ae_attendance_hosp_discharge']==0) | ((df['ae_attendance_hosp_discharge']==1) &  (df['positive_covid_test_before_ae_attendance'] ==0) & (df['covid_primary_care_before_ae_attendance'] ==0))]
model_patients_positive = set(list(positive_covid_patients['patient_id']))
model_patients_negative = set(list(negative_covid_patients['patient_id']))
sus_pos_ecds_pos = len(list(set(sus_patients_positive) & set(model_patients_positive)))
sus_pos_ecds_neg = len(list(set(sus_patients_positive) & set(model_patients_negative)))
sus_neg_ecds_pos = len(list(set(sus_patients_negative) & set(model_patients_positive)))
sus_neg_ecds_neg = len(list(set(sus_patients_negative) & set(model_patients_negative)))
MCC = ((sus_pos_ecds_pos * sus_neg_ecds_neg)-(sus_neg_ecds_pos * sus_pos_ecds_neg))/math.sqrt((sus_pos_ecds_pos + sus_neg_ecds_pos)*(sus_pos_ecds_neg+sus_neg_ecds_neg)*(sus_pos_ecds_pos + sus_pos_ecds_neg)*(sus_neg_ecds_pos+sus_neg_ecds_neg))
sensitivity_dict['cov_ae'] = MCC

#drop recent pos test
positive_covid_patients = df[(df['ae_attendance_hosp_discharge']==1) & ((df['ae_attendance_covid_status']==1)  | (df['covid_primary_care_before_ae_attendance'] ==1))]
negative_covid_patients = df[(df['ae_attendance_hosp_discharge']==0) | ((df['ae_attendance_hosp_discharge']==1) & (df['ae_attendance_covid_status']==0)  & (df['covid_primary_care_before_ae_attendance'] ==0))]
model_patients_positive = set(list(positive_covid_patients['patient_id']))
model_patients_negative = set(list(negative_covid_patients['patient_id']))
sus_pos_ecds_pos = len(list(set(sus_patients_positive) & set(model_patients_positive)))
sus_pos_ecds_neg = len(list(set(sus_patients_positive) & set(model_patients_negative)))
sus_neg_ecds_pos = len(list(set(sus_patients_negative) & set(model_patients_positive)))
sus_neg_ecds_neg = len(list(set(sus_patients_negative) & set(model_patients_negative)))
MCC = ((sus_pos_ecds_pos * sus_neg_ecds_neg)-(sus_neg_ecds_pos * sus_pos_ecds_neg))/math.sqrt((sus_pos_ecds_pos + sus_neg_ecds_pos)*(sus_pos_ecds_neg+sus_neg_ecds_neg)*(sus_pos_ecds_pos + sus_pos_ecds_neg)*(sus_neg_ecds_pos+sus_neg_ecds_neg))
sensitivity_dict['pos_test'] = MCC

#drop cov pc
positive_covid_patients = df[((df['ae_attendance_hosp_discharge']==1) & ((df['ae_attendance_covid_status']==1) | (df['positive_covid_test_before_ae_attendance'] ==1) ))]
negative_covid_patients = df[(df['ae_attendance_hosp_discharge']==0) | ((df['ae_attendance_hosp_discharge']==1) & (df['ae_attendance_covid_status']==0) & (df['positive_covid_test_before_ae_attendance'] ==0))]
model_patients_positive = set(list(positive_covid_patients['patient_id']))
model_patients_negative = set(list(negative_covid_patients['patient_id']))
sus_pos_ecds_pos = len(list(set(sus_patients_positive) & set(model_patients_positive)))
sus_pos_ecds_neg = len(list(set(sus_patients_positive) & set(model_patients_negative)))
sus_neg_ecds_pos = len(list(set(sus_patients_negative) & set(model_patients_positive)))
sus_neg_ecds_neg = len(list(set(sus_patients_negative) & set(model_patients_negative)))
MCC = ((sus_pos_ecds_pos * sus_neg_ecds_neg)-(sus_neg_ecds_pos * sus_pos_ecds_neg))/math.sqrt((sus_pos_ecds_pos + sus_neg_ecds_pos)*(sus_pos_ecds_neg+sus_neg_ecds_neg)*(sus_pos_ecds_pos + sus_pos_ecds_neg)*(sus_neg_ecds_pos+sus_neg_ecds_neg))
sensitivity_dict['cov_pc'] = MCC


with open('output/sensitivity.json', 'w') as fp:
    json.dump(sensitivity_dict, fp)