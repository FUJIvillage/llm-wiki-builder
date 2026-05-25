# LLM Wiki Builder — Data Model Specification

> **Version:** 1.0.0-alpha  
> **Date:** 2026-05-22  
> **DB:** SQLite 3.40+ with JSON1 extension

---

## 1. ER Diagram (Text)

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│    projects     │1       *│    queries      │1       *│    answers      │
├─────────────────┤<───────>├─────────────────┤<───────>├─────────────────┤
│ id (PK)         │         │ id (PK)         │         │ id (PK)         │
│ name (UQ)       │         │ project_id (FK) │         │ query_id (FK)   │
│ raw_path        │         │ question        │         │ selected_choices│
│ wiki_path       │         │ context         │         │ free_text       │
│ llm_endpoint    │         │ query_type      │         │ created_at      │
│ llm_model       │         │ choices (JSON)  │         │ integrated_at   │
│ settings (JSON) │         │ priority_score  │         └─────────────────┘
│ created_at      │         │ status          │
│ updated_at      │         │ llm_generated   │
└─────────────────┘         │ raw_file_refs   │
                            │ created_at      │
                            │ updated_at      │
                            └─────────────────┘
                                    │
                                    │1
                                    │
                                    ▼
                            ┌─────────────────┐
                            │ raw_documents   │
                            ├─────────────────┤
                            │ id (PK)         │
                            │ project_id (FK) │
                            │ file_path       │
                            │ content_hash    │
                            │ content_text    │
                            │ indexed_at      │
                            └─────────────────┘

┌─────────────────┐         ┌─────────────────┐
│  wiki_pages     │         │ integration_    │
├─────────────────┤         │   batches       │
│ id (PK)         │         ├─────────────────┤
│ project_id (FK) │         │ id (PK)         │
│ file_path (UQ)  │         │ project_id (FK) │
│ title           │         │ status          │
│ content         │         │ affected_pages  │
│ last_modified   │         │ diff_summary    │
│ created_at      │         │ created_at      │
└─────────────────┘         │ completed_at    │
                            └─────────────────┘
```

---

## 2. Schema Definition (SQL)

```sql
-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Projects table
CREATE TABLE projects (
    id              TEXT PRIMARY KEY,         -- UUID v4
    name            TEXT NOT NULL UNIQUE,
    raw_path        TEXT NOT NULL,
    wiki_path       TEXT NOT NULL,
    llm_endpoint    TEXT NOT NULL,
    llm_model       TEXT NOT NULL,
    settings        TEXT NOT NULL DEFAULT '{}', -- JSON: {autoIntegrate, autoIntegrateThreshold}
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Queries table
CREATE TABLE queries (
    id              TEXT PRIMARY KEY,         -- UUID v4
    project_id      TEXT NOT NULL,
    question        TEXT NOT NULL,
    context         TEXT NOT NULL DEFAULT '', -- raw file context summary shown to user
    query_type      TEXT NOT NULL CHECK(query_type IN ('yes_no', 'single_select', 'multi_select', 'scale')),
    choices         TEXT NOT NULL,            -- JSON array of {id, label, description?}
    priority_score  REAL NOT NULL CHECK(priority_score >= 0 AND priority_score <= 1),
    status          TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'answered', 'skipped', 'archived')),
    llm_generated   INTEGER NOT NULL DEFAULT 1, -- 0=false, 1=true (SQLite bool)
    raw_file_refs   TEXT NOT NULL DEFAULT '[]', -- JSON array of relative file paths
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_queries_project_status ON queries(project_id, status);
CREATE INDEX idx_queries_priority ON queries(priority_score DESC);

-- Answers table
CREATE TABLE answers (
    id                  TEXT PRIMARY KEY,     -- UUID v4
    query_id            TEXT NOT NULL UNIQUE,
    selected_choice_ids TEXT NOT NULL,        -- JSON array of choice.id strings
    free_text           TEXT,                 -- nullable
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    integrated_at       TEXT,                 -- nullable, set when batch integration occurs
    
    FOREIGN KEY (query_id) REFERENCES queries(id) ON DELETE CASCADE
);

-- Raw documents (indexed content)
CREATE TABLE raw_documents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      TEXT NOT NULL,
    file_path       TEXT NOT NULL,            -- relative to project.raw_path
    content_hash    TEXT NOT NULL,            -- xxhash64 hex for change detection
    content_text    TEXT,                     -- file content (Phase 1 full text, Phase 2 may truncate)
    indexed_at      TEXT NOT NULL DEFAULT (datetime('now')),
    
    UNIQUE(project_id, file_path),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_raw_docs_project ON raw_documents(project_id);

-- Wiki pages (mirror of filesystem, kept in sync)
CREATE TABLE wiki_pages (
    id              TEXT PRIMARY KEY,         -- UUID v4
    project_id      TEXT NOT NULL,
    file_path       TEXT NOT NULL,            -- relative to project.wiki_path
    title           TEXT NOT NULL,
    content         TEXT NOT NULL,
    last_modified   TEXT NOT NULL DEFAULT (datetime('now')),
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    
    UNIQUE(project_id, file_path),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_wiki_project ON wiki_pages(project_id);

-- Integration batches (Phase 2)
CREATE TABLE integration_batches (
    id              TEXT PRIMARY KEY,         -- UUID v4
    project_id      TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'processing', 'done', 'failed')),
    affected_pages  TEXT NOT NULL DEFAULT '[]', -- JSON array of wiki_page IDs
    diff_summary    TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at    TEXT,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Query embeddings (Phase 3: sqlite-vec extension)
-- VIRTUAL TABLE, created separately after sqlite-vec load
-- CREATE VIRTUAL TABLE query_embeddings USING vec0(
--     query_id INTEGER PRIMARY KEY,
--     embedding FLOAT[384]
-- );
```

---

## 3. JSON Schema Definitions

### Project.settings

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "autoIntegrate": { "type": "boolean", "default": false },
    "autoIntegrateThreshold": { "type": "integer", "minimum": 1, "default": 10 },
    "watchRawFolder": { "type": "boolean", "default": false }
  },
  "additionalProperties": false
}
```

### Query.choices

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["id", "label"],
    "properties": {
      "id": { "type": "string", "minLength": 1, "maxLength": 64 },
      "label": { "type": "string", "minLength": 1, "maxLength": 256 },
      "description": { "type": "string", "maxLength": 512 }
    },
    "additionalProperties": false
  },
  "minItems": 2,
  "maxItems": 20
}
```

### Query.raw_file_refs

```json
{
  "type": "array",
  "items": { "type": "string" },
  "description": "Relative paths from project.raw_path"
}
```

---

## 4. Data Lifecycle

### Query Status Transitions

```
[pending] --(submit_answer)--> [answered]
[pending] --(skip_query)--> [skipped]
[answered] --(integration batch)--> [archived]
[skipped] --(reopen)--> [pending]  (Phase 2)
```

### Answer Integration Lifecycle

```
answer.created_at         → answer exists but not yet integrated
answer.integrated_at      → linked to integration_batches.completed_at
```

When integration batch runs:
1. Collect all answers where `integrated_at IS NULL`
2. Group by related wiki page (via LLM analysis)
3. Generate diffs
4. On user approval (or auto-approval), write to filesystem
5. Update `answer.integrated_at = datetime('now')`
6. Update linked queries status to `archived`

---

## 5. Constraints & Validation

| Entity | Field | Constraint |
|---|---|---|
| projects | name | UNIQUE, 1–64 chars, alphanumeric + hyphen + underscore |
| projects | raw_path | Must exist at creation time (Rust validates) |
| projects | wiki_path | Created if missing; must be writable |
| queries | priority_score | 0.0 – 1.0, generated by LLM or manual |
| queries | question | 10–2000 chars |
| queries | choices | Min 2, max 20 options |
| answers | query_id | UNIQUE (1 answer per query max) |
| raw_documents | content_hash | xxhash64 of file content for change detection |
| wiki_pages | file_path | Relative path, syncs with filesystem |

---

## 6. Migration Strategy

SQLite migrations managed via Rust `rusqlite` with a simple `schema_version` table:

```sql
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT (datetime('now'))
);
```

Migration runner in Rust checks current version, applies sequential `.sql` files from `src-tauri/migrations/`. Phase 1 ships with version `1`.

### Migration Files Structure

```
src-tauri/migrations/
├── 001_initial.sql        -- All tables above
├── 002_vec_extension.sql  -- Phase 3: sqlite-vec virtual table
└── 003_integrations.sql   -- Phase 2: integration_batches enhancements
```
