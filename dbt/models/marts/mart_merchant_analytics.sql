with metrics as (
    select
        merchant,
        count() as transaction_count,
        countIf(is_fraud = 1) as fraud_count,
        {{ fraud_rate('countIf(is_fraud = 1)', 'count()') }} as fraud_rate,
        sum(amount) as total_amount,
        sumIf(amount, is_fraud = 1) as fraud_amount,
        avg(amount) as avg_amount,
        uniqExact(customer_id) as unique_customers
    from {{ ref('stg_transactions') }}
    group by merchant
)

select
    *,
    toUInt8(
        fraud_rate >= {{ var('high_risk_rate') }}
        and transaction_count >= {{ var('merchant_min_transactions') }}
    ) as is_suspicious
from metrics
