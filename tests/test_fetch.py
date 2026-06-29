from pathlib import Path
import ssl

import adptracker.fetch as fetch_module
from adptracker.fetch import (
    ReleaseInfo,
    build_ssl_context,
    parse_release_info,
    sync_latest_national_csv,
    update_default_release_id,
)


def test_parse_release_info_finds_national_artifact() -> None:
    metadata = {
        "chartSections": [
            {
                "chartSubsections": [
                    {
                        "tab_title": "National",
                        "jsonFile": "https://adpemploymentreport.com/artifacts/us_ner/20260701/line_national.json",
                    }
                ]
            }
        ]
    }

    release = parse_release_info(metadata)

    assert release.release_id == "20260701"
    assert release.national_csv_url.endswith("/20260701/line_national.csv")


def test_sync_does_not_download_when_release_id_matches(tmp_path: Path) -> None:
    def load_release(
        metadata_url: str,
        timeout: float,
        ssl_context: ssl.SSLContext | None,
    ) -> ReleaseInfo:
        assert ssl_context is None
        return ReleaseInfo(
            release_id="20260603",
            national_csv_url="https://example.com/line_national.csv",
            national_json_url="https://example.com/line_national.json",
        )

    def fail_download(
        url: str,
        output_path: Path | str,
        timeout: float,
        ssl_context: ssl.SSLContext | None,
    ) -> Path:
        raise AssertionError("CSV should not download when release id matches")

    def fail_write(release_id: str) -> Path:
        raise AssertionError("release id should not update when it already matches")

    result = sync_latest_national_csv(
        current_release_id="20260603",
        output_path=tmp_path / "line_national.csv",
        release_info_loader=load_release,
        downloader=fail_download,
        release_id_writer=fail_write,
    )

    assert result.downloaded is False
    assert "no CSV downloaded" in result.message


def test_sync_downloads_and_updates_when_release_id_changes(tmp_path: Path) -> None:
    calls: dict[str, str] = {}

    def load_release(
        metadata_url: str,
        timeout: float,
        ssl_context: ssl.SSLContext | None,
    ) -> ReleaseInfo:
        assert ssl_context is None
        return ReleaseInfo(
            release_id="20260701",
            national_csv_url="https://example.com/20260701/line_national.csv",
            national_json_url="https://example.com/20260701/line_national.json",
        )

    def download(
        url: str,
        output_path: Path | str,
        timeout: float,
        ssl_context: ssl.SSLContext | None,
    ) -> Path:
        assert ssl_context is None
        calls["download_url"] = url
        path = Path(output_path)
        path.write_text("date,Private Employment\n", encoding="utf-8")
        return path

    def write_release(release_id: str) -> Path:
        calls["release_id"] = release_id
        return tmp_path / "config.py"

    result = sync_latest_national_csv(
        current_release_id="20260603",
        output_path=tmp_path / "line_national.csv",
        release_info_loader=load_release,
        downloader=download,
        release_id_writer=write_release,
    )

    assert result.downloaded is True
    assert calls == {
        "download_url": "https://example.com/20260701/line_national.csv",
        "release_id": "20260701",
    }


def test_update_default_release_id_rewrites_config_constant(tmp_path: Path) -> None:
    config_path = tmp_path / "config.py"
    config_path.write_text(
        'from pathlib import Path\n\nDEFAULT_RELEASE_ID = "20260603"\n',
        encoding="utf-8",
    )

    update_default_release_id("20260701", config_path)

    assert 'DEFAULT_RELEASE_ID = "20260701"' in config_path.read_text(encoding="utf-8")


def test_build_ssl_context_returns_none_without_ca_file() -> None:
    assert build_ssl_context() is None


def test_build_ssl_context_uses_ca_file(monkeypatch) -> None:
    calls: dict[str, str] = {}
    expected_context = object()

    def fake_create_default_context(*, cafile: str):
        calls["cafile"] = cafile
        return expected_context

    monkeypatch.setattr(fetch_module.ssl, "create_default_context", fake_create_default_context)

    assert build_ssl_context(ca_file="company-ca.pem") is expected_context
    assert calls == {"cafile": "company-ca.pem"}
