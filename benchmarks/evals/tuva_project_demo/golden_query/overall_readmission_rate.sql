/*
Last Fetched: December 26, 2025
Source: https://thetuvaproject.com/data-marts/readmissions
*/

-- The numerator is the number of encounters that are index admissions 
-- (i.e. that are eligible to have a readmission count against them)
-- and DID have an unplanned 30-day readmission:
select 
(select count(*)
from readmissions.readmission_summary
where index_admission_flag = 1 and unplanned_readmit_30_flag = 1) * 100
/
-- The denominator is the number of encounters that are index admissions 
-- (i.e. that are eligible to have a readmission count against them):
(select count(*)
from readmissions.readmission_summary
where index_admission_flag = 1) as overall_readmission_rate