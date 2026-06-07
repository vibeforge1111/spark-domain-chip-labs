## Summary

`_execute_subprocess()` reads `output_path` AFTER the `TemporaryDirectory` context manager exits, which deletes the temp directory and all files. If the subprocess wrote output to the file (not stdout), that output is silently lost — `_parse_hook_output` finds the file missing and falls back to stdout.

## Root Cause

```python
with tempfile.TemporaryDirectory(prefix="chip-hook-") as tmpdir:
    # ... create files, run subprocess ...
    proc = subprocess.run(...)

# ← tmpdir deleted here, output_path no longer exists!

if proc.returncode == 0:
    output = _parse_hook_output(output_path, proc.stdout)  # reads deleted file
```

## Fix

Move the `if/else` block that reads `output_path` inside the `with` block.

## CWE

CWE-459: Incomplete Cleanup

<details>

```json
{"packet_version":"spark-compete-hotfix-v1","team_details":{"team_name":"Bug Hunters","team_lead_telegram":"@drophub_sir","members":[{"name":"Sampson","telegram":"@drophub_sir","github":"esc1200"},{"name":"ZakJan","telegram":"@Daraking2612","github":"ZakJan777"},{"name":"Saleem","telegram":"@Saleemkhan114","github":"dara917"}]},"issue":{"type":"bug","severity":"HIGH","cwe":"CWE-459","title":"Hook output file read after TemporaryDirectory cleanup causes silent data loss","affected_file":"src/chip_labs/intelligence_serving/chip_runtime.py","affected_line_or_symbol":"250","owner_surface":"domain-chip-labs","evidence_types":["reproduction_steps","test_patch"],"reproduction_steps":"1. Chip hook writes output to file (not stdout) 2. TemporaryDirectory exits, deleting output file 3. _parse_hook_output finds file missing, falls back to stdout 4. Hook output silently lost","smoke_test":"N/A — structural bug in context manager scope"},"pr":{"url":"PLACEHOLDER","body_must_include":"CWE-459"}}
```

</details>
