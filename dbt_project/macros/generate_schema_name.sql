{% macro create_schema(relation) -%}
  {{ log("Tentative de création du schéma : " ~ relation.schema, info=True) }}
  {%- call statement('create_schema') -%}
    SELECT pg_advisory_xact_lock(hashtext('create_schema_' || '{{ relation.schema }}'));
    
    CREATE SCHEMA IF NOT EXISTS "{{ relation.schema | trim }}";
  {%- endcall -%}
{%- endmacro %}