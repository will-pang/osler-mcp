/*
Last Fetched: January 2, 2026
Source: https://thetuvaproject.com/data-marts/chronic-conditions
*/

with patients as (
select person_id
from core.patient
)

, conditions as (
select distinct
  a.person_id
, b.condition
from patients a
left join chronic_conditions.tuva_chronic_conditions_long b
 on a.person_id = b.person_id
)

, condition_count as (
select
  person_id
, count(distinct condition) as condition_count
from conditions
group by 1
)

select 
  condition_count
, count(1)
, cast(100 * count(distinct person_id)/sum(count(distinct person_id)) over() as numeric(38,1)) as percent
from condition_count
group by 1
order by 1