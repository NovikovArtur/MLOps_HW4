select
    category,
    count() as transaction_count,
    countIf(is_fraud = 1) as fraud_count,
    {{ fraud_rate('countIf(is_fraud = 1)', 'count()') }} as fraud_rate,
    sum(amount) as total_amount,
    sumIf(amount, is_fraud = 1) as fraud_amount
from {{ ref('stg_transactions') }}
group by category
