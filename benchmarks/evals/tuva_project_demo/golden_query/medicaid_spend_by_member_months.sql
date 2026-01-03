/*
Last Fetched: January 2, 2026
Source: https://thetuvaproject.com/data-marts/financial-pmpm
*/

select
      data_source
    , year_month
    , cast(sum(medical_paid) as decimal(18,2)) as medical_paid
    , count(*) as member_months
    , cast(sum(medical_paid)/count(*) as decimal(18,2)) as pmpm
from financial_pmpm.pmpm_prep
group by
      data_source
    , year_month
order by
      data_source
    , year_month;