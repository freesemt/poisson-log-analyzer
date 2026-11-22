"""Parser for the Apache/Nginx common and combined log formats."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Iterator, Optional

_LINE = re.compile(
    r"^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "
    r'"(?P<method>[A-Z]+) (?P<path>\S+)(?: [^"]*)?" '
    r"(?P<status>\d{3}) (?P<size>\d+|-)"
)
_TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


@dataclass(frozen=True)
class LogEntry:
    timestamp: datetime
    ip: str
    method: str
    path: str
    status: int
    size: int


def parse_line(line: str) -> Optional[LogEntry]:
    """Return the parsed entry, or None if the line is not a valid log line."""
    m = _LINE.match(line)
    if m is None:
        return None
    try:
        ts = datetime.strptime(m["time"], _TIME_FORMAT)
    except ValueError:
        return None
    size = 0 if m["size"] == "-" else int(m["size"])
    return LogEntry(ts, m["ip"], m["method"], m["path"], int(m["status"]), size)


def parse_lines(lines: Iterable[str]) -> Iterator[LogEntry]:
    """Yield entries for valid lines; malformed lines are skipped."""
    for line in lines:
        entry = parse_line(line)
        if entry is not None:
            yield entry
