from cohortextractor import StudyDefinition, patients, codelist, codelist_from_csv

# Import Codelists
from codelists import *

start_date="2020-09-01"
end_date="2021-01-01"

ae_discharge_dict = {"discharged_to_ward": str(306706006), "discharged_to_icu": str(1066391000000105)}
ae_discharge_list = [value for (key, value) in ae_discharge_dict.items()]






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
        NOT has_died
        AND
        (covid_hospital_admission OR ae_attendance)
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
        
        # https://github.com/opensafely/risk-factors-research/issues/46
        sex=patients.sex(
            return_expectations={
                "rate": "universal",
                "category": {"ratios": {"M": 0.49, "F": 0.51}},
            }
        ),

    ),



    #did they attend ae ever and discharged to hosp or icu
    ae_attendance = patients.attended_emergency_care(
        between=["index_date", end_date],
        returning="binary_flag",
        find_last_match_in_period=True,
        discharged_to=ae_discharge_list,
        return_expectations={
            "incidence": 0.4
        }
        
    ),

    # want people who attended ae then go on to be admitted to hosp
    ae_attendance_date = patients.attended_emergency_care(
        returning="date_arrived",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
        discharged_to=ae_discharge_list,
        return_expectations = {
            "incidence": 0.5,
            "category": {"ratios": {306706006: 0.5, 1066391000000105: 0.5}},}
    ),

    # covid status of those attendance to ae
    ae_attendance_covid_status = patients.attended_emergency_care(
        between=["index_date", end_date],
        returning="binary_flag",
        find_last_match_in_period=True,
        with_these_diagnoses=covid_codes_ae,
        return_expectations= {
            "incidence": 0.9
        }
    ),

    

    # date of ae attendance due to covid
    ae_attendance_covid_status_date = patients.attended_emergency_care(
        between=["index_date", end_date],
        returning="date_arrived",
        find_last_match_in_period=True,
        with_these_diagnoses=covid_codes_ae,
        return_expectations= {
            "incidence": 0.9
        }
    ),

    # in those attending ae had they had recent positiv cov test
    positive_covid_test_before_ae_attendance = patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=["ae_attendance_date - 14 days", "ae_attendance_date + 7 days"],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01",  "latest" : "2021-02-01"},
            "rate": "exponential_increase",
            
        },
    ),

    # looks at more historical positive cov test
    positive_covid_test_before_ae_attendance_month = patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=["ae_attendance_date - 28 days", "ae_attendance_date -14 days"],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01",  "latest" : "2021-02-01"},
            "rate": "exponential_increase",
            
        },
    ),

    # in those attending ae had they had positive cov in pc
    covid_primary_care_before_ae_attendance = patients.with_these_clinical_events(
        codelist=covid_primary_care_codes,
        between=["ae_attendance_date - 14 days", "ae_attendance_date"],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01",  "latest" : "2021-02-01"},
            "rate": "exponential_increase",
       
        },
    ),
    


    primary_covid_hospital_admission=patients.admitted_to_hospital(
        returning="date_admitted",
        with_these_primary_diagnoses=covid_codes,
        on_or_after="index_date",
        date_format="YYYY-MM-DD",
        find_first_match_in_period=True,
        return_expectations={
            "incidence": 0.3,
        },
    ),

    covid_hospital_admission=patients.admitted_to_hospital(
        returning="date_admitted",
        with_these_diagnoses=covid_codes,
        on_or_after="index_date",
        date_format="YYYY-MM-DD",
        find_first_match_in_period=True,
        return_expectations={
            "incidence": 0.3,
        },
    ),



)
