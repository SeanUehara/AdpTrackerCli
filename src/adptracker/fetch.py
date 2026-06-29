from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
import urllib.request

from . import config
from .config import (
    ADP_PRODUCTION_JSON_URL,
    DEFAULT_CACHE_PATH,
    DEFAULT_NATIONAL_CSV_URL,
    DEFAULT_RELEASE_ID,
)


_RELEASE_ID_PATTERN = re.compile(r"/artifacts/us_ner/(?P<release_id>\d{8})/")
_DEFAULT_RELEASE_PATTERN = re.compile(
    r'(?m)^DEFAULT_RELEASE_ID\s*=\s*["\'](?P<release_id>\d{8})["\']'
)


@dataclass(frozen=True)
class ReleaseInfo:
    release_id: str
    national_csv_url: str
    national_json_url: str


@dataclass(frozen=True)
class FetchResult:
    release_id: str
    csv_path: Path
    downloaded: bool
    message: str

#Tradeoff: Fetches from the ADP website. Can create an email and subscribe to the ADP National Employment Report to get updates.
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


def sync_latest_national_csv(
    current_release_id: str = DEFAULT_RELEASE_ID,
    metadata_url: str = ADP_PRODUCTION_JSON_URL,
    output_path: Path | str = DEFAULT_CACHE_PATH,
    timeout: float = 30,
    release_info_loader: Callable[[str, float], ReleaseInfo] | None = None,
    downloader: Callable[[str, Path | str, float], Path] | None = None,
    release_id_writer: Callable[[str], Path] | None = None,
) -> FetchResult:
    loader = release_info_loader or fetch_latest_release_info
    download = downloader or fetch_national_csv
    write_release_id = release_id_writer or update_default_release_id

    release = loader(metadata_url, timeout)
    destination = Path(output_path)

    if release.release_id == current_release_id:
        return FetchResult(
            release_id=release.release_id,
            csv_path=destination,
            downloaded=False,
            message=f"ADP release {release.release_id} is already current; no CSV downloaded.",
        )

    csv_path = download(release.national_csv_url, destination, timeout)
    write_release_id(release.release_id)
    return FetchResult(
        release_id=release.release_id,
        csv_path=csv_path,
        downloaded=True,
        message=f"Downloaded ADP release {release.release_id} to {csv_path}.",
    )


def fetch_latest_release_info(
    metadata_url: str = ADP_PRODUCTION_JSON_URL,
    timeout: float = 30,
) -> ReleaseInfo:
    request = urllib.request.Request(
        metadata_url,
        headers={"User-Agent": "adptracker/0.1"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        metadata = json.loads(response.read().decode("utf-8"))

    return parse_release_info(metadata)


def parse_release_info(metadata: dict[str, Any]) -> ReleaseInfo:
    national_json_url = _find_national_json_url(metadata)
    match = _RELEASE_ID_PATTERN.search(national_json_url)
    if not match:
        raise ValueError(f"Could not find an ADP release ID in {national_json_url}")

    return ReleaseInfo(
        release_id=match.group("release_id"),
        national_csv_url=national_json_url.removesuffix(".json") + ".csv",
        national_json_url=national_json_url,
    )


def update_default_release_id(
    release_id: str,
    config_path: Path | str | None = None,
) -> Path:
    path = Path(config_path) if config_path is not None else Path(config.__file__)
    content = path.read_text(encoding="utf-8")
    updated, replacements = _DEFAULT_RELEASE_PATTERN.subn(
        f'DEFAULT_RELEASE_ID = "{release_id}"',
        content,
        count=1,
    )
    if replacements != 1:
        raise ValueError(f"Could not update DEFAULT_RELEASE_ID in {path}")

    path.write_text(updated, encoding="utf-8")
    return path


def _find_national_json_url(metadata: dict[str, Any]) -> str:
    for section in metadata.get("chartSections", []):
        for subsection in section.get("chartSubsections", []):
            json_file = subsection.get("jsonFile", "")
            if (
                subsection.get("tab_title") == "National"
                and isinstance(json_file, str)
                and json_file.endswith("/line_national.json")
            ):
                return json_file

    for value in _walk_values(metadata):
        if isinstance(value, str) and value.endswith("/line_national.json"):
            return value

    raise ValueError("Could not find line_national.json in ADP metadata")


def _walk_values(value: Any) -> list[Any]:
    if isinstance(value, dict):
        values: list[Any] = []
        for item in value.values():
            values.extend(_walk_values(item))
        return values
    if isinstance(value, list):
        values = []
        for item in value:
            values.extend(_walk_values(item))
        return values
    return [value]
