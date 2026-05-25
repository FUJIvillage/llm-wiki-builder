#!/usr/bin/env python3
"""Idempotent demo data seeder for LLM Wiki Builder backend.

Usage:
    cd backend && . .venv/bin/activate && python scripts/seed.py
"""
import json
import os
import sys
from pathlib import Path

# Add parent dir to path so imports work regardless of cwd
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from app.database import engine
from app.models import SQLModel, Project, Query, Answer
from sqlmodel import Session, select


def seed() -> None:
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # --- Project (idempotent: upsert by name) ---
        project_name = "OpenClaw Archive"
        stmt = select(Project).where(Project.name == project_name)
        existing = session.exec(stmt).first()
        if existing:
            project = existing
            print(f"Project '{project_name}' already exists (id={project.id})")
        else:
            raw_path = os.environ.get("SEED_RAW_PATH", "")
            project = Project(
                name=project_name,
                raw_path=raw_path if raw_path else None,
            )
            session.add(project)
            session.commit()
            session.refresh(project)
            print(f"Created project '{project_name}' (id={project.id})")

        # --- Queries & Answers ---
        queries_data = [
            {
                "question": "NPU LLM App は現在の主要プロジェクトですか？",
                "context": "2026-04-04.md に「NPU LLM App プロジェクト」として記録あり。他プロジェクトとの優先順位を確認したい。",
                "type": "yes_no",
                "choices": [
                    {"id": "c1", "label": "Yes", "description": "最優先または主要プロジェクト"},
                    {"id": "c2", "label": "No", "description": "優先順位は低い／アーカイブ済み"},
                ],
                "score": 0.92,
                "answer": ["c1"],
            },
            {
                "question": "edge-tts-test の結果、どの音声合成エンジンを採用しましたか？",
                "context": "2026-04-05-edge-tts-test.md に複数のTTS検証記録あり。最終的な採用方針を統一したい。",
                "type": "single_select",
                "choices": [
                    {"id": "c1", "label": "Edge TTS (Microsoft)"},
                    {"id": "c2", "label": "OpenAI TTS"},
                    {"id": "c3", "label": "ElevenLabs"},
                    {"id": "c4", "label": "未確定／継続評価中"},
                ],
                "score": 0.78,
                "answer": ["c2"],
            },
            {
                "question": "cron-setup の記録はどのカテゴリに分類しますか？",
                "context": "自動化基盤の整備記録。wiki構成のカテゴリ分類に影響。",
                "type": "single_select",
                "choices": [
                    {"id": "c1", "label": "インフラ運用"},
                    {"id": "c2", "label": "プロジェクト設定"},
                    {"id": "c3", "label": "ツール検証"},
                    {"id": "c4", "label": "セッション記録"},
                ],
                "score": 0.65,
                "answer": ["c1"],
            },
            {
                "question": "Memory Log の記録頻度と目的を選んでください",
                "context": "2026-04-06.md はMemory Log形式。複数のセッションが混在している。",
                "type": "multi_select",
                "choices": [
                    {"id": "c1", "label": "毎日定例記録"},
                    {"id": "c2", "label": "週次サマリー"},
                    {"id": "c3", "label": "障害・トラブル記録"},
                    {"id": "c4", "label": "ツール設定変更ログ"},
                ],
                "score": 0.71,
                "answer": ["c1", "c4"],
            },
            {
                "question": "GitHub CLI認証の問題は解決済みですか？",
                "context": "2026-04-06.md に「ブラウザ認証タイムアウト」と記録あり。現在の状態を確認。",
                "type": "yes_no",
                "choices": [
                    {"id": "c1", "label": "Yes", "description": "認証成功、正常に動作中"},
                    {"id": "c2", "label": "No", "description": "未解決／別の認証方式を使用"},
                ],
                "score": 0.85,
                "answer": ["c1"],
            },
            {
                "question": "OpenRouterの無料版モデル（qwen/qwen3.6-plus-preview:free）を、機密性の高いコードやプロンプトを含む開発作業で継続して使用すべきか？",
                "context": "ファイルには「無料で使用可能（条件：プロンプト/レスポンスが学習に使用）」と明記されており、NPU LLM Appの開発や自律開発サイクルで実際に使用されている。プライバシーとセキュリティのトレードオフが存在する。",
                "type": "yes_no",
                "choices": [
                    {"id": "c1", "label": "Yes", "description": "コスト優先で学習利用条件を受け入れ、継続使用する"},
                    {"id": "c2", "label": "No", "description": "機密情報流出リスクを避け、有料版または別プロバイダーに移行する"},
                ],
                "score": 0.9,
                "answer": ["c2"],
            },
            {
                "question": "サブエージェントspawn時の「pairing required」エラーに対して、「メインセッションで直接実行」という回避策を、今後も恒久的な運用方針として維持すべきか？",
                "context": "ファイルの「未解決の問題」セクションに記載されており、サブエージェント機能は使用できずメインセッションでの直接実行が現在の回避策となっている。並列処理やサブタスク分割の制約が生じる可能性がある。",
                "type": "yes_no",
                "choices": [
                    {"id": "c1", "label": "Yes", "description": "現状の回避策を維持し、メインセッション集中運用とする"},
                    {"id": "c2", "label": "No", "description": "pairing requiredエラーの根本原因解決を優先し、サブエージェント機能の復旧を目指す"},
                ],
                "score": 0.85,
                "answer": ["c2"],
            },
            {
                "question": "Andrej KarpathyのautoresearchパターンをOpenClawの自律開発サイクルに導入する場合、現時点で最も不足している前提条件はどれか？",
                "context": "ファイルではautoresearchの3要素（明確な指標、自動評価、高速イテレーション）が紹介されている。現在のNPU LLM App開発ではCI/CDとテストコードが整備されつつあるが、autoresearch特有の「自動スコア測定→commit/reset」ループは未構築である。",
                "type": "single_select",
                "choices": [
                    {"id": "c1", "label": "自動評価パイプライン", "description": "実験結果を自動判定し、改善/悪化を機械的に判断する仕組み（prepare.py相当）"},
                    {"id": "c2", "label": "エージェント編集制約ルール", "description": "エージェントが編集可能なファイルを限定する明確なガバナンス（train.pyのみ編集可など）"},
                    {"id": "c3", "label": "明確な数値指標の定義", "description": "「良い」ではなく数値化された評価指標（推論速度、精度、APKサイズなど）"},
                    {"id": "c4", "label": "高速イテレーション環境", "description": "1サイクルを数分以内に完了させる計算リソースと軽量タスク設計"},
                ],
                "score": 0.8,
                "answer": ["c1"],
            },
        ]

        created_count = 0
        skipped_count = 0

        for qd in queries_data:
            # Idempotent: skip if question already exists for this project
            stmt_q = select(Query).where(
                Query.project_id == project.id,
                Query.question == qd["question"],
            )
            if session.exec(stmt_q).first():
                skipped_count += 1
                continue

            query = Query(
                project_id=project.id,
                question=qd["question"],
                context=qd["context"],
                query_type=qd["type"],
                choices_json=json.dumps(qd["choices"]),
                priority_score=qd["score"],
                status="answered",
                llm_generated=True,
                raw_file_refs_json=json.dumps(["demo.md"]),
            )
            session.add(query)
            session.commit()
            session.refresh(query)

            answer = Answer(
                query_id=query.id,
                selected_choice_ids_json=json.dumps(qd["answer"]),
            )
            session.add(answer)
            created_count += 1

        session.commit()
        # Count current answers for this project
        answer_count = session.exec(
            select(Answer).join(Query).where(Query.project_id == project.id)
        ).all()
        print(f"Done: {created_count} queries created, {skipped_count} skipped")
        print(f"Project '{project_name}' now has {len(answer_count)} answers")


if __name__ == "__main__":
    seed()
