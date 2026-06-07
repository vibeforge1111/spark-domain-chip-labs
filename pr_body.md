## Summary

JSON parsers commonly return `3.0` for integer-like values. Since `isinstance(3.0, int)` is `False` in Python, `_int_value` silently returns the default instead of the actual value. This causes false negatives in calibration checks when counts come as floats.

## Impact

- `_int_value(row.get("impression_count"), default=-1) > 0` rejects `{"impression_count": 3.0}` as having no impression denominator
- `_has_downstream_signal` misses signals when counts come as floats
- `minimum_rows` from JSON becomes 20 (default) instead of the actual value

## Fix

Accept float values that are mathematically integers:

```python
# Before
return value if isinstance(value, int) else default

# After
if isinstance(value, int):
    return value
if isinstance(value, float) and value.is_integer():
    return int(value)
return default
```

## CWE

CWE-682: Incorrect Calculation

<details>

```json
{"packet_version":"spark-compete-hotfix-v1","team_details":{"team_name":"Bug Hunters","team_lead_telegram":"@drophub_sir","members":[{"name":"Sampson","telegram":"@drophub_sir","github":"esc1200"},{"name":"ZakJan","telegram":"@Daraking2612","github":"ZakJan777"},{"name":"Saleem","telegram":"@Saleemkhan114","github":"dara917"}]},"issue":{"type":"bug","severity":"MEDIUM","cwe":"CWE-682","title":"_int_value rejects float values from JSON causing false negatives in calibration","affected_file":"src/chip_labs/content_outcome_calibration.py","affected_line_or_symbol":"240","owner_surface":"domain-chip-labs","evidence_types":["reproduction_steps","test_patch"],"reproduction_steps":"1. Pass {\"impression_count\": 3.0} to _int_value with default=-1 2. Returns -1 instead of 3 3. Calibration check incorrectly reports missing data","smoke_test":"python -c \"v=3.0; print(isinstance(v,int), isinstance(v,float) and v.is_integer())\""},"pr":{"url":"PLACEHOLDER","body_must_include":"CWE-682"}}
```

</details>
