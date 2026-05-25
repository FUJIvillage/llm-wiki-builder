# LLM Wiki Builder — API Specification

> **Version:** 1.0.0-alpha  
> **Date:** 2026-05-22  
> **Protocol:** Tauri Commands (Rust → Frontend IPC)

---

## 1. Overview

All communication between React Frontend and Rust Backend uses **Tauri Commands** (invoke/handler pattern). Commands are strongly typed with `serde` serialization. Errors propagate as `Result<T, AppError>` where `AppError` serializes to a structured JSON error for the Frontend.

### Error Format

```typescript
interface AppError {
  code: string;           // e.g. "LLM_TIMEOUT", "INVALID_PATH", "DB_CONSTRAINT"
  message: string;        // Human-readable (Japanese for user-facing errors)
  details?: Record<string, unknown>;
}
```

### Common Return Wrapper

All commands return either `T` on success or throw `AppError` on failure.

```typescript
// Frontend invoke pattern
import { invoke } from '@tauri-apps/api/core';

const result = await invoke<Project>('create_project', { payload });
```

---

## 2. Project Commands

### `create_project`

Creates a new project workspace.

**Request:**
```typescript
interface CreateProjectPayload {
  name: string;              // 1-64 chars, unique
  rawPath: string;           // absolute path, must exist
  wikiPath: string;          // absolute path, created if missing
  llmEndpoint: string;       // URL, e.g. "https://openrouter.ai/api/v1"
  llmModel: string;          // e.g. "anthropic/claude-sonnet-4"
  llmApiKey: string;         // stored in OS keyring, not SQLite
}
```

**Response:** `Project`

```typescript
interface Project {
  id: string;                // UUID v4
  name: string;
  rawPath: string;
  wikiPath: string;
  llmModel: string;
  llmEndpoint: string;       // key NOT included, read-only endpoint
  createdAt: string;         // ISO 8601
  updatedAt: string;
  settings: ProjectSettings;
}

interface ProjectSettings {
  autoIntegrate: boolean;    // default: false
  autoIntegrateThreshold: number; // min answers to trigger integration, default: 10
}
```

**Error Codes:**
- `INVALID_NAME`: empty or too long
- `PATH_NOT_FOUND`: rawPath does not exist
- `NAME_DUPLICATE`: project name already exists
- `LLM_ENDPOINT_INVALID`: URL parse failure

---

### `list_projects`

**Request:** `{}`

**Response:** `ProjectSummary[]`

```typescript
interface ProjectSummary {
  id: string;
  name: string;
  pendingQueryCount: number;  // computed from queries WHERE status = 'pending'
  totalAnswerCount: number;   // computed from answers
  lastIndexedAt: string | null;
  createdAt: string;
}
```

**Error Codes:** none

---

### `get_project`

**Request:** `{ projectId: string }`

**Response:** `Project`

**Error Codes:**
- `PROJECT_NOT_FOUND`

---

### `delete_project`

Soft delete (cascade delete queries/answers). Wiki/raw files on disk are NOT deleted.

**Request:** `{ projectId: string }`

**Response:** `boolean` (success)

**Error Codes:**
- `PROJECT_NOT_FOUND`

---

### `update_project_settings`

**Request:**
```typescript
interface UpdateProjectSettingsPayload {
  projectId: string;
  settings: Partial<ProjectSettings>;
}
```

**Response:** `Project`

---

## 3. Indexer Commands

### `index_raw_files`

Scans rawPath recursively and builds the content index in SQLite.

**Request:** `{ projectId: string }`

**Response:** `IndexResult`

```typescript
interface IndexResult {
  scannedFiles: number;      // total files found
  indexedFiles: number;      // files successfully read
  skippedFiles: number;      // unreadable / non-text
  totalBytes: number;        // raw content bytes
  durationMs: number;
}
```

**Events emitted:**
- `index:progress` — `{ processed: number, total: number, currentFile: string }`
- `index:complete` — `{ result: IndexResult }`

**Error Codes:**
- `PROJECT_NOT_FOUND`
- `RAW_PATH_INVALID`: path no longer exists or unreadable

---

## 4. Query Commands

### `generate_queries`

Calls LLM API with raw content summary, generates structured queries, saves to DB.

**Request:** `{ projectId: string }`

**Response:** `GenerateQueriesResult`

```typescript
interface GenerateQueriesResult {
  generatedCount: number;
  queries: Query[];          // newly created queries
  modelUsed: string;
  tokensUsed: number;        // prompt + completion
  durationMs: number;
}
```

**Events emitted:**
- `generation:start` — `{ projectId }`
- `generation:progress` — `{ stage: 'summarize' | 'generate' | 'save', detail?: string }`
- `generation:complete` — `{ result: GenerateQueriesResult }`
- `generation:error` — `{ error: AppError }`

**Error Codes:**
- `PROJECT_NOT_FOUND`
- `LLM_TIMEOUT`: >30s no response
- `LLM_RATE_LIMITED`
- `LLM_INVALID_RESPONSE`: JSON schema mismatch
- `NO_RAW_CONTENT`: indexer has not been run or all files empty

---

### `list_queries`

**Request:**
```typescript
interface ListQueriesPayload {
  projectId: string;
  status?: 'pending' | 'answered' | 'skipped' | 'archived' | 'all';  // default: 'pending'
  limit?: number;    // default: 50
  offset?: number;   // default: 0
}
```

**Response:** `Query[]`

```typescript
interface Query {
  id: string;
  projectId: string;
  question: string;
  context: string;           // raw file summary shown to user
  queryType: QueryType;
  choices: Choice[];         // answer options
  priorityScore: number;     // 0.0 – 1.0
  status: QueryStatus;
  llmGenerated: boolean;
  rawFileRefs: string[];     // relative paths from rawPath
  createdAt: string;
  updatedAt: string;
}

type QueryType = 'yes_no' | 'single_select' | 'multi_select' | 'scale';
type QueryStatus = 'pending' | 'answered' | 'skipped' | 'archived';

interface Choice {
  id: string;                // short slug, e.g. "yes", "option_a"
  label: string;             // display text
  description?: string;      // secondary line shown below label
}
```

---

### `get_query`

**Request:** `{ queryId: string }`

**Response:** `Query` (with `answer?: Answer` embedded if status is answered)

**Error Codes:**
- `QUERY_NOT_FOUND`

---

### `submit_answer`

**Request:**
```typescript
interface SubmitAnswerPayload {
  queryId: string;
  selectedChoiceIds: string[];  // empty if free-text only (discouraged)
  freeText?: string;            // optional supplementary text
}
```

**Response:** `Answer`

```typescript
interface Answer {
  id: string;
  queryId: string;
  selectedChoiceIds: string[];
  freeText: string | null;
  createdAt: string;
}
```

**Side effects:**
- Query status → `answered`
- If autoIntegrate threshold met, triggers integration batch (Phase 2)

**Error Codes:**
- `QUERY_NOT_FOUND`
- `QUERY_ALREADY_ANSWERED`
- `INVALID_CHOICE`: selectedChoiceIds contains unknown id for this query
- `ANSWER_EMPTY`: no choices selected AND no freeText provided

---

### `skip_query`

**Request:**
```typescript
interface SkipQueryPayload {
  queryId: string;
  reason?: 'not_applicable' | 'need_more_info' | 'later' | 'other';
  reasonText?: string;
}
```

**Response:** `Query` (updated)

**Error Codes:**
- `QUERY_NOT_FOUND`
- `QUERY_ALREADY_ANSWERED`

---

## 5. Wiki Commands (Phase 1: Read-Only)

### `list_wiki_pages`

**Request:** `{ projectId: string }`

**Response:** `WikiPageSummary[]`

```typescript
interface WikiPageSummary {
  id: string;
  filePath: string;          // relative to wikiPath
  title: string;
  lastModified: string;
  wordCount: number;
}
```

---

### `get_wiki_page`

**Request:** `{ pageId: string }`

**Response:** `WikiPage`

```typescript
interface WikiPage {
  id: string;
  projectId: string;
  filePath: string;
  title: string;
  content: string;           // raw Markdown
  lastModified: string;
  createdAt: string;
}
```

**Error Codes:**
- `PAGE_NOT_FOUND`

---

## 6. Integration Commands (Phase 2 Preview)

These commands exist in Phase 1 as stubs returning `NotImplemented` or minimal data.

### `run_integration` → Stub

### `get_integration_batches` → Stub returning `[]`

---

## 7. System Commands

### `get_app_info`

**Request:** `{}`

**Response:**
```typescript
interface AppInfo {
  version: string;
  tauriVersion: string;
  os: string;
  dbPath: string;
}
```

---

### `validate_llm_connection`

Tests API key / endpoint by sending a minimal request.

**Request:** `{ endpoint: string; apiKey: string; model: string }`

**Response:** `{ valid: boolean; modelName?: string; error?: string }`

---

## 8. Event Streams (Tauri → Frontend)

Tauri `Channel` used for long-running operations.

| Event | Payload | Source |
|---|---|---|
| `index:progress` | `{ processed, total, currentFile }` | `index_raw_files` |
| `index:complete` | `{ result: IndexResult }` | `index_raw_files` |
| `generation:start` | `{ projectId }` | `generate_queries` |
| `generation:progress` | `{ stage, detail }` | `generate_queries` |
| `generation:complete` | `{ result }` | `generate_queries` |
| `generation:error` | `{ error }` | `generate_queries` |

---

## 9. TypeScript Type Exports

All types are maintained in `src/types/index.ts` and kept in sync with Rust models via manual review (Phase 1). Phase 2 may adopt `ts-rs` for automatic Rust → TypeScript generation.
