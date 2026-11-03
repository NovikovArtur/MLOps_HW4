select
    t.state_code,
    s.state_name,
    count() as transaction_count,
    countIf(t.is_fraud = 1) as fraud_count,
    {{ fraud_rate('countIf(t.is_fraud = 1)', 'count()') }} as fraud_rate,
    uniqExact(t.customer_id) as unique_customers,
    uniqExact(t.merchant) as unique_merchants,
    sum(t.amount) as total_amount,
    sumIf(t.amount, t.is_fraud = 1) as fraud_amount
from {{ ref('stg_transactions') }} as t
left join {{ ref('states') }} as s on t.state_code = s.state_code
group by t.state_code, s.state_name
