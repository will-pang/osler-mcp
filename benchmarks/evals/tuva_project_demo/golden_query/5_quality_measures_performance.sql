/*
Last Fetched: December 26, 2025
Source: https://thetuvaproject.com/data-marts/quality-measures
*/

select
      measure_id
    , measure_name
    , performance_period_end
    , performance_rate
from quality_measures.summary_counts
order by performance_rate desc