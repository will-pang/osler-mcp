/*
Last Fetched: December 26, 2025
Source: https://thetuvaproject.com/data-marts/cms-hccs
*/

select
      patient.state
    , patient.city
    , patient.zip_code
    , avg(risk.payment_risk_score) as average_payment_risk_score
from cms_hcc.patient_risk_scores as risk
    inner join core.patient as patient
        on risk.person_id = patient.person_id
group by
      patient.state
    , patient.city
    , patient.zip_code;