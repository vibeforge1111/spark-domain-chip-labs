# Absorption Bundle

Fresh agents working on Memory Doctor should preserve three boundaries:

1. Diagnose before repair. A doctor report can recommend a forget command, but it should not mutate memory.
2. Separate active truth from historical trace. "Maya appears in traces" and "Maya is active preferred_name" are different findings.
3. Preserve Telegram usefulness. The natural-language path should return a short answer; CLI JSON can hold full traces.

## Minimal Probe

Run:

```bash
python -m pytest tests/test_telegram_generic_memory.py -q -k "memory_doctor or multiple_generic_deletions"
python -m pytest tests/test_gateway_ask_telegram.py -q -k "memory_doctor"
```

Then run a live local check:

```bash
python -m spark_intelligence.cli memory doctor --home C:\Users\USER\.spark\state\spark-intelligence --human-id human:telegram:8319079055 --topic Maya
```

Expected behavior: partial delete integrity failures should be explicit; active profile should show Cem as preferred_name; Maya trace mentions should not override active profile.
