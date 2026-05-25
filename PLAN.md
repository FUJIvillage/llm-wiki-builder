# LLM Wiki Builder — Phase 1 実装計画

> **Version:** 1.0.0-alpha  
> **Date:** 2026-05-22  
> **Scope:** MVP Core Loop (Project Setup → Query Generation → Answer → Persist)

---

## ゴール

Phase 1 の終了時点で、以下が動作するデスクトップアプリを完成させる：

1. **プロジェクト作成** — 名前、rawPath、wikiPath、LLM設定を登録
2. **初回インデックス** — rawフォルダのMarkdownファイルを読み込み、SQLiteにインデックス
3. **クエリ生成** — LLM APIを呼び出し、未カバー領域の問いを生成
4. **Query Inbox** — 優先度順に未回答クエリを一覧表示
5. **選択式回答** — Yes/No、複数選択、スケールで回答しSQLiteに保存

---

## 前提条件

- Rust toolchain (cargo, rustc) インストール済み
- Node.js v22+ インストール済み
- Tauri CLI (`cargo install tauri-cli`) インストール済み
- OpenRouter API Key（または他のOpenAI-compatible key）を所持

---

## ディレクトリ構造

```
llm-wiki-builder/
├── README.md
├── REQUIREMENTS.md
├── TECH_DECISIONS.md
├── PLAN.md
├── architecture.html
├── src/                          # React Frontend
│   ├── main.tsx
│   ├── App.tsx
│   ├── components/
│   │   ├── Sidebar.tsx           # プロジェクトリスト + 新規作成
│   │   ├── ProjectForm.tsx       # プロジェクト設定フォーム
│   │   ├── QueryInbox.tsx        # クエリ一覧 + 回答UI
│   │   ├── QueryCard.tsx         # 単一クエリ表示（選択肢付き）
│   │   └── WikiBrowser.tsx       # Phase 1ではread-onlyプレビュー
│   ├── hooks/
│   │   ├── useProjects.ts        # TanStack Query wrapper
│   │   ├── useQueries.ts         # クエリ一覧・回答submit
│   │   └── useTauriCommand.ts    # invoke wrapper with types
│   ├── stores/
│   │   └── appStore.ts           # Zustand（選択中プロジェクト等）
│   ├── types/
│   │   └── index.ts              # Project, Query, Answer, Choice types
│   └── styles/
│       └── index.css             # Tailwind directives
├── src-tauri/                    # Rust Backend
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   ├── src/
│   │   ├── main.rs               # entrypoint + command registration
│   │   ├── commands/
│   │   │   ├── project.rs        # project CRUD commands
│   │   │   ├── query.rs          # query fetch / answer submit
│   │   │   └── generation.rs     # LLM query generation trigger
│   │   ├── models/
│   │   │   ├── project.rs        # Project struct + validation
│   │   │   ├── query.rs          # Query struct + QueryType enum
│   │   │   └── answer.rs         # Answer struct
│   │   ├── db/
│   │   │   ├── mod.rs            # SQLite connection pool init
│   │   │   ├── schema.rs         # table definitions + migrations
│   │   │   └── repo.rs           # CRUD operations (projects, queries, answers)
│   │   ├── llm/
│   │   │   ├── mod.rs            # LlmClient trait + init
│   │   │   ├── client.rs         # OpenAiCompatibleClient impl
│   │   │   ├── prompts.rs        # include_str!(query_generation.txt)
│   │   │   └── prompts/
│   │   │       └── query_generation.txt
│   │   ├── indexer/
│   │   │   ├── mod.rs
│   │   │   └── raw_indexer.rs    # rawフォルダ走査 + 内容読み込み
│   │   └── fs_watcher.rs         # (Phase 1では手動トリガーのみ、WatcherはStub)
│   └── capabilities/
│       └── default.json          # fs:allow-read scoped to project paths
├── .hermes/plans/                # Hermes Plan Mode 互換
│   └── 2026-05-22_llm-wiki-builder-phase1.md
└── docs/
    └── api_spec.md               # Frontend-Rust Command API 型定義
```

---

## タスク分解（実装順）

### Week 1: 土台構築 + データ層

#### Task 1: Tauri v2 プロジェクト初期化
- [ ] `cargo create-tauri-app --beta` 実行（template: react-ts）
- [ ] `Cargo.toml` 依存整備：`rusqlite`, `serde`, `tokio`, `reqwest`, `anyhow`, `thiserror`
- [ ] `tauri.conf.json` permission 設定：`fs:allow-read` を `{rawPath}` / `{wikiPath}` にスコープ制限
- [ ] Frontend 依存：`tailwindcss`, `@tanstack/react-query`, `zustand`, `lucide-react`

#### Task 2: SQLite スキーマ設計 + マイグレーション
- [ ] `db/schema.rs` にテーブル定義を実装
  - `projects` テーブル
  - `queries` テーブル（JSON型で `choices` を保存）
  - `answers` テーブル
- [ ] アプリ起動時にマイグレーション自動実行
- [ ] DBファイルパス：`~/.local/share/llm-wiki-builder/db.sqlite`

#### Task 3: Project CRUD (Rust Commands)
- [ ] `commands/project.rs`: `create_project`, `list_projects`, `get_project`, `delete_project`
- [ ] 入力検証：rawPath/wikiPath が存在すること、name の重複チェック
- [ ] API Key は OS keyring (`keyring` crate) に保存し、DBには暗号化しないが参照IDのみ保持

#### Task 4: Project UI (React)
- [ ] `Sidebar.tsx`: プロジェクト一覧 + 新規作成ボタン
- [ ] `ProjectForm.tsx`: 設定フォーム（名前、パス、LLMエンドポイント、モデル、API Key）
- [ ] Zustand で `selectedProjectId` を管理
- [ ] TanStack Query でプロジェクト一覧をキャッシュ

### Week 2: インデックス + クエリ生成

#### Task 5: Raw Indexer (Rust)
- [ ] `indexer/raw_indexer.rs`: rawPath を再帰走査、`.md` / `.txt` を読み込み
- [ ] ファイル内容を `raw_documents` テーブル（またはメモリ）に保存
- [ ] Phase 1 では全文はDBに保存、将来はベクトル化
- [ ] コマンド：`index_raw_files(project_id)`

#### Task 6: LLM Client 実装
- [ ] `llm/client.rs`: `reqwest` ベースの OpenAI-compatible クライアント
- [ ] 構造化出力 (`response_format: { type: "json_object" }`) を使用
- [ ] エラーハンドリング：タイムアウト、レート制限、無効なAPI Key
- [ ] コマンド：`generate_queries(project_id)` → `Vec<Query>`

#### Task 7: クエリ生成プロンプト設計
- [ ] `llm/prompts/query_generation.txt` を作成
- [ ] 入力：rawファイル内容の要約（トークン制限に合わせて先頭Nファイル）
- [ ] 出力JSONスキーマ定義：`question`, `choices[]`, `queryType`, `priorityScore`, `context`
- [ ] スパイク：3つの異なるプロジェクトでプロンプト精度を検証

### Week 3: Query Inbox + 回答フロー

#### Task 8: Query Inbox UI
- [ ] `QueryInbox.tsx`: 未回答クエリ一覧（優先度降順）
- [ ] `QueryCard.tsx`:
  - Yes/No: 左右ボタン
  - 複数選択: 横並びラジオ/チェックボタン
  - スケール: 1-5 セグメントボタン
  - スキップボタン（理由選択プルダウン）
- [ ] キーボードショートカット：1~5, Y/N, S（スキップ）

#### Task 9: 回答保存 (Rust Commands)
- [ ] `commands/query.rs`: `submit_answer(query_id, selected_choices, free_text?)`
- [ ] `skip_query(query_id, reason)`
- [ ] 回答後、次の未回答クエリを自動表示

#### Task 10: 動作確認 + スパイク検証
- [ ] 実際のrawフォルダ（OpenClawのraw等）を使ってE2Eテスト
- [ ] クエリ品質チェック：単純な事実確認になっていないか、選択肢は適切か
- [ ] 優先度スコアの妥当性：実際に重要な問いが上位に来るか

---

## スパイク計画（並行検証）

### Spike A: プロンプト精度検証（Task 7と並行）

```bash
# スパイク用ディレクトリ
mkdir -p ~/projects/llm-wiki-builder/spikes/prompt-quality
```

- 目的：クエリ生成プロンプトが「構造化に役立つ問い」を生成できるか検証
- 方法：3つの異なるテーマのrawセット（技術ブログ、プロジェクトメモ、論文抄訳）を用意し、それぞれでプロンプトを実行
- 評価基準：
  1. 生成されたクエリ数（10個以上を目標）
  2. 選択肢付きクエリの比率（80%以上）
  3. 重複・類似クエリの比率（20%以下）
  4. 実際に回答するとWikiに役立ちそうか（主観評価5段階）

### Spike B: sqlite-vec ベクトル検索（並行検証、Phase 1では未統合）

```bash
mkdir -p ~/projects/llm-wiki-builder/spikes/vector-search
```

- 目的：sqlite-vec + embedding でクエリ重複検出が実用的か検証
- 方法：既存の問い10個を手動で作成し、類似クエリを投入して重複排除の精度を測定
- 評価基準：
  - 全く異なるテーマのクエリは誤検出されないか
  - 似たテーマの異なる問いは区別されるか
  - 同一テーマの重複クエリは検出されるか

### Spike C: Tauri v2 Permission + FS Scope（Task 1の検証）

```bash
mkdir -p ~/projects/llm-wiki-builder/spikes/tauri-fs-scope
```

- 目的：Tauri v2 の `fs:allow-read` スコープ制限がプロジェクトパスに動的に適用できるか
- 方法：最小限のTauriアプリで、ユーザー選択ディレクトリ以下のみ読み取れることを確認
- 評価基準：スコープ外パスへのアクセスが ` forbidden` となること

---

## リスクと対策

| リスク | 影響 | 対策 |
|---|---|---|
| LLM API 応答が遅い/失敗する | クエリ生成が使いものにならない | タイムアウト設定（30s）、リトライ3回、フォールバックでダミークエリ生成 |
| rawファイルが多すぎてコンテキスト超過 | クエリ生成精度低下 | ファイルを要約してから送信、最大トークン数で打ち切り |
| Tauri v2 のbreaking change | ビルド失敗 | 公式betaドキュメントを追従、lockファイルでバージョン固定 |
| ユーザー環境にRustがない | ビルド不可 | Phase 1 では開発者向け、Phase 2/3 でバイナリ配布 |
| 選択式回答が網羅的でない | 回答が不十分 | 「その他」+ フリーテキストを常に付与、Spike Aで改善 |

---

## 完了定義（Definition of Done）

- [ ] `cargo tauri dev` でアプリが起動する
- [ ] プロジェクトを作成し、rawPath/wikiPath/LLM設定が保存できる
- [ ] rawフォルダのファイルがインデックスされる
- [ ] 「クエリ生成」ボタンでLLM APIが呼ばれ、SQLiteにクエリが保存される
- [ ] Query Inbox に未回答クエリが優先度順で表示される
- [ ] 選択式UIで回答でき、回答がSQLiteに保存される
- [ ] スパイク A/B/C の結果が `spikes/` に記録されている
- [ ] README.md にビルド手順と動作確認手順が記載されている

---

## 次フェーズへの接続

Phase 2 では以下を追加する：

1. **Integration Engine** — 回答ストックからWiki差分を生成
2. **Wiki Browser** — Markdownエディタ + DiffレビューUI
3. **File Watcher** — rawフォルダの自動監視
4. **Git連携** — wikiフォルダの自動コミット

Phase 1 のデータモデルは Phase 2 で拡張されるが、破壊的変更は避ける設計とする。
