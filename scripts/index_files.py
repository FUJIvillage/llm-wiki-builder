#!/usr/bin/env python3
"""Index OpenClaw raw files for query generation."""

import json
import os
import re
from pathlib import Path
from datetime import datetime

RAW_DIR = os.environ.get("RAW_DIR", "")
if not RAW_DIR:
    raise ValueError("Please set RAW_DIR environment variable to your raw files directory")
OUTPUT_FILE = os.environ.get("INDEX_OUTPUT", "data/file_index.json")


def extract_date_from_filename(filename: str) -> str:
    """Extract YYYY-MM-DD from filename."""
    match = re.match(r"(\d{4}-\d{2}-\d{2})", filename)
    return match.group(1) if match else "unknown"


def read_file_chunk(filepath: Path, max_chars: int = 3000) -> dict:
    """Read file and return metadata + truncated content."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        return {
            "filename": filepath.name,
            "date": extract_date_from_filename(filepath.name),
            "size": 0,
            "error": str(e),
            "content": "",
        }
    
    # Truncate if too long (keep first and last part)
    if len(content) > max_chars:
        half = max_chars // 2
        content = content[:half] + "\n\n... [truncated] ...\n\n" + content[-half:]
    
    return {
        "filename": filepath.name,
        "date": extract_date_from_filename(filepath.name),
        "size": filepath.stat().st_size,
        "word_count": len(content.split()),
        "content": content,
    }


def index_files(raw_dir: str, max_files: int = None) -> list:
    """Index all markdown files in raw directory."""
    raw_path = Path(raw_dir)
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw directory not found: {raw_dir}")
    
    files = sorted(raw_path.glob("*.md"))
    if max_files:
        files = files[:max_files]
    
    print(f"[Index] Found {len(files)} files in {raw_dir}")
    
    indexed = []
    for filepath in files:
        entry = read_file_chunk(filepath)
        indexed.append(entry)
        if len(indexed) % 50 == 0:
            print(f"  ... indexed {len(indexed)}/{len(files)}")
    
    return indexed


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default=RAW_DIR)
    parser.add_argument("--output", default=OUTPUT_FILE)
    parser.add_argument("--max-files", type=int, default=None)
    args = parser.parse_args()
    
    os.makedirs(Path(args.output).parent, exist_ok=True)
    
    indexed = index_files(args.raw_dir, args.max_files)
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "source_dir": args.raw_dir,
            "file_count": len(indexed),
            "files": indexed,
        }, f, ensure_ascii=False, indent=2)
    
    total_size = sum(f["size"] for f in indexed)
    total_words = sum(f["word_count"] for f in indexed)
    print(f"[Index] Done: {len(indexed)} files, {total_size/1024/1024:.1f}MB, {total_words:,} words")
    print(f"[Index] Output: {args.output}")


if __name__ == "__main__":
    main()
