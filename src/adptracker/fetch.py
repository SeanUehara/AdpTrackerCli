from __future__ import annotations

import urllib.request
from pathlib import Path

from .config import DEFAULT_CACHE_PATH, DEFAULT_NATIONAL_CSV_URL


def fetch_national_csv(
    url: str = DEFAULT_NATIONAL_CSV_URL,
    output_path: Path | str = DEFAULT_CACHE_PATH,
    timeout: float = 30,
) -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "adptracker/0.1"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content = response.read()

    destination.write_bytes(content)
    return destination
