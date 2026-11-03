{% macro amount_bucket(column) -%}
    case
        when {{ column }} < {{ var('medium_amount') }} then 'SMALL'
        when {{ column }} < {{ var('large_amount') }} then 'MEDIUM'
        else 'LARGE'
    end
{%- endmacro %}
