/*
Last Fetched: December 26, 2025
Source: https://thetuvaproject.com/data-marts/chronic-conditions
*/

select
  condition
, count(distinct person_id) as total_patients
, cast(count(distinct person_id) * 100.0 / (select count(distinct person_id) from core.patient) as numeric(38,2)) as percent_of_patients
from chronic_conditions.tuva_chronic_conditions_long
group by 1
order by 3 desc