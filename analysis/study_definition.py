from cohortextractor import StudyDefinition, patients, codelist, codelist_from_csv

# Import Codelists
from codelists import *

start_date = "2021-06-01"


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

hosp_discharge_list = [str(306706006), str(1066331000000109), str(1066391000000105), str(1066361000000104)]

ae_discharge_list = [str(key) for (key, value) in ae_discharge_dict.items()]


study = StudyDefinition(
    index_date=start_date,
    default_expectations={
        "date": {"earliest": "index_date", "latest": "index_date + 3 months"},
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
        (hospital_admission OR ae_attendance)
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
    ####
    # Any hospital admission or ae attendance
    ####
    # index date + 1 day to give time for hospital admission to appear
    hospital_admission=patients.admitted_to_hospital(
        returning="binary_flag",
        between=["index_date + 1 day", "index_date + 3 months"],
        date_format="YYYY-MM-DD",
        find_last_match_in_period=True,
        return_expectations={
            "incidence": 0.3,
        },
    ),
    ae_attendance=patients.attended_emergency_care(
        between=["index_date", "index_date + 3 months"],
        returning="binary_flag",
        find_last_match_in_period=True,
        return_expectations={"incidence": 0.4},
    ),
    ae_attendance_date=patients.attended_emergency_care(
        between=["index_date", "index_date + 3 months"],
        returning="date_arrived",
        date_format="YYYY-MM-DD",
        find_last_match_in_period=True,
        return_expectations={"incidence": 0.4},
    ),
    ae_attendance_hosp_discharge=patients.attended_emergency_care(
        between=["index_date", "index_date + 3 months"],
        returning="binary_flag",
        find_last_match_in_period=True,
        discharged_to=hosp_discharge_list,
        return_expectations={"incidence": 0.4},
    ),
    ae_attendance_hosp_discharge_date=patients.attended_emergency_care(
        between=["index_date", "index_date + 3 months"],
        returning="date_arrived",
        date_format="YYYY-MM-DD",
        find_last_match_in_period=True,
        discharged_to=hosp_discharge_list,
        return_expectations={"incidence": 0.4},
    ),
    ####
    # ae count
    ####
    ae_attendance_count=patients.attended_emergency_care(
        between=["index_date", "index_date + 3 months"],
        returning="number_of_matches_in_period",
        return_expectations={"int": {"distribution": "normal", "mean": 2, "stddev": 1}},
    ),
    ####
    # hospital admission
    ####
    emergency_covid_hospital_admission_date=patients.admitted_to_hospital(
        returning="date_admitted",
        with_these_diagnoses=covid_codes,
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
        between=["index_date + 1 day", "index_date + 3 months"],
        date_format="YYYY-MM-DD",
        find_last_match_in_period=True,
        return_expectations={
            "incidence": 0.8,
        },
    ),
    ####
    # satisfying ae before emergency covid hospital admission
    ####
    ae_before_date=patients.attended_emergency_care(
        between=[
            "emergency_covid_hospital_admission_date - 14 days",
            "emergency_covid_hospital_admission_date",
        ],
        returning="date_arrived",
        date_format="YYYY-MM-DD",
        find_last_match_in_period=True,
    ),
    ae_before_with_hospital_discharge_date=patients.attended_emergency_care(
        between=[
            "emergency_covid_hospital_admission_date - 14 days",
            "emergency_covid_hospital_admission_date",
        ],
        returning="date_arrived",
        date_format="YYYY-MM-DD",
        discharged_to=hosp_discharge_list,
        find_last_match_in_period=True,
    ),
    ae_before_with_covid=patients.attended_emergency_care(
        between=[
            "emergency_covid_hospital_admission_date - 14 days",
            "emergency_covid_hospital_admission_date",
        ],
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        with_these_diagnoses=covid_codes_ae,
        find_last_match_in_period=True,
    ),
    ae_before_with_hospital_discharge_covid=patients.attended_emergency_care(
        between=[
            "emergency_covid_hospital_admission_date - 14 days",
            "emergency_covid_hospital_admission_date",
        ],
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        with_these_diagnoses=covid_codes_ae,
        discharged_to=hosp_discharge_list,
        find_last_match_in_period=True,
    ),
    ae_before_with_resp=patients.attended_emergency_care(
        between=[
            "emergency_covid_hospital_admission_date - 14 days",
            "emergency_covid_hospital_admission_date",
        ],
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        with_these_diagnoses=respiratory_codes_ae,
        find_last_match_in_period=True,
    ),
    ae_before_with_hospital_discharge_resp=patients.attended_emergency_care(
        between=[
            "emergency_covid_hospital_admission_date - 14 days",
            "emergency_covid_hospital_admission_date",
        ],
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        with_these_diagnoses=respiratory_codes_ae,
        discharged_to=hosp_discharge_list,
        find_last_match_in_period=True,
    ),
    ae_before_with_prim_care_suspected=patients.with_these_clinical_events(
        codelist=covid_primary_care_suspected_codes,
        between=[
            "ae_before_date - 14 days",
            "ae_before_date",
        ],
        returning="binary_flag",
    ),
    ae_before_with_hospital_discharge_prim_care_suspected=patients.with_these_clinical_events(
        codelist=covid_primary_care_suspected_codes,
        between=[
            "ae_before_with_hospital_discharge_date - 14 days",
            "ae_before_with_hospital_discharge_date",
        ],
        returning="binary_flag",
    ),
    ae_before_with_prim_care_probable=patients.with_these_clinical_events(
        codelist=covid_primary_care_codes,
        between=[
            "ae_before_date - 14 days",
            "ae_before_date",
        ],
        returning="binary_flag",
    ),
    ae_before_with_hospital_discharge_prim_care_probable=patients.with_these_clinical_events(
        codelist=covid_primary_care_codes,
        between=[
            "ae_before_with_hospital_discharge_date - 14 days",
            "ae_before_with_hospital_discharge_date",
        ],
        returning="binary_flag",
    ),
    ae_before_with_positive_covid_test=patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=[
            "ae_before_date - 28 days",
            "ae_before_date +7 days",
        ],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01", "latest": "2021-02-01"},
            "rate": "exponential_increase",
        },
    ),
    ae_before_with_hospital_discharge_positive_covid_test=patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=[
            "ae_before_with_hospital_discharge_date - 28 days",
            "ae_before_with_hospital_discharge_date +7 days",
        ],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01", "latest": "2021-02-01"},
            "rate": "exponential_increase",
        },
    ),
    ae_before_with_positive_covid_test_2_weeks=patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=[
            "ae_before_date - 14 days",
            "ae_before_date +7 days",
        ],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01", "latest": "2021-02-01"},
            "rate": "exponential_increase",
        },
    ),
    ae_before_with_hospital_discharge_positive_covid_test_2_weeks=patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=[
            "ae_before_with_hospital_discharge_date - 14 days",
            "ae_before_with_hospital_discharge_date +7 days",
        ],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01", "latest": "2021-02-01"},
            "rate": "exponential_increase",
        },
    ),
    ####
    # satisfying ae attendances without subsequent hospitalisation
    ####
    # ae_attendance_date
    emergency_covid_hospital_admission_after_ae=patients.admitted_to_hospital(
        returning="binary_flag",
        with_these_diagnoses=covid_codes,
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
        between=[
            "ae_attendance_date",
            "ae_attendance_date + 14 days",
        ],
        date_format="YYYY-MM-DD",
        find_last_match_in_period=True,
        return_expectations={
            "incidence": 0.3,
        },
    ),
    emergency_covid_hospital_admission_after_ae_hosp_discharge=patients.admitted_to_hospital(
        returning="binary_flag",
        with_these_diagnoses=covid_codes,
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
        between=[
            "ae_attendance_hosp_discharge_date",
            "ae_attendance_hosp_discharge_date + 14 days",
        ],
        date_format="YYYY-MM-DD",
        find_last_match_in_period=True,
        return_expectations={
            "incidence": 0.3,
        },
    ),
    covid_primary_care_before_ae=patients.with_these_clinical_events(
        codelist=covid_primary_care_codes,
        between=[
            "ae_attendance_date - 14 days",
            "ae_attendance_date",
        ],
        returning="binary_flag",
    ),
    covid_primary_care_before_ae_hosp_discharge=patients.with_these_clinical_events(
        codelist=covid_primary_care_codes,
        between=[
            "ae_attendance_hosp_discharge_date - 14 days",
            "ae_attendance_hosp_discharge_date",
        ],
        returning="binary_flag",
    ),
    suspected_covid_primary_care_before_ae=patients.with_these_clinical_events(
        codelist=covid_primary_care_suspected_codes,
        between=[
            "ae_attendance_date - 14 days",
            "ae_attendance_date",
        ],
        returning="binary_flag",
    ),
    suspected_covid_primary_care_before_ae_hosp_discharge=patients.with_these_clinical_events(
        codelist=covid_primary_care_suspected_codes,
        between=[
            "ae_attendance_hosp_discharge_date - 14 days",
            "ae_attendance_hosp_discharge_date",
        ],
        returning="binary_flag",
    ),
    pos_test=patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=[
            "ae_attendance_date - 28 days",
            "ae_attendance_date + 7 days",
        ],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01", "latest": "2021-02-01"},
            "rate": "exponential_increase",
        },
    ),
    pos_test_hosp_discharge=patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=[
            "ae_attendance_hosp_discharge_date - 28 days",
            "ae_attendance_hosp_discharge_date + 7 days",
        ],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01", "latest": "2021-02-01"},
            "rate": "exponential_increase",
        },
    ),
    pos_test_2_weeks=patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=[
            "ae_attendance_date - 14 days",
            "ae_attendance_date + 7 days",
        ],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01", "latest": "2021-02-01"},
            "rate": "exponential_increase",
        },
    ),
    pos_test_2_weeks_hosp_discharge=patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=[
            "ae_attendance_hosp_discharge_date - 14 days",
            "ae_attendance_hosp_discharge_date + 7 days",
        ],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01", "latest": "2021-02-01"},
            "rate": "exponential_increase",
        },
    ),
    ae_cov=patients.attended_emergency_care(
        between=[
            "ae_attendance_date",
            "ae_attendance_date",
        ],
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        with_these_diagnoses=covid_codes_ae,
        find_last_match_in_period=True,
    ),
    ae_cov_hosp_discharge=patients.attended_emergency_care(
        between=[
            "ae_attendance_hosp_discharge_date",
            "ae_attendance_hosp_discharge_date",
        ],
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        with_these_diagnoses=covid_codes_ae,
        discharged_to=hosp_discharge_list,
        find_last_match_in_period=True,
    ),
    ae_resp=patients.attended_emergency_care(
        between=[
            "ae_attendance_date",
            "ae_attendance_date",
        ],
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        with_these_diagnoses=respiratory_codes_ae,
        find_last_match_in_period=True,
    ),
    ae_resp_hosp_discharge=patients.attended_emergency_care(
        between=[
            "ae_attendance_hosp_discharge_date",
            "ae_attendance_hosp_discharge_date",
        ],
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        with_these_diagnoses=respiratory_codes_ae,
        discharged_to=hosp_discharge_list,
        find_last_match_in_period=True,
    ),
    discharge_destination = patients.attended_emergency_care(
        between=[
            "ae_attendance_date",
            "ae_attendance_date",
        ],
        returning="discharge_destination",
        date_format="YYYY-MM-DD",
        find_last_match_in_period=True,
        return_expectations={
                "rate": "universal",
                "category": {"ratios": {"001": 0.49, "002": 0.51}},
            }
    ),
)
