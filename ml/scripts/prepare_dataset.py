"""Split the raw dataset into stratified train/validation/test directories.

Input : ml/dataset/raw/<ClassName>/*.jpg
Output: ml/dataset/processed/{train,validation,test}/<ClassName>/*.jpg
        + manifest.csv + dataset_report.json (actual counts, no fabrication)

Usage:
    python ml/scripts/prepare_dataset.py [--raw ml/dataset/raw] [--out ml/dataset/processed]
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import shutil
from pathlib import Path

SPLITS = {"train": 0.70, "validation": 0.15, "test": 0.15}
SEED = 42
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def split_counts(n: int) -> dict[str, int]:
    """Deterministic 70/15/15 split sizes (min 1 in val/test when n >= 4)."""
    train = round(n * SPLITS["train"])
    val = round(n * SPLITS["validation"])
    test = n - train - val
    if n >= 4:
        val, test = max(1, val), max(1, test)
        if train + val + test != n:
            train = n - val - test
    return {"train": train, "validation": val, "test": test}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=Path(__file__).resolve().parents[1] / "dataset" / "raw")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[1] / "dataset" / "processed")
    args = parser.parse_args()

    rng = random.Random(SEED)
    class_dirs = sorted(d for d in args.raw.iterdir() if d.is_dir())
    if not class_dirs:
        raise SystemExit(f"No class folders found in {args.raw}. Run download_dataset.py first.")

    for split in SPLITS:
        # OneDrive/Windows can transiently lock dirs — stale files are
        # overwritten by copy2 anyway, so removal failures are non-fatal
        if (args.out / split).exists():
            shutil.rmtree(args.out / split, ignore_errors=True)

    rows: list[dict] = []
    report: dict[str, dict] = {}

    for class_dir in class_dirs:
        files = sorted(p for p in class_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS)
        rng.shuffle(files)
        counts = split_counts(len(files))

        offset = 0
        for split, count in counts.items():
            dest_dir = args.out / split / class_dir.name
            dest_dir.mkdir(parents=True, exist_ok=True)
            for image in files[offset: offset + count]:
                shutil.copy2(image, dest_dir / image.name)
                rows.append({"split": split, "class": class_dir.name, "filepath": str(dest_dir / image.name)})
            offset += count

        report[class_dir.name] = {"total": len(files), **counts}

    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["split", "class", "filepath"])
        writer.writeheader()
        writer.writerows(rows)

    payload = {
        "seed": SEED,
        "split_ratios": SPLITS,
        "total_images": sum(r["total"] for r in report.values()),
        "num_classes": len(report),
        "per_class": report,
    }
    (args.out / "dataset_report.json").write_text(json.dumps(payload, indent=2))

    print(f"Split {payload['total_images']} images / {payload['num_classes']} classes "
          f"-> {args.out} (train {sum(c['train'] for c in report.values())}, "
          f"val {sum(c['validation'] for c in report.values())}, "
          f"test {sum(c['test'] for c in report.values())})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
