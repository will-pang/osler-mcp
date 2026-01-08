/*
Last Fetched: January 2, 2026
Source: https://thetuvaproject.com/data-marts/quality-measures
*/

select
      measure_id
    , exclusion_reason
    , count(person_id) as patient_count
from quality_measures.summary_long
where exclusion_flag = 1
group by
      measure_id
    , exclusion_reason
order by
      measure_id
    , exclusion_reason