# LLM Wiki Builder — 要件定義書

> **Version:** 1.0.0-alpha  
> **Date:** 2026-05-22  
> **Philosophy:** Karpathy's LLM Wiki ("Read → Write → Ask → Integrate")

---

## 1. プロダクト概要

**LLM Wiki Builder** は、ユーザーがプロジェクト単位で未加工の知識断片（raw）を構造化されたWikiに昇華させることを支援する、**ローカルファースト**のデスクトップアプリである。

KarpathyのLLM Wiki思想に則り、以下の循環を自動化・半自動化する：

1. **Read（収集）** — rawフォルダから資料を取り込む
2. **Ask（問う）** — LLMが重要な問い（クエリ）を生成する
3. **Write（書く）** — ユーザーが選択式インターフェースで最小摩擦で回答する
4. **Integrate（統合）** — 回答ストックをLLMが定期的にWiki Markdownに統合する

---

## 2. 思想との対応関係

| Karpathyの段階 | アプリにおける実装 | 自動化レベル |
|---|---|---|
| **Read** | rawフォルダの取り込み・監視 | 自動 |
| **Ask** | LLMによるクエリ生成・優先度付け | 自動（LLM駆動） |
| **Write** | 選択式回答UI | ユーザー操作（最小摩擦） |
| **Integrate** | 回答ストックの定期Wiki統合 | 半自動（承認制） |

---

## 3. ユーザーフロー

### 3.1 初期セットアップフロー
```
[アプリ起動]
  → [プロジェクト作成/選択]
    → [rawフォルダパスを設定]（既存Wikiフォルダがあればリンク）
      → [LLM API設定]（OpenRouter/OpenAI/Local）
        → [初回インデックス作成]
          → [LLMが初回クエリセットを生成]
```

### 3.2 デイリーフロー（メインフロー）
```
[アプリを開く]
  → [優先度順に未回答クエリを表示]
    → [ユーザーが選択式で回答]
      → [次のクエリへ]
        → [終了]
          → [回答は自動保存・ストック]
```

### 3.3 統合フロー（バックグラウンド）
```
[回答がN件ストックされる or 一定時間経過]
  → [統合バッチが起動]
    → [LLMが回答ストックを解析]
      → [Wikiページの差分を生成]
        → [ユーザー承認（または自動承認設定）]
          → [Wikiファイルに書き出し]
            → [生成済みクエリをアーカイブ]
```

---

## 4. 機能要件

### 4.1 プロジェクト管理（Project Workspace）

| ID | 要件 | 優先度 | 備考 |
|---|---|---|---|
| P-01 | プロジェクトのCRUD | Must | 名前、rawPath、wikiPath、LLM設定 |
| P-02 | rawフォルダの取り込み | Must | `.md`, `.txt`, `.json`, 画像（OCR経由）対象 |
| P-03 | 既存wikiフォルダのリンク | Must | 既存Markdownファイル群を尊重 |
| P-04 | ファイル監視（Watch） | Should | raw追加・変更を検知し差分インデックス更新 |
| P-05 | プロジェクト切り替え | Must | サイドバーからワンクリック切り替え |

### 4.2 クエリ生成エンジン（Query Engine）

| ID | 要件 | 優先度 | 備考 |
|---|---|---|---|
| Q-01 | LLMによるクエリ生成 | Must | プロジェクト全体（raw + wiki）をコンテキストに入力 |
| Q-02 | 重要度スコアリング | Must | カバレッジGap、矛盾検出、新近性、深さの4軸 |
| Q-03 | 選択肢付きクエリ生成 | Must | Yes/No、複数選択、スケール（1-5）、固有値選択 |
| Q-04 | 重複・類似クエリ排除 | Must | ベクトル埋め込みで類似度判定 |
| Q-05 | クエリの手動作成 | Should | ユーザーが自らクエリを追加可能 |
| Q-06 | クエリ生成トリガー | Must | 初回セットアップ時、手動、ファイル監視時 |

**重要度スコアリングの4軸：**
- **Coverage Gap:** 重要テーマに未回答クエリが多いほど高得点
- **Contradiction:** raw間・wiki間で矛盾・曖昧さを検出
- **Recency:** 新しく追加されたrawに関連するクエリを優先
- **Depth:** 表層的ではなく、構造的・本質的な問いを優先

### 4.3 クエリ回答UI（Query Inbox）

| ID | 要件 | 優先度 | 備考 |
|---|---|---|---|
| U-01 | 優先度順リスト表示 | Must | スコア降順、未回答のみデフォルト表示 |
| U-02 | 選択式回答インターフェース | Must | タップ/クリックのみで回答完了 |
| U-03 | 回答タイプ | Must | ①Yes/No ②複数選択（ラジオ/チェック） ③スケール ④固有値リスト |
| U-04 | テキスト入力最小化 | Must | 「その他」や補足のみフリーテキスト可 |
| U-05 | スキップ機能 | Must | 後で回答可能、スキップ理由を軽く記録 |
| U-06 | クエリの折りたたみ/展開 | Should | 長い文脈表示を制御 |
| U-07 | キーボードショートカット | Should | 1~9で選択、Enterで確定、Sでスキップ |

### 4.4 ストック・統合エンジン（Integration Engine）

| ID | 要件 | 優先度 | 備考 |
|---|---|---|---|
| I-01 | 回答の永続化 | Must | SQLiteローカルDBに保存 |
| I-02 | 統合バッチ処理 | Must | 手動実行 + 自動（設定可能な間隔） |
| I-03 | LLM統合プロンプト | Must | 回答ストックを踏まえたWiki差分生成 |
| I-04 | 差分レビューUI | Must | Git Diff風のBefore/After表示 |
| I-05 | 承認制適用 | Must | デフォルトは承認制、設定で自動適用可 |
| I-06 | 統合履歴 | Should | 過去の統合バッチとその差分を閲覧可能 |
| I-07 | コンフリクト検出 | Should | ユーザーが手動でWikiを編集した場合の競合検出 |

### 4.5 Wiki管理（Wiki Browser）

| ID | 要件 | 優先度 | 備考 |
|---|---|---|---|
| W-01 | Markdownビューア | Must | レンダリング + 生テキスト切り替え |
| W-02 | 軽量エディタ | Must | 統合適用前の手動修正や直接編集 |
| W-03 | 内部リンク補完 | Should | `[[Page Name]]` 形式のWikiリンク |
| W-04 | 全文検索 | Must | プロジェクト内Wiki + rawの全文検索 |
| W-05 | テンプレート | Should | 新規ページ作成時の雛形選択 |

### 4.6 システム・設定

| ID | 要件 | 優先度 | 備考 |
|---|---|---|---|
| S-01 | LLM API設定 | Must | OpenAI-compatible API（OpenRouter, OpenAI, Local等） |
| S-02 | モデル選択 | Must | クエリ生成用・統合用で異なるモデル指定可 |
| S-03 | 自動統合設定 | Should | オフ / N件貯まるごと / 毎日指定時刻 |
| S-04 | バックアップ | Should | wikiフォルダのGit自動コミット（設定で有効化） |
| S-05 | エクスポート | Should | Wikiを静的サイト（MkDocs等）またはPDFへ出力 |

---

## 5. 非機能要件

| 項目 | 要件 |
|---|---|
| **アーキテクチャ** | ローカルファースト。データはユーザーマシンに保存し、クラウド同期は任意 |
| **プライバシー** | raw/wikiコンテンツはローカルでインデックス化。LLM送信時は必要最小限のコンテキストのみ |
| **プラットフォーム** | デスクトップ優先（Windows / macOS / Linux）。レスポンシブUIだがモバイルは後回し |
| **パフォーマンス** | アプリ起動 < 2秒、クエリ表示 < 500ms、統合差分生成 < 10秒（モデル依存） |
| **オフライン** | クエリの閲覧・回答はオフライン可能。クエリ生成・統合のみオンライン必要 |
| **データ形式** | Wiki: Markdown（互換性重視）。DB: SQLite。設定: JSON |
| **アクセシビリティ** | キーボードのみで操作可能、選択肢は画面リーダー対応 |

---

## 6. データモデル

```
Project
├── id: UUID
├── name: String
├── rawPath: String        // rawフォルダの絶対パス
├── wikiPath: String        // wikiフォルダの絶対パス
├── llmConfig: JSON        // endpoint, model, apiKey(encrypted)
├── createdAt: DateTime
└── settings: JSON         // 自動統合設定等

Query
├── id: UUID
├── projectId: UUID
├── question: String        // 質問文
├── context: String         // 生成時の参照文脈（要約）
├── queryType: Enum         // YES_NO | MULTI_CHOICE | SCALE | SELECT
├── choices: JSON           // 選択肢リスト
├── priorityScore: Float    // 重要度スコア
├── status: Enum            // PENDING | ANSWERED | SKIPPED | ARCHIVED
├── llmGenerated: Boolean   // true: LLM生成, false: 手動作成
├── createdAt: DateTime
└── updatedAt: DateTime

Answer
├── id: UUID
├── queryId: UUID
├── selectedChoices: JSON   // 選択された値
├── freeText: String?       // 補足フリーテキスト
├── skippedReason: String?  // スキップ理由
├── createdAt: DateTime
└── integratedAt: DateTime? // 統合された日時

WikiPage
├── id: UUID
├── projectId: UUID
├── filePath: String        // wikiPathからの相対パス
├── title: String
├── content: String         // Markdown全文
├── lastIntegratedAt: DateTime?
├── lastManualEditAt: DateTime?
└── createdAt: DateTime

IntegrationBatch
├── id: UUID
├── projectId: UUID
├── status: Enum            // PENDING | PROCESSING | DONE | FAILED
├── affectedPages: JSON     // 変更されたWikiPage IDリスト
├── diffSummary: String     // 変更要約
├── createdAt: DateTime
└── completedAt: DateTime?
```

---

## 7. アーキテクチャ設計

### 7.1 技術スタック（推奨）

| Layer | Technology | 選定理由 |
|---|---|---|
| **Frontend** | React + TypeScript + Tailwind CSS | コンポーネント豊富、型安全性 |
| **Desktop Shell** | Tauri (Rust) | 軽量・高速・ローカルファイルシステムアクセス |
| **Local Server** | Rust (Tauri Command) or Node.js | ファイル監視、LLM API中継、SQLiteアクセス |
| **Database** | SQLite | 零構成、単一ファイル、ポータブル |
| **Indexing** | sqlite-vec or local embedding | ローカルでのベクトル検索・類似度判定 |
| **LLM Client** | OpenAI-compatible HTTP | 汎用性、OpenRouter/Local対応 |

### 7.2 コンポーネント構成

```
┌─────────────────────────────────────────┐
│  Tauri Desktop App (React UI)           │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Sidebar │ │ Query    │ │ Wiki     │ │
│  │(Project)│ │ Inbox    │ │ Browser  │ │
│  └─────────┘ └──────────┘ └──────────┘ │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│  Tauri Backend (Rust)                 │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ │
│  │ File    │ │ Query    │ │ LLM      │ │
│  │ Watcher │ │ Engine   │ │ Client   │ │
│  └─────────┘ └──────────┘ └──────────┘ │
│  ┌─────────┐ ┌──────────┐             │
│  │ SQLite  │ │ Integra- │             │
│  │ Store   │ │ tion     │             │
│  └─────────┘ │ Engine   │             │
│              └──────────┘             │
└─────────────────────────────────────────┘
```

### 7.3 LLMプロンプト設計（概要）

**クエリ生成プロンプト:**
```
あなたは知識策展者です。以下のプロジェクト資料（raw + wiki）を分析し、
構造化・明確化に役立つ重要な問い（クエリ）を生成してください。

各クエリは以下を満たすこと：
1. 単純な事実確認でなく、判断・整理を要する問い
2. 選択肢を必ず提示し、ユーザーの入力負荷を最小化
3. 4軸スコア（Coverage/Contradiction/Recency/Depth）を付与

出力形式: JSON配列
```

**統合プロンプト:**
```
以下の「問いと回答」のペア群を、既存Wikiの文脈に統合してください。

原則：
- 既存内容と矛盾しないよう統合する
- 新規セクションの追加、既存セクションの拡張、または脚注形式
- Markdown形式で出力
- 変更箇所をdiff形式で明示

入力：
- 既存Wikiページ（該当部分）
- 問いと回答のリスト
```

---

## 8. UI/UX 設計原則

1. **Zero-Friction（零摩擦）**
   - テキスト入力は原則不要。タップ/クリック/キーで完結
   - アプリを開いて3秒以内に最初のクエリに回答可能

2. **Inbox Zero 隐喻**
   - 未回答クエリを「Inbox」として扱う
   - 全て回答済み = インボックスゼロの達成感

3. **漸進的開示**
   - クエリの文脈・出典は折りたたみ
   - 回答後に「なぜこの問いが重要か」の解説を表示（学習効果）

4. **透明性**
   - LLMが何を考え、どのraw/wikiを参照してクエリを生成したかを表示
   - 統合差分は必ず承認前に可視化

---

## 9. 実装フェーズ

### Phase 1: Core Loop（MVP）
- [ ] プロジェクト作成・raw/wikiフォルダリンク
- [ ] LLM API接続設定
- [ ] 初回クエリ生成（手動トリガー）
- [ ] Query Inbox UI（優先度順表示 + 選択式回答）
- [ ] 回答のSQLite保存

### Phase 2: Integration
- [ ] 統合バッチ処理（手動実行）
- [ ] Wiki差分表示・承認UI
- [ ] Markdownファイル書き出し
- [ ] 統合済みクエリのアーカイブ

### Phase 3: Automation & Polish
- [ ] ファイル監視・差分インデックス更新
- [ ] 自動統合（設定可能）
- [ ] Wikiブラウザ・軽量エディタ
- [ ] Git自動コミット連携
- [ ] 静的サイトエクスポート

---

## 10. 用語集

| 用語 | 定義 |
|---|---|
| **Raw** | 未加工の知識断片（メモ、クリップ、RSS記事、会話ログ等） |
| **Wiki** | Markdownで記述された構造化知識ベース |
| **Query** | LLMまたはユーザーが生成した問い。選択肢付き |
| **Answer** | ユーザーがQueryに対して行った選択・回答 |
| **Integration** | 回答ストックをLLMがWikiに統合・書き込む処理 |
| **Coverage Gap** | Wikiやrawが未カバーの重要テーマ・概念 |

---

## 11. オープン質問・検討事項

1. **ローカルLLM対応:** 完全オフライン運用のため、Ollama等ローカルモデル対応の優先度は？
2. **マルチユーザー:** 将来的なクラウド同期・チーム共有の想定は？（現段階は単一ユーザー）
3. **rawの種別:** 画像・PDF・音声等の非テキストrawの取り扱い（OCR/文字起こしの自動実行有無）
4. **命名規則:** Wikiページのファイル命名と内部リンク規約（WikiLinks vs Markdown標準リンク）
5. **既存Wiki互換:** Obsidian / GitLab Wiki / MkDocs等の既存エコシステムとの互換性レベル
