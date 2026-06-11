"""Fail CI if tracked files contain operator-specific identifiers."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LeakRule:
    name: str
    pattern: re.Pattern[str]


PERSONA_NAMES = ("Ma" + "ya",)

RULES = (
    LeakRule("telegram-id", re.compile(r"telegram:(?!0+\b)\d{6,}")),
    LeakRule("human-telegram-id", re.compile(r"human:telegram:(?!0+\b)\d+")),
    LeakRule("spark-home-path", re.compile(r"C:[\\/]+Users[\\/]+USER[\\/]+[.]spark")),
    LeakRule(
        "operator-persona-name",
        re.compile(r"\b(?:" + "|".join(re.escape(name) for name in PERSONA_NAMES) + r")\b"),
    ),
    LeakRule(
        "preferred-name-assignment",
        re.compile(r"preferred_name\s*=\s*(?!<operator>\b)(?:\"[^\"]+\"|'[^']+'|[A-Za-z][\w-]*)"),
    ),
)


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files"], text=True)
    return [Path(line) for line in output.splitlines() if line]


def find_hits(paths: list[Path]) -> list[tuple[Path, str]]:
    hits: list[tuple[Path, str]] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for rule in RULES:
            if rule.pattern.search(text):
                hits.append((path, rule.name))
    return hits


def main() -> int:
    hits = find_hits(tracked_files())
    if hits:
        for path, rule_name in hits:
            print(f"LEAK {path}: {rule_name}")
        return 1
    print("no personal identifiers in tracked files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
