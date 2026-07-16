"""Bounded, symlink-safe local file discovery and reads."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


DEFAULT_MAX_SCAN_ENTRIES = 4_000
DEFAULT_MAX_SCAN_FILES = 1_000
DEFAULT_MAX_SCAN_BYTES = 32 * 1024 * 1024
DEFAULT_MAX_FILE_BYTES = 1024 * 1024


@dataclass
class ScanBudget:
    """One cumulative work budget shared by all roots in a logical scan."""

    max_entries: int = DEFAULT_MAX_SCAN_ENTRIES
    max_files: int = DEFAULT_MAX_SCAN_FILES
    max_bytes: int = DEFAULT_MAX_SCAN_BYTES
    entries_seen: int = 0
    files_seen: int = 0
    bytes_read: int = 0

    @property
    def exhausted(self) -> bool:
        return (
            self.entries_seen >= self.max_entries
            or self.files_seen >= self.max_files
        )


def iter_bounded_files(
    roots: Iterable[Path],
    *,
    suffixes: set[str] | None = None,
    budget: ScanBudget | None = None,
) -> Iterator[Path]:
    """Yield regular files without following links or exceeding scan work."""
    work = budget or ScanBudget()
    stack: list[Path] = []
    for root in reversed(list(roots)):
        candidate = Path(root)
        try:
            if candidate.is_symlink():
                continue
        except OSError:
            continue
        stack.append(candidate)
    while stack and not work.exhausted:
        directory = stack.pop()
        try:
            entries = os.scandir(directory)
        except OSError:
            continue
        with entries:
            for entry in entries:
                if work.entries_seen >= work.max_entries or work.files_seen >= work.max_files:
                    return
                work.entries_seen += 1
                try:
                    if entry.is_symlink():
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        stack.append(Path(entry.path))
                        continue
                    if not entry.is_file(follow_symlinks=False):
                        continue
                except OSError:
                    continue
                path = Path(entry.path)
                if suffixes is not None and path.suffix.lower() not in suffixes:
                    continue
                work.files_seen += 1
                yield path


def read_text_bounded(
    path: Path,
    *,
    budget: ScanBudget | None = None,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
) -> str:
    """Read UTF-8 text under both per-file and cumulative byte ceilings."""
    work = budget or ScanBudget()
    remaining = max(0, work.max_bytes - work.bytes_read)
    allowed = min(max_file_bytes, remaining)
    if allowed <= 0:
        return ""
    try:
        with Path(path).open("rb") as handle:
            payload = handle.read(allowed + 1)
    except OSError:
        return ""
    consumed = min(len(payload), allowed)
    work.bytes_read += consumed
    if len(payload) > allowed:
        return ""
    return payload.decode("utf-8", errors="ignore")
