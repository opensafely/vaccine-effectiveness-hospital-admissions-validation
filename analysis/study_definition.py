from cohortextractor import StudyDefinition, patients, codelist, codelist_from_csv


start_date="2020-09-01"
end_date="2021-01-01"

study = StudyDefinition(
    index_date=start_date
    default_expectations={
        "date": {"earliest": "1900-01-01", "latest": "today"},
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
        """,
        registered=patients.registered_as_of(
            "index_date",
        ),
        has_died=patients.died_from_any_cause(
            on_or_before="index_date",
            returning="binary_flag",
        ),
    ),


    # https://github.com/opensafely/risk-factors-research/issues/49
    age=patients.age_as_of(
        "index_date",
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
            "incidence" : 0.001
        },
    ),
    
    # https://github.com/opensafely/risk-factors-research/issues/46
    sex=patients.sex(
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"M": 0.49, "F": 0.51}},
        }
    ),

    attended_ae = patients.attended_emergency_care(
        between=["index_date", end_date],
        returning="binary_flag",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        return_expectations={
            "incidence": 0.05
        }
        
    )

    attended_ae_date = patients.attended_emergency_care(
        between=["index_date", end_date],
        returning="date_arrived",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
    )

    attended_ae_for_covid = patients.attended_emergency_care(
        between=["index_date", end_date],
        returning="binary_flag",
        find_first_match_in_period=True,
        with_these_diagnoses=covid_codes,
    )

    attended_ae_for_respiratory = patients.attended_emergency_care(
        between=["index_date", end_date],
        returning="binary_flag",
        find_first_match_in_period=True,
        with_these_diagnoses=respiratory_codes,
    )

    recent_positive_covid_test_before_admission = patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=["attended_ae_date - 2 weeks", "attended_ae_date"],
        returning="binary_flag",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2021-01-01",  "latest" : "2021-02-01"},
            "rate": "exponential_increase",
            "incidence": 0.1,
        },
    ),


)
