/*
Last Fetched: January 2, 2026
Source: https://thetuvaproject.com/data-marts/readmissions
*/

with readmit as (
  select
    rs.drg_code as ms_drg_code,
    drg.ms_drg_description,
    sum(case when index_admission_flag = 1 then 1 else 0 end) as index_admissions,
    sum(case when index_admission_flag = 1
             and unplanned_readmit_30_flag = 1 then 1 else 0 end) as readmissions
  from readmissions.readmission_summary rs
  left join terminology.ms_drg drg
    on rs.drg_code = drg.ms_drg_code
  group by
    rs.drg_code,
    drg.ms_drg_description
)
select
  ms_drg_code,
  ms_drg_description,
  index_admissions,
  readmissions,
  case
    when index_admissions = 0 then 0
    else readmissions / index_admissions
  end as readmission_rate
from readmit
order by index_admissions desc
