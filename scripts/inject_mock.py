#!/usr/bin/env python3
"""Inject generated queries into frontend Mock API."""

import json
import re
from pathlib import Path

QUERIES_FILE = "data/generated_queries.json"
API_FILE = "src/lib/api.ts"


def inject_into_api():
    with open(QUERIES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    queries = data.get("queries", [])
    if not queries:
        print("[Inject] No queries to inject")
        return
    
    # Read current api.ts
    api_path = Path(API_FILE)
    content = api_path.read_text(encoding="utf-8")
    
    # Find MOCK_QUERIES array and replace it
    # Pattern: const MOCK_QUERIES: Query[] = [...];
    start_marker = "const MOCK_QUERIES: Query[] = ["
    end_marker = "];\n\nlet mockQueries"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("[Inject] Could not find MOCK_QUERIES array in api.ts")
        return
    
    # Build new mock queries string
    query_lines = []
    for q in queries:
        lines = json.dumps(q, ensure_ascii=False, indent=2)
        # Indent to match file style
        lines = "  " + lines.replace("\n", "\n  ")
        query_lines.append(lines)
    
    new_array = start_marker + "\n" + ",\n\n".join(query_lines) + "\n];"
    
    new_content = content[:start_idx] + new_array + content[end_idx + len(end_marker) - 2:]
    
    # Also update the pending count in MOCK_PROJECTS
    pending_count = len([q for q in queries if q.get("status") == "pending"])
    new_content = re.sub(
        r"(pending_query_count:)\s*\d+",
        f"\1 {pending_count}",
        new_content,
    )
    
    api_path.write_text(new_content, encoding="utf-8")
    print(f"[Inject] Injected {len(queries)} queries into {API_FILE}")
    print(f"[Inject] Updated pending count to {pending_count}")


def main():
    inject_into_api()


if __name__ == "__main__":
    main()
