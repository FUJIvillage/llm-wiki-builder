#!/usr/bin/env python3
"""Batch query generation: process multiple files per LLM call."""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

ROBLOX_AGENT = str(Path.home() / "projects" / "roblox-auto-merchant" / "agent" / "src")
if ROBLOX_AGENT not in sys.path:
    sys.path.insert(0, ROBLOX_AGENT)

from opencode_go_client import chat_completion

INDEX_FILE = os.environ.get("INDEX_FILE", "data/file_index.json")
OUTPUT_FILE = os.environ.get("QUERIES_OUTPUT", "data/generated_queries.json")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "5"))

BATCH_PROMPT_TEMPLATE = """あなたはWiki構築のためのクエリ生成アシスタントです。

以下は{file_count}個の活動記録ファイルです。各ファイルの内容を分析し、知識を体系化するために必要なYes/Noまたは選択式のクエリを生成してください。

【ファイル一覧】
{files_summary}

【出力形式】
以下のJSON配列形式で、各ファイルあたり1〜2個のクエリを合計で出力してください:

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
    "raw_file_refs": ["元ファイル名.md"]
  }}
]

ルール:
- 各ファイルから重要な判断・決定・設定・問題を問う
- priority_score: ファイルの重要性に応じて0.5〜0.95
- ファイル名はraw_file_refsに正確に記載すること
"""


def generate_batch(files_batch: list, batch_num: int, total_batches: int) -> list:
    """Generate queries for a batch of files."""
    # Build summary
    summaries = []
    for f in files_batch:
        summaries.append(f"【{f['filename']}】({f['date']}, {f['word_count']} words)\n{f['content'][:1200]}")
    
    prompt = BATCH_PROMPT_TEMPLATE.format(
        file_count=len(files_batch),
        files_summary="\n\n---\n\n".join(summaries),
    )
    
    try:
        response = chat_completion(
            messages=[
                {"role": "system", "content": "You are a query generation assistant. Output valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=4000,
        )
        
        text = response.strip()
        if "```" in text:
            parts = text.split("```")
            text = parts[1] if len(parts) > 1 else text
            text = text.replace("json", "").strip()
        
        queries = json.loads(text)
        if not isinstance(queries, list):
            queries = [queries]
        
        # Add metadata
        for i, q in enumerate(queries):
            q["id"] = f"q-batch{batch_num}-{i:02d}-{hash(q.get('question', '')) % 10000:04d}"
            q["project_id"] = "proj-openclaw-001"
            q["status"] = "pending"
            q["llm_generated"] = True
            q["created_at"] = datetime.now().isoformat()
            q["updated_at"] = datetime.now().isoformat()
        
        return queries
    except Exception as e:
        print(f"  [Error] Batch {batch_num}/{total_batches}: {e}")
        return []


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default=INDEX_FILE)
    parser.add_argument("--output", default=OUTPUT_FILE)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    args = parser.parse_args()
    
    with open(args.index, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    files = data["files"]
    total_batches = (len(files) + args.batch_size - 1) // args.batch_size
    
    print(f"[BatchGenerate] {len(files)} files, {args.batch_size} per batch = {total_batches} API calls")
    
    all_queries = []
    for batch_num in range(total_batches):
        start = batch_num * args.batch_size
        end = start + args.batch_size
        batch = files[start:end]
        
        print(f"  Batch {batch_num + 1}/{total_batches} ({len(batch)} files)...", end=" ", flush=True)
        queries = generate_batch(batch, batch_num, total_batches)
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
    
    print(f"[BatchGenerate] Done: {len(all_queries)} queries from {len(files)} files")
    print(f"[BatchGenerate] Output: {args.output}")


if __name__ == "__main__":
    main()
