from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PACKAGE_ROOT / "data"

DEFAULT_RELEASE_ID = "20260603"
DEFAULT_NATIONAL_CSV_URL = (
    f"https://adpemploymentreport.com/artifacts/us_ner/{DEFAULT_RELEASE_ID}/line_national.csv"
)

DEFAULT_HISTORY_PATH = DATA_DIR / "ADP_NER_history.csv"
DEFAULT_CACHE_PATH = DATA_DIR / "line_national.csv"
