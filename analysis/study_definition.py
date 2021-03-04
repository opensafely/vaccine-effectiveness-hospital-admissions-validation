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

    ),


    #did they attend ae ever
    attended_ae = patients.attended_emergency_care(
        between=["index_date", end_date],
        returning="binary_flag",
        find_first_match_in_period=True,
        return_expectations={
            "incidence": 0.05
        }
        
    )

    # date of ae attendance
    attended_ae_date = patients.attended_emergency_care(
        between=["index_date", end_date],
        returning="date_arrived",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
    )

    # covid status of those admitted to ae
    attended_ae_covid_status = patients.attended_emergency_care(
        between=["index_date", end_date],
        returning="binary_flag",
        find_first_match_in_period=True,
        with_these_diagnoses=covid_codes,
    )

    # in those attending ae had they had recent positiv cov test
    positive_covid_test_before_admission = patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        between=["attended_ae_date - 2 weeks", "attended_ae_date"],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01",  "latest" : "2021-02-01"},
            "rate": "exponential_increase",
            "incidence": 0.1,
        },
    ),

    # in those attending ae had they had positive cov in pc
    covid_primary_care_before_admission = patients.with_these_clinical_events(
        codelist=covid_primary_care_codes,
        between=["attended_ae_date - 2 weeks", "attended_ae_date"],
        returning="binary_flag",
        return_expectations={
            "date": {"earliest": "2021-01-01",  "latest" : "2021-02-01"},
            "rate": "exponential_increase",
            "incidence": 0.1,
        },
    ),
    
    # does ae attendance lead to hosp admission
    ae_preceding_hospital_admission = patients.admitted_to_hospital(
        between["attended_ae_date", "attended_ae_date + 2 days"],
        returning="binary_flag",
        return_expectations={"incidence": 0.9}
    )


)
