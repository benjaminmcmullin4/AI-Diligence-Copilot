"""Load pre-computed demo analyses into the database on first run."""

import json
from pathlib import Path

from core.database import get_analysis, init_db, save_analysis

DEMO_DIR = Path(__file__).parent / "samples"

DEMO_FILES = [
    "acme_saas.json",
    "peak_health.json",
    "summit_retail.json",
]


def load_demo_samples(db_path: str | Path) -> None:
    """Load demo analyses into DB if they don't already exist."""
    init_db(db_path)

    for filename in DEMO_FILES:
        filepath = DEMO_DIR / filename
        if not filepath.exists():
            continue

        with open(filepath) as f:
            data = json.load(f)

        analysis_id = data.get("id", filename.replace(".json", ""))
        if get_analysis(db_path, analysis_id) is not None:
            continue

        save_analysis(db_path, analysis_id, {
            "company_name": data["company_name"],
            "business_model": data["business_model"],
            "status": "completed",
            "request_json": json.dumps(data.get("request", {})),
            "condensed_json": json.dumps(data.get("condensed", {})),
            "analysis_json": json.dumps(data.get("analysis", {})),
            "memo_json": json.dumps(data.get("memo", {})),
            "memo_markdown": data.get("memo_markdown", ""),
            "is_demo": 1,
        })
