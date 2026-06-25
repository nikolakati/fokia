"""
One Film, Many Futures - frame extraction and preprocessing template.

This script has two modes:

1. extract_preprocess
   - extracts raw frames from a video with ffmpeg
   - computes simple technical metrics for every raw frame
   - writes data/curation_log.csv with all fields that can be filled automatically

2. build_curated
    - reads the manually reviewed data/curation_log.csv
    - copies/resizes frames marked final_decision=kept
    - writes data/metadata.csv and a blank data/annotations.csv template
    - protects an existing data/annotations.csv unless --overwrite-annotations is used
    - can clean old curated images first with --clean-curated-dir

Requirements:
    python -m pip install pillow

Also install ffmpeg:
    Windows: winget install --id Gyan.FFmpeg -e
    macOS:   brew install ffmpeg
    Linux:   sudo apt install ffmpeg

Example first run:
    python extract_preprocess_frames_template.py extract_preprocess \
        --video film.mp4 \
        --film-short nosferatu \
        --interval 10

After students manually review data/curation_log.csv and fill final_decision,
final_reason, reviewer and comment:

    python extract_preprocess_frames_template.py build_curated \
        --film-short nosferatu \
        --film-title "Nosferatu" \
        --film-year 1922 \
        --source-platform "Internet Archive" \
        --source-url "https://archive.org/details/..." \
        --license-status "public-domain claim by source; see source_rights_memo.md" \
        --access-date 2026-05-01 \
        --interval 10
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageFilter, ImageStat


TECHNICAL_REMOVE_REASONS = {
    "black_frame",
    "low_contrast",
    "blurred",
    "near_duplicate",
}


def timestamp_for_index(index: int, seconds_per_frame: int) -> str:
    seconds = (index - 1) * seconds_per_frame
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def read_frame_index(path: Path) -> int:
    # Works with names like nosferatu_raw_000001.jpg or film_raw_000001.jpg.
    return int(path.stem.split("_")[-1])


def average_hash(img: Image.Image) -> int:
    gray = img.convert("L").resize((8, 8), Image.Resampling.LANCZOS)
    pixels = list(gray.getdata())
    avg = sum(pixels) / len(pixels)
    bits = 0
    for pixel in pixels:
        bits = (bits << 1) | int(pixel >= avg)
    return bits


def hamming_distance(hash_a: int, hash_b: int) -> int:
    return (hash_a ^ hash_b).bit_count()


def blur_edge_score(img: Image.Image) -> float:
    # Simple edge-energy proxy. Low values usually mean very blurred or flat frames.
    edges = img.convert("L").filter(ImageFilter.FIND_EDGES)
    return ImageStat.Stat(edges).mean[0]


def resize_without_upscale(img: Image.Image, max_side: int) -> Image.Image:
    width, height = img.size
    longest = max(width, height)
    if longest <= max_side:
        return img
    scale = max_side / longest
    new_size = (round(width * scale), round(height * scale))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def run_ffmpeg_extract(video: Path, raw_dir: Path, film_short: str, interval: int) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    output_pattern = raw_dir / f"{film_short}_raw_%06d.jpg"
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video),
        "-vf",
        f"fps=1/{interval}",
        "-q:v",
        "3",
        str(output_pattern),
    ]
    print("Running:", " ".join(command))
    subprocess.run(command, check=True)


def technical_reason(row: dict, thresholds: argparse.Namespace) -> str:
    if row["brightness"] < thresholds.dark_threshold:
        return "black_frame"
    if row["contrast"] < thresholds.low_contrast_threshold:
        return "low_contrast"
    if row["blur_edge_score"] < thresholds.blur_threshold:
        return "blurred"
    if row["duplicate_distance"] <= thresholds.duplicate_distance_threshold:
        return "near_duplicate"
    return "usable_candidate"


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def mode_extract_preprocess(args: argparse.Namespace) -> None:
    video = Path(args.video)
    raw_dir = Path(args.raw_dir)
    curation_log = Path(args.curation_log)

    if not args.skip_extraction:
        run_ffmpeg_extract(video, raw_dir, args.film_short, args.interval)

    raw_files = sorted(raw_dir.glob("*.jpg"), key=read_frame_index)
    if not raw_files:
        raise SystemExit(f"No .jpg raw frames found in {raw_dir}")

    if len(raw_files) < 300:
        print(f"WARNING: found {len(raw_files)} raw frames. The assignment asks for at least 300.")

    rows = []
    previous_hash = None
    previous_raw_frame_id = ""

    for path in raw_files:
        index = read_frame_index(path)
        raw_frame_id = f"{args.film_short}_raw_{index:06d}"

        with Image.open(path) as img:
            gray = img.convert("L")
            stat = ImageStat.Stat(gray)
            brightness = round(stat.mean[0], 3)
            contrast = round(stat.stddev[0], 3)
            edge_score = round(blur_edge_score(img), 3)
            phash = average_hash(img)
            duplicate_distance = (
                hamming_distance(previous_hash, phash)
                if previous_hash is not None
                else 64
            )

        duplicate_of = ""
        if previous_hash is not None and duplicate_distance <= args.duplicate_distance_threshold:
            duplicate_of = previous_raw_frame_id

        row = {
            "raw_frame_id": raw_frame_id,
            "raw_filename": str(path).replace("\\", "/"),
            "frame_number": index,
            "timestamp": timestamp_for_index(index, args.interval),
            "extraction_rate": f"1 frame / {args.interval} sec",
            "brightness": brightness,
            "contrast": contrast,
            "blur_edge_score": edge_score,
            "perceptual_hash": f"{phash:016x}",
            "duplicate_distance": duplicate_distance,
            "duplicate_of": duplicate_of,
        }
        reason = technical_reason(row, args)
        row["script_suggestion"] = "remove" if reason in TECHNICAL_REMOVE_REASONS else "review"
        row["script_reason"] = reason
        row["final_decision"] = ""
        row["final_reason"] = ""
        row["final_curated_image_id"] = ""
        row["final_curated_filename"] = ""
        row["reviewer"] = ""
        row["comment"] = ""
        rows.append(row)

        previous_hash = phash
        previous_raw_frame_id = raw_frame_id

    fieldnames = [
        "raw_frame_id",
        "raw_filename",
        "frame_number",
        "timestamp",
        "extraction_rate",
        "brightness",
        "contrast",
        "blur_edge_score",
        "perceptual_hash",
        "duplicate_distance",
        "duplicate_of",
        "script_suggestion",
        "script_reason",
        "final_decision",
        "final_reason",
        "final_curated_image_id",
        "final_curated_filename",
        "reviewer",
        "comment",
    ]
    write_csv(curation_log, rows, fieldnames)
    print(f"Wrote {curation_log} with {len(rows)} rows.")
    print("Next step: manually review final_decision, final_reason, reviewer and comment.")


def mode_build_curated(args: argparse.Namespace) -> None:
    curation_log = Path(args.curation_log)
    curated_dir = Path(args.curated_dir)
    metadata_path = Path(args.metadata)
    annotations_path = Path(args.annotations)
    curated_dir.mkdir(parents=True, exist_ok=True)

    if args.clean_curated_dir:
        removed_count = 0
        for item in curated_dir.iterdir():
            if item.is_file() and item.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                item.unlink()
                removed_count += 1
            elif item.is_file():
                print(f"Skipping non-image file in curated dir: {item}")
            elif item.is_dir():
                print(f"Skipping subdirectory in curated dir: {item}")
        print(f"Cleaned {removed_count} old curated image files from {curated_dir}")

    rows = read_csv(curation_log)
    kept_rows = [row for row in rows if row.get("final_decision", "").strip().lower() == "kept"]

    if len(kept_rows) < 120:
        print(f"WARNING: only {len(kept_rows)} rows have final_decision=kept. The assignment asks for at least 120.")

    metadata_rows = []
    annotation_rows = []

    for new_index, row in enumerate(kept_rows, start=1):
        image_id = row.get("final_curated_image_id") or f"{args.film_short}_{int(row['frame_number']):06d}"
        filename = row.get("final_curated_filename") or f"{image_id}.jpg"
        raw_path = Path(row["raw_filename"])
        output_path = curated_dir / filename

        with Image.open(raw_path) as img:
            processed = resize_without_upscale(img, args.max_side)
            processed.save(output_path, quality=92)

        row["final_curated_image_id"] = image_id
        row["final_curated_filename"] = filename

        metadata_rows.append({
            "image_id": image_id,
            "frame_filename": filename,
            "film_title": args.film_title,
            "film_year": args.film_year,
            "source_platform": args.source_platform,
            "source_url": args.source_url,
            "license_status": args.license_status,
            "access_date": args.access_date,
            "timestamp": row["timestamp"],
            "extraction_rate": row["extraction_rate"],
            "curation_decision": row["final_decision"],
            "notes": row.get("comment", ""),
        })

        annotation_rows.append({
            "image_id": image_id,
            "frame_filename": filename,
            "primary_object_label": "",
            "secondary_object_labels": "",
            "narrative_label": "",
            "confidence": "",
            "requires_context": "",
            "annotator_id": "",
            "annotator_notes": "",
        })

    # Save updated curation log with generated curated IDs/filenames.
    write_csv(curation_log, rows, list(rows[0].keys()))

    write_csv(metadata_path, metadata_rows, [
        "image_id",
        "frame_filename",
        "film_title",
        "film_year",
        "source_platform",
        "source_url",
        "license_status",
        "access_date",
        "timestamp",
        "extraction_rate",
        "curation_decision",
        "notes",
    ])
    annotation_fieldnames = [
        "image_id",
        "frame_filename",
        "primary_object_label",
        "secondary_object_labels",
        "narrative_label",
        "confidence",
        "requires_context",
        "annotator_id",
        "annotator_notes",
    ]

    if annotations_path.exists() and not args.overwrite_annotations:
        print(
            f"WARNING: {annotations_path} already exists. "
            "It was not overwritten. Use --overwrite-annotations to replace it."
        )
    else:
        write_csv(annotations_path, annotation_rows, annotation_fieldnames)
        print(f"Wrote blank annotation template {annotations_path}")

    print(f"Curated images: {len(metadata_rows)}")
    print(f"Wrote {metadata_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract frames, preprocess, and build dataset CSV templates.")
    sub = parser.add_subparsers(dest="mode", required=True)

    p1 = sub.add_parser("extract_preprocess")
    p1.add_argument("--video", default="film.mp4")
    p1.add_argument("--film-short", required=True)
    p1.add_argument("--interval", type=int, default=10)
    p1.add_argument("--raw-dir", default="raw_frames")
    p1.add_argument("--curation-log", default="data/curation_log.csv")
    p1.add_argument("--skip-extraction", action="store_true", help="Use existing raw_frames instead of running ffmpeg.")
    p1.add_argument("--dark-threshold", type=float, default=18)
    p1.add_argument("--low-contrast-threshold", type=float, default=12)
    p1.add_argument("--blur-threshold", type=float, default=4)
    p1.add_argument("--duplicate-distance-threshold", type=int, default=5)
    p1.set_defaults(func=mode_extract_preprocess)

    p2 = sub.add_parser("build_curated")
    p2.add_argument("--film-short", required=True)
    p2.add_argument("--film-title", required=True)
    p2.add_argument("--film-year", required=True)
    p2.add_argument("--source-platform", required=True)
    p2.add_argument("--source-url", required=True)
    p2.add_argument("--license-status", required=True)
    p2.add_argument("--access-date", required=True)
    p2.add_argument("--curation-log", default="data/curation_log.csv")
    p2.add_argument("--curated-dir", default="data/images/curated")
    p2.add_argument("--metadata", default="data/metadata.csv")
    p2.add_argument("--annotations", default="data/annotations.csv")
    p2.add_argument(
        "--overwrite-annotations",
        action="store_true",
        help="Overwrite data/annotations.csv if it already exists.",
    )
    p2.add_argument(
        "--clean-curated-dir",
        action="store_true",
        help="Remove old .jpg/.jpeg/.png files from the curated image folder before rebuilding it.",
    )
    p2.add_argument("--max-side", type=int, default=768)
    p2.set_defaults(func=mode_build_curated)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
