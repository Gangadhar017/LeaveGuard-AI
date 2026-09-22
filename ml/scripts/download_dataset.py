"""Download a curated subset of the PlantVillage dataset (color images).

Source: https://github.com/spMohanty/PlantVillage-Dataset (official mirror of
the PlantVillage dataset, CC-BY-SA licensed research data).

Only a bounded number of images per class is downloaded to keep the project
lightweight for a classical-ML pipeline. Counts are written to
ml/dataset/raw/download_manifest.json — those are the *actual* counts used.

Usage:
    python ml/scripts/download_dataset.py [--per-class 320] [--out ml/dataset/raw]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

REPO = "spMohanty/PlantVillage-Dataset"
BRANCH = "master"
LIST_URL = (
    f"https://api.github.com/repos/{REPO}/contents/raw/color/"
    "{{class_name}}?per_page=1000&page={page}"
)
RAW_URL = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/raw/color/{{class_name}}/{{name}}"

CLASSES = [
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
]

HEADERS = {"User-Agent": "leafguard-ai-dataset-downloader"}
EXTENSIONS = (".jpg", ".jpeg", ".png")


def list_class_files(class_name: str, per_class: int) -> list[str]:
    """List image filenames for one class (stops once per_class is reached)."""
    names: list[str] = []
    page = 1
    while len(names) < per_class and page <= 5:
        url = LIST_URL.format(class_name=class_name, page=page)
        req = urlrequest.Request(url, headers=HEADERS)
        with urlrequest.urlopen(req, timeout=30) as response:
            items = json.load(response)
        if not items:
            break
        for item in items:
            if item.get("type") == "file" and item["name"].lower().endswith(EXTENSIONS):
                names.append(item["name"])
                if len(names) == per_class:
                    break
        page += 1
    return names


def download_one(class_name: str, name: str, dest_dir: Path, retries: int = 3) -> bool:
    dest = dest_dir / name
    if dest.exists() and dest.stat().st_size > 0:
        return True
    url = RAW_URL.format(class_name=class_name, name=urlrequest.quote(name))
    for attempt in range(retries):
        try:
            req = urlrequest.Request(url, headers=HEADERS)
            with urlrequest.urlopen(req, timeout=60) as response:
                data = response.read()
            if len(data) < 500:
                raise URLError("suspiciously small file")
            dest.write_bytes(data)
            return True
        except (HTTPError, URLError, OSError) as exc:
            if attempt == retries - 1:
                print(f"  FAILED {class_name}/{name}: {exc}", file=sys.stderr)
                return False
            time.sleep(1 + attempt)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-class", type=int, default=320)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[1] / "dataset" / "raw")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, int] = {}

    for class_name in CLASSES:
        dest_dir = args.out / class_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        names = list_class_files(class_name, args.per_class)
        if not names:
            print(f"{class_name}: no files listed (API problem?)", file=sys.stderr)
            manifest[class_name] = 0
            continue

        done = 0
        with ThreadPoolExecutor(max_workers=12) as pool:
            futures = {pool.submit(download_one, class_name, n, dest_dir): n for n in names}
            for future in as_completed(futures):
                done += int(future.result())
                print(f"\r{class_name}: {done}/{len(names)}", end="", flush=True)
        print()
        manifest[class_name] = done

    total = sum(manifest.values())
    payload = {
        "source": f"https://github.com/{REPO} (raw/color)",
        "subset": f"first N files per class, N<={args.per_class}",
        "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "per_class": manifest,
        "total": total,
    }
    (args.out / "download_manifest.json").write_text(json.dumps(payload, indent=2))
    print(f"DONE: {total} images across {len(manifest)} classes -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
