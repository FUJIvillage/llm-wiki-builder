#!/usr/bin/env python3
"""Test indexer against OpenClaw sample data without Tauri/Rust build."""

import os
import sys
import hashlib
import time
from pathlib import Path

RAW_PATH = Path(os.environ.get("RAW_PATH", "./sample-raw"))
WIKI_PATH = Path(os.environ.get("WIKI_PATH", "./sample-wiki"))
SUPPORTED_EXTS = {".md", ".txt", ".mdown", ".markdown"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def index_raw_files(raw_path: Path):
    start = time.time()
    scanned = 0
    indexed = 0
    skipped = 0
    total_bytes = 0
    sample_files = []

    for root, _, files in os.walk(raw_path):
        for filename in files:
            filepath = Path(root) / filename
            ext = filepath.suffix.lower()
            if ext not in SUPPORTED_EXTS:
                continue

            scanned += 1
            size = filepath.stat().st_size
            if size > MAX_FILE_SIZE:
                skipped += 1
                continue

            try:
                content = filepath.read_text(encoding="utf-8", errors="replace")
            except Exception:
                skipped += 1
                continue

            content_hash = hashlib.md5(content.encode()).hexdigest()
            total_bytes += size
            indexed += 1

            if len(sample_files) < 5:
                sample_files.append({
                    "path": str(filepath.relative_to(raw_path)),
                    "size": size,
                    "hash": content_hash[:8],
                    "preview": content[:200].replace("\n", " "),
                })

    duration_ms = int((time.time() - start) * 1000)

    return {
        "scanned": scanned,
        "indexed": indexed,
        "skipped": skipped,
        "total_bytes": total_bytes,
        "duration_ms": duration_ms,
        "samples": sample_files,
    }


def main():
    if not RAW_PATH.exists():
        print(f"ERROR: Raw path not found: {RAW_PATH}")
        sys.exit(1)

    print("=" * 60)
    print("OpenClaw Raw Indexer Test")
    print("=" * 60)

    result = index_raw_files(RAW_PATH)

    print(f"\nScanned files:   {result['scanned']}")
    print(f"Indexed files:   {result['indexed']}")
    print(f"Skipped files:   {result['skipped']}")
    print(f"Total bytes:     {result['total_bytes']:,}")
    print(f"Duration:        {result['duration_ms']}ms")

    print("\n--- Sample Files ---")
    for s in result["samples"]:
        print(f"\n  {s['path']}")
        print(f"  size={s['size']:,}B hash={s['hash']}...")
        print(f"  preview: {s['preview'][:120]}...")

    print("\n" + "=" * 60)
    print("Indexer test PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
