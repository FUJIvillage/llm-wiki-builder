#!/usr/bin/env python3
"""Generate queries from indexed files using OpenCode Go API (Hermes's own API)."""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add roblox-auto-merchant agent src to path for opencode_go_client
ROBLOX_AGENT = str(Path.home() / "projects" / "roblox-auto-merchant" / "agent" / "src")
if ROBLOX_AGENT not in sys.path:
    sys.path.insert(0, ROBLOX_AGENT)

try:
    from opencode_go_client import chat_completion
except ImportError:
    print("[Error] opencode_go_client not found. Ensure roblox-auto-merchant/agent/src exists.")
    sys.exit(1)

INDEX_FILE = os.environ.get("INDEX_FILE", "data/file_index.json")
OUTPUT_FILE = os.environ.get("QUERIES_OUTPUT", "data/generated_queries.json")

PROMPT_TEMPLATE = """あなたはWiki構築のためのクエリ生成アシスタントです。

以下はOpenClawエージェントの活動記録ファイルです。このファイルの内容を分析し、知識を体系化するために必要なYes/Noまたは選択式のクエリを生成してください。

【ファイル情報】
- ファイル名: {filename}
- 日付: {date}
- 内容:
{content}

【出力形式】
以下のJSON配列形式で1〜3個のクエリを出力してください:

[
  {{
    "question": "クエリの質問文（日本語）",
    "context": "このクエリが選ばれた理由や背景（2-3文）",
    "query_type": "yes_no または single_select または multi_select",
    "choices": [
      {{"id": "c1", "label": "選択肢1", "description": "説明（任意）"}},
      {{"id": "c2", "label": "選択肢2", "description": "説明（任意）"}}
    ],
    "priority_score": 0.0〜1.0,
    "raw_file_refs": ["{filename}"]
  }}
]

ルール:
- yes_no: 2つの選択肢（Yes/No）
- single_select: 3〜4つの選択肢（単一回答）
- multi_select: 3〜5つの選択肢（複数回答可）
- priority_score: ファイルの重要性に応じて0.5〜0.95
- ファイルの内容に基づいた具体的な質問にすること
- ファイルに含まれる判断・決定・設定・問題を問う形にすること
"""


def generate_for_file(file_entry: dict) -> list:
    """Generate queries for a single file using LLM."""
    prompt = PROMPT_TEMPLATE.format(
        filename=file_entry["filename"],
        date=file_entry["date"],
        content=file_entry["content"][:2500],  # Limit content length
    )
    
    try:
        response = chat_completion(
            messages=[
                {"role": "system", "content": "You are a query generation assistant for knowledge base curation. Output valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        
        # Parse JSON from response
        text = response.strip()
        # Remove markdown code blocks if present
        if "```" in text:
            text = text.split("```")[1] if "```json" in text else text.split("```")[0]
            text = text.replace("json", "").strip()
        
        queries = json.loads(text)
        if not isinstance(queries, list):
            queries = [queries]
        
        # Add metadata
        for i, q in enumerate(queries):
            q["id"] = f"q-{file_entry['date']}-{i:02d}-{hash(file_entry['filename'] + str(i)) % 10000:04d}"
            q["project_id"] = "proj-openclaw-001"
            q["status"] = "pending"
            q["llm_generated"] = True
            q["created_at"] = datetime.now().isoformat()
            q["updated_at"] = datetime.now().isoformat()
        
        return queries
    except Exception as e:
        print(f"  [Error] {file_entry['filename']}: {e}")
        return []


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default=INDEX_FILE)
    parser.add_argument("--output", default=OUTPUT_FILE)
    parser.add_argument("--max-files", type=int, default=5, help="Max files to process (for testing)")
    args = parser.parse_args()
    
    with open(args.index, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    files = data["files"]
    if args.max_files:
        files = files[:args.max_files]
    
    print(f"[Generate] Processing {len(files)} files...")
    
    all_queries = []
    for i, file_entry in enumerate(files, 1):
        print(f"  [{i}/{len(files)}] {file_entry['filename']}...", end=" ")
        queries = generate_for_file(file_entry)
        all_queries.extend(queries)
        print(f"{len(queries)} queries")
    
    os.makedirs(Path(args.output).parent, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "file_count": len(files),
            "query_count": len(all_queries),
            "queries": all_queries,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"[Generate] Done: {len(all_queries)} queries from {len(files)} files")
    print(f"[Generate] Output: {args.output}")


if __name__ == "__main__":
    main()
