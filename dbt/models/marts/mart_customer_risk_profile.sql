with metrics as (
    select
        customer_id,
        count() as transaction_count,
        countIf(is_fraud = 1) as fraud_count,
        {{ fraud_rate('countIf(is_fraud = 1)', 'count()') }} as fraud_rate,
        sum(amount) as total_amount,
        avg(amount) as avg_amount,
        min(transaction_time) as first_transaction_time,
        max(transaction_time) as last_transaction_time,
        uniqExact(transaction_date) as active_days
    from {{ ref('stg_transactions') }}
    group by customer_id
)

select
    *,
    case
        when fraud_rate >= {{ var('high_risk_rate') }} then 'HIGH'
        when fraud_rate >= {{ var('medium_risk_rate') }} then 'MEDIUM'
        else 'LOW'
    end as risk_level
from metrics
