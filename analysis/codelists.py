from cohortextractor import codelist, codelist_from_csv, combine_codelists


covid_codes = codelist_from_csv(
    "codelists/opensafely-covid-identification.csv",
    system="icd10",
    column="icd10_code",
)

covid_codes_ae = codelist_from_csv(
    "codelists/opensafely-covid-ae-diagnosis-codes.csv",
    system="snomed",
    column="snomed_id",
)
