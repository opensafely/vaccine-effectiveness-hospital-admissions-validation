
from cohortextractor import (
    codelist,
    codelist_from_csv,
    combine_codelists
)



covid_codes = codelist_from_csv(
    "codelists/opensafely-covid-identification.csv",
    system="icd10",
    column="icd10_code",
)

covid_codes_ae = codelist_from_csv(
    "analysis/covid_codes.csv",
    system="snomed",
    column="snomed_id",
)


covid_primary_care_positive_test = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-probable-covid-positive-test.csv",
    system="ctv3",
    column="CTV3ID",
)

covid_primary_care_code = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-probable-covid-clinical-code.csv",
    system="ctv3",
    column="CTV3ID",
)

covid_primary_care_sequalae = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-probable-covid-sequelae.csv",
    system="ctv3",
    column="CTV3ID",
)

covid_primary_care_codes = combine_codelists(covid_primary_care_positive_test, covid_primary_care_code, covid_primary_care_sequalae)

covid_primary_care_111_suspected = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-helper-111-suspected.csv",
    system="ctv3",
    column="CTV3ID",
)

covid_primary_care_advice_suspected = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-suspected-covid-advice.csv",
    system="ctv3",
    column="CTV3ID",
)

covid_primary_care_had_test_suspected = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-suspected-covid-had-test.csv",
    system="ctv3",
    column="CTV3ID",
)

covid_primary_care_isolation_suspected = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-suspected-covid-isolation-code.csv",
    system="ctv3",
    column="CTV3ID",
)

covid_primary_care_nonspecific_suspected = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-suspected-covid-nonspecific-clinical-assessment.csv",
    system="ctv3",
    column="CTV3ID",
)

covid_primary_care_codes_suspected = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-suspected-covid-suspected-codes.csv",
    system="ctv3",
    column="CTV3ID",
)

covid_primary_care_suspected_codes = combine_codelists(covid_primary_care_111_suspected, covid_primary_care_advice_suspected, covid_primary_care_codes_suspected, covid_primary_care_isolation_suspected, covid_primary_care_nonspecific_suspected, covid_primary_care_had_test_suspected)


high_risk_codes = codelist(
    ['1300561000000107'], system="snomed")

moderate_risk_codes = codelist(
    ['1300571000000100'], system="snomed")

low_risk_codes = codelist(
    ['1300591000000101'], system="snomed")
