import type { Project, ProjectSummary, Query, Answer, CreateProjectPayload, SubmitAnswerPayload, SkipQueryPayload, ListQueriesPayload } from '../types';

// Toggle: VITE_USE_MOCK=true to use mock data
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

// ── API Helpers ──────────────────────────────────────────

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  return res.json();
}

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  return res.json();
}

// ── Normalizers (backend int id → frontend string id) ───

function normProject(p: any): ProjectSummary {
  return {
    id: String(p.id),
    name: p.name,
    pending_query_count: p.pending_query_count ?? 0,
    total_answer_count: p.total_answer_count ?? 0,
    last_indexed_at: p.last_indexed_at ?? null,
    created_at: p.created_at,
  };
}

function normQuery(q: any): Query {
  return {
    id: String(q.id),
    project_id: String(q.project_id),
    question: q.question,
    context: q.context ?? '',
    query_type: q.query_type,
    choices: q.choices ?? [],
    priority_score: q.priority_score,
    status: q.status,
    llm_generated: q.llm_generated ?? false,
    raw_file_refs: q.raw_file_refs ?? [],
    created_at: q.created_at,
    updated_at: q.updated_at,
  };
}

// ── Mock Data (fallback when USE_MOCK=true) ───────────────

const MOCK_PROJECTS: ProjectSummary[] = [
  {
    id: 'proj-openclaw-001',
    name: 'OpenClaw Archive',
    pending_query_count: 0,
    total_answer_count: 8,
    last_indexed_at: '2026-05-22T10:00:00Z',
    created_at: '2026-04-01T00:00:00Z',
  },
];

const MOCK_QUERIES: Query[] = [
  {
    id: 'q-001',
    project_id: 'proj-openclaw-001',
    question: 'NPU LLM App は現在の主要プロジェクトですか？',
    context: '2026-04-04.md に「NPU LLM App プロジェクト」として記録あり。他プロジェクトとの優先順位を確認したい。',
    query_type: 'yes_no',
    choices: [
      { id: 'c1', label: 'Yes', description: '最優先または主要プロジェクト' },
      { id: 'c2', label: 'No', description: '優先順位は低い／アーカイブ済み' },
    ],
    priority_score: 0.92,
    status: 'answered',
    llm_generated: true,
    raw_file_refs: ['2026-04-04.md'],
    created_at: '2026-05-22T10:00:00Z',
    updated_at: '2026-05-22T10:00:00Z',
  },
  {
    id: 'q-002',
    project_id: 'proj-openclaw-001',
    question: 'edge-tts-test の結果、どの音声合成エンジンを採用しましたか？',
    context: '2026-04-05-edge-tts-test.md に複数のTTS検証記録あり。最終的な採用方針を統一したい。',
    query_type: 'single_select',
    choices: [
      { id: 'c1', label: 'Edge TTS (Microsoft)' },
      { id: 'c2', label: 'OpenAI TTS' },
      { id: 'c3', label: 'ElevenLabs' },
      { id: 'c4', label: '未確定／継続評価中' },
    ],
    priority_score: 0.78,
    status: 'answered',
    llm_generated: true,
    raw_file_refs: ['2026-04-05-edge-tts-test.md'],
    created_at: '2026-05-22T10:01:00Z',
    updated_at: '2026-05-22T10:01:00Z',
  },
  {
    id: 'q-003',
    project_id: 'proj-openclaw-001',
    question: 'cron-setup の記録はどのカテゴリに分類しますか？',
    context: '自動化基盤の整備記録。wiki構成のカテゴリ分類に影響。',
    query_type: 'single_select',
    choices: [
      { id: 'c1', label: 'インフラ運用' },
      { id: 'c2', label: 'プロジェクト設定' },
      { id: 'c3', label: 'ツール検証' },
      { id: 'c4', label: 'セッション記録' },
    ],
    priority_score: 0.65,
    status: 'answered',
    llm_generated: true,
    raw_file_refs: ['2026-04-05-cron-setup.md'],
    created_at: '2026-05-22T10:02:00Z',
    updated_at: '2026-05-22T10:02:00Z',
  },
  {
    id: 'q-004',
    project_id: 'proj-openclaw-001',
    question: 'Memory Log の記録頻度と目的を選んでください',
    context: '2026-04-06.md はMemory Log形式。複数のセッションが混在している。',
    query_type: 'multi_select',
    choices: [
      { id: 'c1', label: '毎日定例記録' },
      { id: 'c2', label: '週次サマリー' },
      { id: 'c3', label: '障害・トラブル記録' },
      { id: 'c4', label: 'ツール設定変更ログ' },
    ],
    priority_score: 0.71,
    status: 'answered',
    llm_generated: true,
    raw_file_refs: ['2026-04-06.md'],
    created_at: '2026-05-22T10:03:00Z',
    updated_at: '2026-05-22T10:03:00Z',
  },
  {
    id: 'q-005',
    project_id: 'proj-openclaw-001',
    question: 'GitHub CLI認証の問題は解決済みですか？',
    context: '2026-04-06.md に「ブラウザ認証タイムアウト」と記録あり。現在の状態を確認。',
    query_type: 'yes_no',
    choices: [
      { id: 'c1', label: 'Yes', description: '認証成功、正常に動作中' },
      { id: 'c2', label: 'No', description: '未解決／別の認証方式を使用' },
    ],
    priority_score: 0.85,
    status: 'answered',
    llm_generated: true,
    raw_file_refs: ['2026-04-06.md'],
    created_at: '2026-05-22T10:04:00Z',
    updated_at: '2026-05-22T10:04:00Z',
  },
];

// Extra mock queries (LLM generated)
const EXTRA_MOCK_QUERIES: Query[] = [
  {
    id: 'q-2026-04-04-00-9018',
    project_id: 'proj-openclaw-001',
    question: 'OpenRouterの無料版モデル（qwen/qwen3.6-plus-preview:free）を、機密性の高いコードやプロンプトを含む開発作業で継続して使用すべきか？',
    context: 'ファイルには「無料で使用可能（条件：プロンプト/レスポンスが学習に使用）」と明記されており、NPU LLM Appの開発や自律開発サイクルで実際に使用されている。プライバシーとセキュリティのトレードオフが存在する。',
    query_type: 'yes_no',
    choices: [
      { id: 'c1', label: 'Yes', description: 'コスト優先で学習利用条件を受け入れ、継続使用する' },
      { id: 'c2', label: 'No', description: '機密情報流出リスクを避け、有料版または別プロバイダーに移行する' },
    ],
    priority_score: 0.9,
    status: 'answered',
    llm_generated: true,
    raw_file_refs: ['2026-04-04.md'],
    created_at: '2026-05-25T12:16:56.504019',
    updated_at: '2026-05-25T12:16:56.504041',
  },
  {
    id: 'q-2026-04-04-01-9019',
    project_id: 'proj-openclaw-001',
    question: 'サブエージェントspawn時の「pairing required」エラーに対して、「メインセッションで直接実行」という回避策を、今後も恒久的な運用方針として維持すべきか？',
    context: 'ファイルの「未解決の問題」セクションに記載されており、サブエージェント機能は使用できずメインセッションでの直接実行が現在の回避策となっている。並列処理やサブタスク分割の制約が生じる可能性がある。',
    query_type: 'yes_no',
    choices: [
      { id: 'c1', label: 'Yes', description: '現状の回避策を維持し、メインセッション集中運用とする' },
      { id: 'c2', label: 'No', description: 'pairing requiredエラーの根本原因解決を優先し、サブエージェント機能の復旧を目指す' },
    ],
    priority_score: 0.85,
    status: 'answered',
    llm_generated: true,
    raw_file_refs: ['2026-04-04.md'],
    created_at: '2026-05-25T12:16:56.504043',
    updated_at: '2026-05-25T12:16:56.504044',
  },
  {
    id: 'q-2026-04-04-02-9020',
    project_id: 'proj-openclaw-001',
    question: 'Andrej KarpathyのautoresearchパターンをOpenClawの自律開発サイクルに導入する場合、現時点で最も不足している前提条件はどれか？',
    context: 'ファイルではautoresearchの3要素（明確な指標、自動評価、高速イテレーション）が紹介されている。現在のNPU LLM App開発ではCI/CDとテストコードが整備されつつあるが、autoresearch特有の「自動スコア測定→commit/reset」ループは未構築である。',
    query_type: 'single_select',
    choices: [
      { id: 'c1', label: '自動評価パイプライン', description: '実験結果を自動判定し、改善/悪化を機械的に判断する仕組み（prepare.py相当）' },
      { id: 'c2', label: 'エージェント編集制約ルール', description: 'エージェントが編集可能なファイルを限定する明確なガバナンス（train.pyのみ編集可など）' },
      { id: 'c3', label: '明確な数値指標の定義', description: '「良い」ではなく数値化された評価指標（推論速度、精度、APKサイズなど）' },
      { id: 'c4', label: '高速イテレーション環境', description: '1サイクルを数分以内に完了させる計算リソースと軽量タスク設計' },
    ],
    priority_score: 0.8,
    status: 'answered',
    llm_generated: true,
    raw_file_refs: ['2026-04-04.md'],
    created_at: '2026-05-25T12:16:56.504045',
    updated_at: '2026-05-25T12:16:56.504046',
  },
];

let mockQueries = [...MOCK_QUERIES, ...EXTRA_MOCK_QUERIES];

const MOCK_ANSWERS: Answer[] = [
  { id: 'ans-q-001', query_id: 'q-001', selected_choice_ids: ['c1'], free_text: null, created_at: '2026-05-22T11:00:00Z', integrated_at: '2026-05-22T11:05:00Z' },
  { id: 'ans-q-002', query_id: 'q-002', selected_choice_ids: ['c2'], free_text: null, created_at: '2026-05-22T11:10:00Z', integrated_at: '2026-05-22T11:15:00Z' },
  { id: 'ans-q-003', query_id: 'q-003', selected_choice_ids: ['c1'], free_text: null, created_at: '2026-05-22T11:20:00Z', integrated_at: '2026-05-22T11:25:00Z' },
  { id: 'ans-q-004', query_id: 'q-004', selected_choice_ids: ['c1', 'c4'], free_text: null, created_at: '2026-05-22T11:30:00Z', integrated_at: '2026-05-22T11:35:00Z' },
  { id: 'ans-q-005', query_id: 'q-005', selected_choice_ids: ['c1'], free_text: null, created_at: '2026-05-22T11:40:00Z', integrated_at: '2026-05-22T11:45:00Z' },
  { id: 'ans-q-9018', query_id: 'q-2026-04-04-00-9018', selected_choice_ids: ['c2'], free_text: null, created_at: '2026-05-25T13:00:00Z', integrated_at: '2026-05-25T13:05:00Z' },
  { id: 'ans-q-9019', query_id: 'q-2026-04-04-01-9019', selected_choice_ids: ['c2'], free_text: null, created_at: '2026-05-25T13:10:00Z', integrated_at: '2026-05-25T13:15:00Z' },
  { id: 'ans-q-9020', query_id: 'q-2026-04-04-02-9020', selected_choice_ids: ['c1'], free_text: null, created_at: '2026-05-25T13:20:00Z', integrated_at: '2026-05-25T13:25:00Z' },
];

// ── API Exports ───────────────────────────────────────────

export async function createProject(payload: CreateProjectPayload): Promise<Project> {
  if (USE_MOCK) {
    throw new Error('Mock createProject not implemented');
  }
  return apiPost<Project>('/api/projects', payload);
}

export async function listProjects(): Promise<ProjectSummary[]> {
  if (USE_MOCK) return [...MOCK_PROJECTS];
  const data = await apiGet<any[]>('/api/projects');
  return data.map(normProject);
}

export async function listQueries(payload: ListQueriesPayload): Promise<Query[]> {
  if (USE_MOCK) {
    const filtered = mockQueries.filter(q => q.project_id === payload.project_id);
    if (payload.status) {
      return filtered.filter(q => q.status === payload.status);
    }
    return filtered;
  }
  const data = await apiGet<any[]>(`/api/projects/${payload.project_id}/queries`);
  return data.map(normQuery);
}

export async function submitAnswer(payload: SubmitAnswerPayload): Promise<Answer> {
  if (USE_MOCK) {
    const query = mockQueries.find(q => q.id === payload.query_id);
    if (!query) throw new Error('Query not found');
    query.status = 'answered';
    const answer: Answer = {
      id: `ans-${payload.query_id}-${Date.now()}`,
      query_id: payload.query_id,
      selected_choice_ids: payload.selected_choice_ids,
      free_text: payload.free_text ?? null,
      created_at: new Date().toISOString(),
      integrated_at: null,
    };
    MOCK_ANSWERS.push(answer);
    return answer;
  }
  return apiPost<Answer>(`/api/queries/${payload.query_id}/answer`, payload);
}

export async function skipQuery(payload: SkipQueryPayload): Promise<void> {
  if (USE_MOCK) {
    const query = mockQueries.find(q => q.id === payload.query_id);
    if (query) query.status = 'skipped';
    return;
  }
  await apiPost<void>(`/api/queries/${payload.query_id}/skip`, payload);
}

export async function generateQueries(projectId: string): Promise<void> {
  if (USE_MOCK) {
    // Add extra generated queries for demo
    const generated: Query[] = [
      {
        id: `q-generated-${Date.now()}`,
        project_id: projectId,
        question: 'Gateway watchdog の監視間隔を短縮すべきか？',
        context: '2026-04-07-gateway-watchdog.md に「15分間隔」で監視と記録。頻度が十分か判断したい。',
        query_type: 'yes_no',
        choices: [
          { id: 'c1', label: 'Yes', description: '5分間隔に短縮して早期検出を優先する' },
          { id: 'c2', label: 'No', description: '15分間隔を維持し、リソース消費を抑える' },
        ],
        priority_score: 0.72,
        status: 'pending',
        llm_generated: true,
        raw_file_refs: ['2026-04-07-gateway-watchdog.md'],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      {
        id: `q-generated-${Date.now() + 1}`,
        project_id: projectId,
        question: 'Free LLM Fallback 戦略として、複数プロバイダーのフォールバック順序をどうすべきか？',
        context: '2026-04-08-free-llm-fallback.md に複数の無料モデル候補が記録されている。優先順位を統一したい。',
        query_type: 'single_select',
        choices: [
          { id: 'c1', label: 'OpenRouter無料 → Fireworks無料 → ローカル' },
          { id: 'c2', label: 'Fireworks無料 → OpenRouter無料 → ローカル' },
          { id: 'c3', label: 'ローカル優先 → クラウドフォールバック' },
          { id: 'c4', label: '用途別で使い分ける（開発/本番）' },
        ],
        priority_score: 0.88,
        status: 'pending',
        llm_generated: true,
        raw_file_refs: ['2026-04-08-free-llm-fallback.md'],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      {
        id: `q-generated-${Date.now() + 2}`,
        project_id: projectId,
        question: 'Compound Command Rejection 機能は有効のまま運用すべきか？',
        context: '2026-04-07-compound-command-rejection.md に複数コマンド拒否の仕様記録あり。セキュリティと利便性のバランスを確認。',
        query_type: 'yes_no',
        choices: [
          { id: 'c1', label: 'Yes', description: 'セキュリティ優先で有効維持する' },
          { id: 'c2', label: 'No', description: '利便性向上のため無効化または緩和する' },
        ],
        priority_score: 0.75,
        status: 'pending',
        llm_generated: true,
        raw_file_refs: ['2026-04-07-compound-command-rejection.md'],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];
    mockQueries = [...mockQueries, ...generated];
    return;
  }
  await apiPost<void>(`/api/projects/${projectId}/generate`, {});
}

export interface WikiPage {
  project_id: string;
  title: string;
  content: string;
  updated_at: string;
  source_queries: number;
}

export async function exportProject(projectId: string, format: 'markdown' | 'json'): Promise<{ format: string; filename: string; content: string }> {
  return apiGet(`/api/projects/${projectId}/export?format=${format}`);
}

export async function getWikiPage(projectId: string): Promise<WikiPage> {
  if (USE_MOCK) {
    const answered = mockQueries.filter(q => q.status === 'answered');
    const sections = answered.map(q => {
      const ans = MOCK_ANSWERS.find(a => a.query_id === q.id);
      const selected = q.choices.filter(c => ans?.selected_choice_ids.includes(c.id));
      const answerText = selected.map(c => c.label).join(', ');
      return `## ${q.question}\n\n${q.context}\n\n**Answer:** ${answerText}\n\n*Sources:* ${q.raw_file_refs.join(', ')}\n`;
    }).join('\n---\n\n');
    const content = `# OpenClaw Archive Wiki\n\n*Generated from ${answered.length} answered queries*\n\n---\n\n${sections}`;
    return {
      project_id: projectId,
      title: 'OpenClaw Archive Wiki',
      content,
      updated_at: new Date().toISOString(),
      source_queries: answered.length,
    };
  }
  return apiGet<WikiPage>(`/api/projects/${projectId}/wiki`);
}
