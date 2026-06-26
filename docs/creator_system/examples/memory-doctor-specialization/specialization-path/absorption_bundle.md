# Absorption Bundle

Fresh agents working on Memory Doctor should preserve three boundaries:

1. Diagnose before repair. A doctor report can recommend a forget command, but it should not mutate memory.
2. Separate active truth from historical trace. "Assistant appears in traces" and "Assistant is active operator_label" are different findings.
3. Preserve Telegram usefulness. The natural-language path should return a short answer; CLI JSON can hold full traces.

## Minimal Probe

Run:

```bash
python -m pytest tests/test_telegram_generic_memory.py -q -k "memory_doctor or multiple_generic_deletions"
python -m pytest tests/test_gateway_ask_telegram.py -q -k "memory_doctor"
```

Then run a live local check:

```bash
python -m spark_intelligence.cli memory doctor --home C:\Users\<operator>\.spark\state\spark-intelligence:telegram:0000000000 --topic Assistant
```

Expected behavior: partial delete integrity failures should be explicit; active profile should show operator as operator_label; Assistant trace mentions should not override active profile.
