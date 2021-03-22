from cohortextractor import StudyDefinition, patients, codelist, codelist_from_csv

# Import Codelists
from codelists import *

start_date="2020-09-01"
end_date="2021-01-01"

ae_discharge_dict = {1066341000000100:"Ambulatory Emergency Care", 19712007: "Patient Transfer", 183919006: "Other", 1066361000000104: "High dependency unit", 305398007: "Mortuary", 1066381000000108: "Other", 1066331000000109: "Emergency department short stay ward", 306705005: "Other", 306706006:"Ward", 306689006: "Home", 306694006: "Residential or Nursing Home", 306691003: "Residential or Nursing Home", 1066351000000102: "Other", 1066401000000108: "Other", 1066371000000106: "Coronary Care Unit", 50861005: "Other", 1066391000000105: "ICU", "missing": "missing"}

# ae_discharge_dict = {"discharged_to_ward": str(306706006), "discharged_to_emergency_short_stay": str(1066331000000109), "discharge_to_ambulatory": str(1066341000000100), "discharged_to_icu": str(1066391000000105)}

# ae_discharge_dict = {"discharged_to_ward": str(306706006), "discharged_to_emergency_short_stay": str(1066331000000109), "discharged_to_high_dependency": str(1066361000000104), "discharged_to_icu": str(1066391000000105), "discharged_to_hospice": str(183919006), "patient_transfer": str(19712007), "discharge_to_ambulatory": str(1066341000000100)}

ae_discharge_list = [value for (key, value) in ae_discharge_dict.items()]

diagnosis_codes = {"uppper_resp_infection": str(54150009), "lower_resp_infection": str(50417007), "pneumonia": str(233604007), "sars": str(398447004), "resp_failure": str(409622000)}

respiratory_codes = [value for (key, value) in diagnosis_codes.items()]


study = StudyDefinition(
    index_date=start_date,
    default_expectations={
        "date": {"earliest": start_date, "latest": end_date},
        "rate": "uniform",
        "incidence": 0.5,
    },
   
    population=patients.satisfying(
        """
        registered
        AND
        (age >= 18 AND age < 110)
        AND
        (sex = "M" OR sex = "F")
        AND
        (NOT has_died)
        AND
        (hospital_admission OR ae_attendance_any)
        """,
        registered=patients.registered_as_of(
            "index_date",
        ),
        has_died=patients.died_from_any_cause(
            on_or_before="index_date",
            returning="binary_flag",
        ),

        # https://github.com/opensafely/risk-factors-research/issues/49
        age=patients.age_as_of(
            "index_date",
            return_expectations={
                "rate": "universal",
                "int": {"distribution": "population_ages"}
            },
        ),

        sex=patients.sex(
            return_expectations={
                "rate": "universal",
                "category": {"ratios": {"M": 0.49, "F": 0.51}},
            }
        ),
       
    ),

    primary_covid_hospital_admission=patients.admitted_to_hospital(
        returning="date_admitted",
        with_these_primary_diagnoses=covid_codes,
        with_admission_method="21",
        on_or_after="index_date + 7 days",
        date_format="YYYY-MM-DD",
        find_last_match_in_period=True,
        return_expectations={
            "incidence": 0.3,
        },
    ),


    covid_hospital_admission=patients.admitted_to_hospital(
        returning="date_admitted",
        with_these_diagnoses=covid_codes,
        with_admission_method="21",
        on_or_after="index_date + 7 days",
        date_format="YYYY-MM-DD",
        find_last_match_in_period=True,
        return_expectations={
            "incidence": 0.3,
        },
    ),

    hospital_admission=patients.admitted_to_hospital(
        returning="date_admitted",
        on_or_after="index_date + 7 days",
        with_admission_method="21",
        date_format="YYYY-MM-DD",
        find_last_match_in_period=True,
        return_expectations={
            "incidence": 0.3,
        },
    ),

    ae_attendance_any = patients.attended_emergency_care(
        between=["index_date", end_date],
        returning="binary_flag",
        find_last_match_in_period=True,
        return_expectations={
            "incidence": 0.4
        }
        
    ),

   



    #did they attend ae ever and discharged to hosp or icu
    ae_attendance = patients.attended_emergency_care(
        between=["primary_covid_hospital_admission - 7 days", "primary_covid_hospital_admission"],
        returning="binary_flag",
        find_last_match_in_period=True,
        discharged_to=ae_discharge_list,
        return_expectations={
            "incidence": 0.4
        }
        
    ),

    ae_attendance_no_discharge = patients.attended_emergency_care(
        between=["primary_covid_hospital_admission - 7 days", "primary_covid_hospital_admission"],
        returning="binary_flag",
        find_last_match_in_period=True,
        return_expectations={
            "incidence": 0.4
        }
        
    ),

    discharge_destination = patients.attended_emergency_care(
        between=["primary_covid_hospital_admission - 7 days", "primary_covid_hospital_admission"],
        returning="discharge_destination",
        find_last_match_in_period=True,
        return_expectations={
            "incidence": 0.4,
            "category": {"ratios": {306706006: 0.5, 1066391000000105: 0.5}},
        }
        
    ),

    # want people who attended ae then go on to be admitted to hosp
    ae_attendance_date = patients.attended_emergency_care(
        between=["primary_covid_hospital_admission - 7 days", "primary_covid_hospital_admission"],
        returning="date_arrived",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        discharged_to=ae_discharge_list,
        return_expectations = {
            "incidence": 0.5,
            "category": {"ratios": {306706006: 0.5, 1066391000000105: 0.5}},}
    ),

    # want people who attended ae then go on to be admitted to hosp
    ae_attendance_no_discharge_date = patients.attended_emergency_care(
        between=["primary_covid_hospital_admission - 7 days", "primary_covid_hospital_admission"],
        returning="date_arrived",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        return_expectations = {
            "incidence": 0.5,
            "category": {"ratios": {306706006: 0.5, 1066391000000105: 0.5}},}
    ),

    # covid status of those attendance to ae
    ae_attendance_covid_status = patients.attended_emergency_care(
        between=["primary_covid_hospital_admission - 7 days", "primary_covid_hospital_admission"],
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_diagnoses=covid_codes_ae,
        return_expectations= {
            "incidence": 0.9
        }
    ),

    

    # date of ae attendance due to covid
    ae_attendance_covid_status_date = patients.attended_emergency_care(
        between=["primary_covid_hospital_admission - 7 days", "primary_covid_hospital_admission"],
        returning="date_arrived",
        date_format="YYYY-MM-DD",
        find_last_match_in_period=True,
        with_these_diagnoses=covid_codes_ae,
        return_expectations= {
            "incidence": 0.9
        }
    ),

    # date of ae attendance due to respiratory
    ae_attendance_respiratory_status = patients.attended_emergency_care(
        between=["primary_covid_hospital_admission - 7 days", "primary_covid_hospital_admission"],
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        find_last_match_in_period=True,
        with_these_diagnoses=respiratory_codes,
        return_expectations= {
            "incidence": 0.9
        }
    ),

    # in those attending ae had they had recent positiv cov test
    positive_covid_test_before_ae_attendance = patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=["ae_attendance_no_discharge_date - 14 days", "ae_attendance_no_discharge_date + 7 days"],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01",  "latest" : "2021-02-01"},
            "rate": "exponential_increase",
            
        },
    ),

    # looks at more historical positive cov test
    positive_covid_test_month_before_ae_attendance = patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=["ae_attendance_no_discharge_date - 28 days", "ae_attendance_no_discharge_date +7 days"],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01",  "latest" : "2021-02-01"},
            "rate": "exponential_increase",
            
        },
    ),

    # in those attending ae had they had positive cov in pc
    covid_primary_care_before_ae_attendance = patients.with_these_clinical_events(
        codelist=covid_primary_care_codes,
        between=["ae_attendance_no_discharge_date - 14 days", "ae_attendance_no_discharge_date"],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01",  "latest" : "2021-02-01"},
            "rate": "exponential_increase",
       
        },
    ),
    
    

    # looks at more historical positive cov test
    positive_covid_test_before_hospital_admission = patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=["hospital_admission - 14 days", "hospital_admission + 7 days"],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01",  "latest" : "2021-02-01"},
            "rate": "exponential_increase",
            
        },
    ),

    positive_covid_test_month_before_hospital_admission = patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=["hospital_admission - 28 days", "hospital_admission + 7 days"],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01",  "latest" : "2021-02-01"},
            "rate": "exponential_increase",
            
        },
    ),


    # in those attending ae had they had positive cov in pc
    covid_primary_care_before_hospital_admission = patients.with_these_clinical_events(
        codelist=covid_primary_care_codes,
        between=["hospital_admission - 14 days", "hospital_admission"],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01",  "latest" : "2021-02-01"},
            "rate": "exponential_increase",
       
        },
    ),



)
