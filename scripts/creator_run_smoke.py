"""Smoke-check an adaptive creator-run workspace.

Usage:
  python scripts/creator_run_smoke.py path/to/creator-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from chip_labs.creator_run import validate_creator_run


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-check an adaptive creator-run workspace.")
    parser.add_argument("run_dir", type=str, help="Creator-run directory.")
    parser.add_argument("--output", type=str, default=None, help="Optional output JSON file.")
    args = parser.parse_args()

    result = validate_creator_run(args.run_dir).to_dict()
    output = json.dumps(result, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()

