/*
Last Fetched: December 26, 2025
Source: https://thetuvaproject.com/data-marts/ed-classification
*/

select
      p.ccsr_category
    , p.ccsr_category_description
    , p.ccsr_parent_category
    , p.body_system
    , count(*) as visit_count
    , sum(cast(e.paid_amount as decimal(18,2))) as paid_amount
    , cast(sum(e.paid_amount)/count(*) as decimal(18,2))as paid_per_visit
from core.encounter e
    left join ccsr.long_condition_category p
        on e.primary_diagnosis_code = p.normalized_code
        and p.condition_rank = 1
where e.encounter_type = 'emergency department'
group by
      p.ccsr_category
    , p.ccsr_category_description
    , p.ccsr_parent_category
    , p.body_system
order by visit_count desc;