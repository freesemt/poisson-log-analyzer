"""Parser for the Apache/Nginx common and combined log formats."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Iterable, Iterator, Optional

_LINE = re.compile(
    r"^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "
    r'"(?P<request>(?:[^"\\]|\\.)*)" '
    r"(?P<status>\d{3}) (?P<size>\d+|-)"
)
_REQUEST = re.compile(r"^(?P<method>[A-Za-z]+) (?P<path>\S+)(?: .*)?$")
_TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


@dataclass(frozen=True)
class LogEntry:
    timestamp: datetime
    ip: str
    method: str  # "-" when the request line is missing or malformed (e.g. HTTP 400/408)
    path: str  # "-" when the request line is missing or malformed
    status: int
    size: int


def parse_line(line: str) -> Optional[LogEntry]:
    """Return the parsed entry, or None if the line is not a valid log line.

    Lines whose request is empty ("-") or malformed, as logged for HTTP 400/408,
    are kept with method and path "-": they are still requests.
    """
    m = _LINE.match(line)
    if m is None:
        return None
    try:
        ts = datetime.strptime(m["time"], _TIME_FORMAT)
    except ValueError:
        return None
    request = _REQUEST.match(m["request"])
    method, path = (request["method"].upper(), request["path"]) if request else ("-", "-")
    size = 0 if m["size"] == "-" else int(m["size"])
    return LogEntry(ts, m["ip"], method, path, int(m["status"]), size)


def parse_lines(
    lines: Iterable[str], on_skip: Optional[Callable[[str], None]] = None
) -> Iterator[LogEntry]:
    """Yield entries for valid lines; malformed lines are skipped.

    ``on_skip`` is called with each non-blank line that could not be parsed.
    """
    for line in lines:
        entry = parse_line(line)
        if entry is not None:
            yield entry
        elif on_skip is not None and line.strip():
            on_skip(line)
