# LLM Wiki Builder — 技術選定の深掘り

> **Version:** 1.0.0-alpha  
> **Date:** 2026-05-22

---

## 1. デスクトップフレームワーク: Tauri vs Electron

### 選定結果: **Tauri (v2)**

| 観点 | Tauri | Electron | 判定 |
|---|---|---|---|
| **バイナリサイズ** | ~3MB | ~150MB | Tauri ✅ |
| **メモリ使用量** | ~50MB | ~200MB | Tauri ✅ |
| **セキュリティ** | Rust + OSウェブビュー、攻撃面が最小 | Chromium全機能含む、攻撃面大 | Tauri ✅ |
| **FSアクセス** | Rust Command経由で細かく制御可能 | Node.js fs モジュール直接 | Tauri ✅ |
| **開発速度** | Rust学習コストあり | JSのみで完結、チーム慣れている | Electron ✅ |
| **プラグイン生態系** | 成長中（足りないものは自作） | 非常に豊富 | Electron ✅ |
| **Apple Silicon対応** | ネイティブUniversal Binary | もちろん対応 | 同等 |

### 決め手

1. **ローカルファーストの信念と一致** — 軽量・高速・最小権限が思想に合う
2. **ファイルシステムの細かい制御** — Rust 側で raw/wiki フォルダの監視・読み書きを安全に実装
3. **SQLite ネイティブ統合** — Rust から `libsqlite3-sys` + `rusqlite` で直接アクセス、プロセス間通信不要
4. **Hermes環境との親和性** — ユーザーのメイン環境が WSL2/Linux、Rust toolchain は容易に導入可能

### Tauri v2 の新機能活用

- **Permission System**: `fs:allow-read` / `fs:allow-write` をスコープ制限（rawPath/wikiPath のみ）
- **Async Commands**: `async fn` でノンブロッキング LLM API 呼び出し
- **Channel**: Frontend ↔ Backend のストリーミング通信（統合進捗通知など）

---

## 2. フロントエンド: React + 状態管理

### UI フレームワーク: **React 19 + TypeScript + Tailwind CSS v4**

- **React 19**: Server Components は不要だが、`use()` や ref forwarding の改善でコードがシンプルに
- **Tailwind v4**: CSS-first 設定、ビルド高速化、ダークモームデフォルトに最適
- **TypeScript**: 厳格設定 (`strict: true`) で API 契約と型安全性を確保

### 状態管理: **Zustand + TanStack Query**

| 層 | 技術 | 役割 |
|---|---|---|
| **Server State** | TanStack Query v5 | SQLite/FS からの非同期データフェッチ・キャッシュ・再取得 |
| **Client State** | Zustand | UI 表示モード（Query Inbox vs Wiki Browser）、選択中プロジェクト |
| **Form State** | React Hook Form | 回答フォーム（選択式なので実質バリデーション不要だが一貫性のため） |

### なぜ Redux Toolkit ではないか

- グローバル状態が少ない（プロジェクト切り替え、テーマ、画面モードのみ）
- TanStack Query が Server State を隠蔽するため、大半の状態はローカルコンポーネントで完結
- ボイラープレート削減、TypeScript 推論が Zustand の方がシンプル

---

## 3. ローカルベクトル検索: sqlite-vec vs 代替案

### 選定結果: **sqlite-vec**

```
npm install sqlite-vec  # or Rust binding via sqlite_vec crate
```

| 候補 | 特徴 | 判定 |
|---|---|---|
| **sqlite-vec** | SQLite拡張として動作、同一DBに保存、移植性◎ | ✅ 採用 |
| **pgvector** | PostgreSQL必須。SQLiteローカルファースト思想と矛盾 | ❌ |
| **faiss** | Meta製、高速だが別プロセス/メモリ管理が複雑 | ❌ |
| **hnswlib** | C++、Rust binding ありだが永続化要実装 | ❌ |
| **Transformers.js** | ブラウザ内でembedding計算可能、モデルサイズ問題 | ⚠️ 将来検討 |

### sqlite-vec の使い方（設計）

```sql
-- クエリのベクトル表現を保存
CREATE VIRTUAL TABLE query_embeddings USING vec0(
  query_id INTEGER PRIMARY KEY,
  embedding FLOAT[384]  -- all-MiniLM-L6-v2 等の出力次元
);

-- 類似クエリ検索
SELECT query_id, distance
FROM query_embeddings
WHERE embedding MATCH ?
ORDER BY distance
LIMIT 5;
```

### Embedding モデルの選定

| モデル | 次元数 | 言語 | 選定理由 |
|---|---|---|---|
| **all-MiniLM-L6-v2** | 384 | 多言語 | onnxruntime-rs でローカル実行可能、速度◎ |
| **multilingual-e5-small** | 384 | 日本語強い | 日本語クエリ類似度に有利 |
| **OpenAI text-embedding-3-small** | 1536 | 多言語 | API経由、精度最高だがオフライン不可 |

**Phase 1**: OpenAI API 経由で動作させ、Phase 3 で onnxruntime + ローカルモデルに切り替え可能な抽象化層を設計する。

---

## 4. LLM API 抽象化層

### 設計方針: **OpenAI-compatible Client**

```typescript
// src-tauri/src/llm/client.rs (概念)
pub trait LlmClient: Send + Sync {
    async fn chat(&self, messages: Vec<Message>, config: GenerationConfig) -> Result<String>;
    async fn chat_stream(&self, messages: Vec<Message>) -> Result<ChannelStream>;
}

pub struct OpenAiCompatibleClient {
    endpoint: String,
    api_key: String,
    model: String,
    http_client: reqwest::Client,
}
```

### 対応プロバイダー

| プロバイダー | 用途 | 設定例 |
|---|---|---|
| **OpenRouter** | デフォルト推奨、モデル選択の幅 | `https://openrouter.ai/api/v1` |
| **OpenAI** | 高品質出力が必要な統合工程 | `https://api.openai.com/v1` |
| **Ollama** | 完全オフライン運用 | `http://localhost:11434/v1` |
| **LM Studio** | ローカル GUI 管理 | `http://localhost:1234/v1` |

### プロンプト管理: **テンプレートファイル化**

```
src-tauri/src/llm/prompts/
├── query_generation.txt     # クエリ生成用
├── integration.txt          # Wiki統合用
├── summarize_raw.txt        # raw要約用（将来）
└── system/
    └── knowledge_curator.txt # 知識策展者ペルソナ
```

Rust 側で `include_str!()` でコンパイル時埋め込み、環境変数/設定で変数部分を置換。

---

## 5. ファイル監視戦略

### Rust 側実装: **notify crate**

```toml
[dependencies]
notify = "6"
tokio = { version = "1", features = ["full"] }
```

### 設計ポイント

| 項目 | 方針 |
|---|---|
| **監視対象** | `{rawPath}/**/*.md`, `{rawPath}/**/*.txt`（設定で拡張子指定可） |
| **デバウンス** | 500ms デバウンスで連続変更を1イベントに集約 |
| **差分検出** | ファイルハッシュ (xxhash) で前回と比較、実質変更があればインデックス更新 |
| **リアルタイム反映** | 変更検出 → SQLite index 更新 → Frontend に Tauri Event で通知 |
| **手動再インデックス** | プロジェクト設定画面で「今すぐインデックス再構築」ボタン |

---

## 6. ビルド・配布

### パッケージング: **Tauri Bundler**

```bash
# 開発
cd src-tauri && cargo tauri dev

# ビルド（各プラットフォーム）
cargo tauri build --target x86_64-unknown-linux-gnu
cargo tauri build --target x86_64-pc-windows-msvc
cargo tauri build --target x86_64-apple-darwin
cargo tauri build --target aarch64-apple-darwin
```

### 自動更新 (Optional Phase 3)

- **Tauri Updater** + GitHub Releases / 独自更新サーバー
- 差分更新対応、ロールバック機能

---

## 7. 技術選定サマリー

| 層 | 技術 | バージョン | 役割 |
|---|---|---|---|
| **Desktop Shell** | Tauri | v2 | 軽量ネイティブアプリ、FSアクセス制御 |
| **Frontend** | React + TypeScript | 19 / 5.6 | UI層、コンポーネント構築 |
| **Styling** | Tailwind CSS | v4 | ユーティリティファーストCSS |
| **Server State** | TanStack Query | v5 | 非同期データフェッチ・キャッシュ |
| **Client State** | Zustand | v5 | グローバルUI状態 |
| **Backend** | Rust | 1.80+ | Tauri Commands、FS/DB/LLM制御 |
| **Database** | SQLite | 3.40+ | ローカル永続化、零構成 |
| **Vector Search** | sqlite-vec | latest | クエリ重複検出、類似度判定 |
| **Embedding** | OpenAI API (Phase 1) → onnxruntime-rs (Phase 3) | - | テキスト埋め込み |
| **File Watch** | notify (Rust) | v6 | rawフォルダ監視 |
| **LLM Client** | reqwest + 独自抽象層 | - | OpenAI-compatible API通信 |
| **Markdown** | markdown-it / marked | - | Wikiプレビュー描画 |
| **Diff View** | diff-match-patch + 独自UI | - | Wiki統合差分表示 |

---

## 8. 未決定・検討事項

1. **Markdown エディタ**: 軽量な `contenteditable` ベース自前実装 vs CodeMirror / Monaco Editor
2. **アイコン**: Lucide React（軽量・Tree-shakable）が最有力
3. **テスト戦略**: Rust 側は `cargo test`、React 側は Vitest + React Testing Library
4. **国際化 (i18n)**: Phase 1 は日本語固定、Phase 2 で `i18next` 導入検討
5. **パフォーマンス計測**: Tauri の WebView DevTools + Rust profiling (`cargo flamegraph`)
