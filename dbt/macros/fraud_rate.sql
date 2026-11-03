{% macro fraud_rate(fraud_count, total_count) -%}
    100.0 * {{ fraud_count }} / nullIf({{ total_count }}, 0)
{%- endmacro %}
