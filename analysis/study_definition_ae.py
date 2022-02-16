from cohortextractor import StudyDefinition, patients, codelist, codelist_from_csv

# Import Codelists
from codelists import *

start_date = "2021-06-01"
end_date = "2021-10-01"

ae_discharge_dict = {
    1066341000000100: "Ambulatory Emergency Care",
    19712007: "Patient Transfer",
    183919006: "Hospice",
    1066361000000104: "High dependency unit",
    305398007: "Mortuary",
    1066381000000108: "Special baby care unit",
    1066331000000109: "Emergency department short stay ward",
    306705005: "Police custody",
    306706006: "Ward",
    306689006: "Home",
    306694006: "Nursing Home",
    306691003: "Residential Home",
    1066351000000102: "Hospital at home",
    1066401000000108: "Neonatal ICU",
    1066371000000106: "Coronary Care Unit",
    50861005: "Legal Custody",
    1066391000000105: "ICU",
    "missing": "missing",
}


ae_discharge_list = [str(key) for (key, value) in ae_discharge_dict.items()]

hosp_discharge_list = [str(306706006), str(1066331000000109), str(1066391000000105)]

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
                "int": {"distribution": "population_ages"},
            },
        ),
        sex=patients.sex(
            return_expectations={
                "rate": "universal",
                "category": {"ratios": {"M": 0.49, "F": 0.51}},
            }
        ),
    ),
    hospital_admission=patients.admitted_to_hospital(
        returning="binary_flag",
        between=["index_date + 1 day", end_date],
        date_format="YYYY-MM-DD",
        find_last_match_in_period=True,
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ae_attendance_any=patients.attended_emergency_care(
        between=["index_date", end_date],
        returning="binary_flag",
        find_last_match_in_period=True,
        return_expectations={"incidence": 0.4},
    ),
    ae_attendance_count=patients.attended_emergency_care(
        between=["index_date", end_date],
        returning="number_of_matches_in_period",
        discharged_to=hosp_discharge_list,
        return_expectations={"int": {"distribution": "normal", "mean": 2, "stddev": 1}},
    ),
    hospital_admission_count=patients.admitted_to_hospital(
        returning="number_of_matches_in_period",
        between=["index_date + 1 day", end_date],
        return_expectations={"int": {"distribution": "normal", "mean": 2, "stddev": 1}},
    ),
    emergency_hospital_admission_count = patients.admitted_to_hospital(
        returning="number_of_matches_in_period",
        between=["index_date + 1 day", end_date],
        with_admission_method=[
            "21",
            "22",
            "23",
            "24",
            "25",
            "2A",
            "2B",
            "2C",
            "2D",
            "28",
        ],
        with_patient_classification=["1"],
        return_expectations={"int": {"distribution": "normal", "mean": 2, "stddev": 1}},
    ),

    ae_attendance_first_date=patients.attended_emergency_care(
        between=["index_date", end_date],
        returning="date_arrived",
        date_format="YYYY-MM-DD",
        find_first_match_in_period=True,
        discharged_to=hosp_discharge_list,
        return_expectations={
            "date": {"earliest": "2021-01-01", "latest": "2021-02-01"},
            "rate": "exponential_increase",
        },
    ),
    ae_attendance_first_covid_status=patients.attended_emergency_care(
        between=[
            "ae_attendance_first_date",
            "ae_attendance_first_date",
        ],
        returning="binary_flag",
        find_first_match_in_period=True,
        discharged_to=hosp_discharge_list,
        with_these_diagnoses=covid_codes_ae,
        return_expectations={"incidence": 0.9},
    ),
    ae_attendance_second_date=patients.attended_emergency_care(
        between=["ae_attendance_first_date + 1 day", end_date],
        returning="date_arrived",
        find_first_match_in_period=True,
        discharged_to=hosp_discharge_list,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2021-01-01", "latest": "2021-02-01"},
            "rate": "exponential_increase",
        },
    ),
    ae_attendance_second_covid_status=patients.attended_emergency_care(
        between=[
            "ae_attendance_second_date",
            "ae_attendance_second_date",
        ],
        returning="binary_flag",
        find_first_match_in_period=True,
        discharged_to=hosp_discharge_list,
        with_these_diagnoses=covid_codes_ae,
        return_expectations={"incidence": 0.9},
    ),
    ae_attendance_third_date=patients.attended_emergency_care(
        between=["ae_attendance_second_date + 1 day", end_date],
        returning="date_arrived",
        find_first_match_in_period=True,
        discharged_to=hosp_discharge_list,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2021-01-01", "latest": "2021-02-01"},
            "rate": "exponential_increase",
        },
    ),
    ae_attendance_third_covid_status=patients.attended_emergency_care(
        between=[
            "ae_attendance_third_date",
            "ae_attendance_third_date",
        ],
        returning="binary_flag",
        find_first_match_in_period=True,
        discharged_to=hosp_discharge_list,
        with_these_diagnoses=covid_codes_ae,
        return_expectations={"incidence": 0.9},
    ),
    ae_attendance_fourth_date=patients.attended_emergency_care(
        between=["ae_attendance_third_date + 1 day", end_date],
        returning="date_arrived",
        find_first_match_in_period=True,
        discharged_to=hosp_discharge_list,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2021-01-01", "latest": "2021-02-01"},
            "rate": "exponential_increase",
        },
    ),
    ae_attendance_fourth_covid_status=patients.attended_emergency_care(
        between=[
            "ae_attendance_fourth_date",
            "ae_attendance_fourth_date",
        ],
        returning="binary_flag",
        find_first_match_in_period=True,
        discharged_to=hosp_discharge_list,
        with_these_diagnoses=covid_codes_ae,
        return_expectations={"incidence": 0.9},
    ),
    ae_attendance_fifth_date=patients.attended_emergency_care(
        between=["ae_attendance_fourth_date + 1 day", end_date],
        returning="date_arrived",
        find_first_match_in_period=True,
        discharged_to=hosp_discharge_list,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2021-01-01", "latest": "2021-02-01"},
            "rate": "exponential_increase",
        },
    ),
    ae_attendance_fifth_covid_status=patients.attended_emergency_care(
        between=[
            "ae_attendance_fifth_date",
            "ae_attendance_fifth_date",
        ],
        returning="binary_flag",
        find_first_match_in_period=True,
        discharged_to=hosp_discharge_list,
        with_these_diagnoses=covid_codes_ae,
        return_expectations={"incidence": 0.9},
    ),
)
