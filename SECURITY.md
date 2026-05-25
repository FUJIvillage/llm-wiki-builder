# LLM Wiki Builder — Security & Error Handling Specification

> **Version:** 1.0.0-alpha  
> **Date:** 2026-05-22

---

## 1. Threat Model

### Trust Boundaries

```
┌─────────────────────────────────────────┐
│  Untrusted Zone                         │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │ LLM API     │  │ raw files (user │  │
│  │ (OpenRouter)│  │  supplied, may  │  │
│  │             │  │  be malicious)  │  │
│  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────┘
                    │
              Tauri IPC
                    │
┌─────────────────────────────────────────┐
│  Trusted Zone (Rust Backend)            │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ │
│  │ SQLite  │ │ File    │ │ Keyring  │ │
│  │ (local) │ │ Watcher │ │ (OS API) │ │
│  └─────────┘ └─────────┘ └──────────┘ │
└─────────────────────────────────────────┘
                    │
              Tauri IPC
                    │
┌─────────────────────────────────────────┐
│  Trusted Zone (Frontend)                │
│  React app — rendered in OS WebView     │
│  (no arbitrary JS execution from raw)   │
└─────────────────────────────────────────┘
```

### Key Threats

| ID | Threat | Impact | Mitigation |
|---|---|---|---|
| T-01 | **LLM API Key leakage** | Financial loss, API abuse | OS keyring storage, never in SQLite |
| T-02 | **Path traversal via rawPath/wikiPath** | Arbitrary file read/write | Strict path validation, sandbox scope |
| T-03 | **Malicious raw file content** | XSS in Wiki Browser, prompt injection | Markdown sanitization, no HTML execution |
| T-04 | **LLM prompt injection via raw** | Malicious queries generated, data exfil | Input sanitization, output schema enforcement |
| T-05 | **SQLite injection** | Data corruption, information leak | Parameterized queries exclusively |
| T-06 | **IPC abuse from Frontend** | Unauthorized file access | Tauri capability scope per project |

---

## 2. API Key Management

### Storage: OS Keyring

```rust
// src-tauri/src/secrets/mod.rs
use keyring::Entry;

const SERVICE_NAME: &str = "com.llm-wiki-builder";

pub fn store_api_key(project_id: &str, api_key: &str) -> Result<()> {
    let entry = Entry::new(SERVICE_NAME, project_id)?;
    entry.set_password(api_key)?;
    Ok(())
}

pub fn get_api_key(project_id: &str) -> Result<String> {
    let entry = Entry::new(SERVICE_NAME, project_id)?;
    Ok(entry.get_password()?)
}

pub fn delete_api_key(project_id: &str) -> Result<()> {
    let entry = Entry::new(SERVICE_NAME, project_id)?;
    entry.delete_password()?;
    Ok(())
}
```

### Behavior

- API Key is **never persisted in SQLite** or any log file
- Frontend never receives the API Key back after creation (write-only via `create_project`)
- On project deletion, key is purged from keyring
- Key is loaded into memory only during LLM API calls, dropped immediately after
- macOS: Keychain, Windows: Credential Manager, Linux: Secret Service API (libsecret)

### Fallback (Linux headless / keyring unavailable)

```rust
// Store in ~/.local/share/llm-wiki-builder/.keys/{project_id}
// File permissions: 0o600 (owner read/write only)
// Encrypted at rest using data_dir/.master_key (256-bit random, generated on first run)
```

---

## 3. Filesystem Access Control

### Tauri Capability Configuration

```json
// src-tauri/capabilities/default.json
{
  "identifier": "default",
  "description": "Base capability with scoped FS access",
  "windows": ["main"],
  "permissions": [
    "core:default",
    {
      "identifier": "fs:allow-read",
      "allow": [{"path": "$HOME/**"}]
    },
    {
      "identifier": "fs:allow-write",
      "allow": [{"path": "$HOME/**"}]
    },
    {
      "identifier": "fs:allow-read",
      "allow": [{"path": "$APPLOCALDATA/**"}]
    }
  ]
}
```

### Runtime Path Validation

```rust
// src-tauri/src/fs_guard.rs
use std::path::{Path, PathBuf};
use anyhow::{Result, bail};

pub fn validate_project_paths(raw: &str, wiki: &str) -> Result<(PathBuf, PathBuf)> {
    let raw_path = Path::new(raw).canonicalize()?;
    let wiki_path = Path::new(wiki).canonicalize()?;
    
    // Ensure paths exist (wiki created if needed later)
    if !raw_path.exists() {
        bail!("RAW_PATH_INVALID: path does not exist");
    }
    
    // Prevent traversal outside intended directories
    let home = dirs::home_dir().ok_or_else(|| anyhow::anyhow!("Cannot determine home dir"))?;
    for path in [&raw_path, &wiki_path] {
        if !path.starts_with(&home) {
            bail!("PATH_OUTSIDE_HOME: for security, paths must be under home directory");
        }
    }
    
    // Ensure raw and wiki are not the same
    if raw_path == wiki_path {
        bail!("PATHS_IDENTICAL: raw and wiki paths must differ");
    }
    
    // Ensure wiki is not inside raw (prevents recursive indexing)
    if wiki_path.starts_with(&raw_path) {
        bail!("WIKI_INSIDE_RAW: wiki path cannot be inside raw path");
    }
    
    Ok((raw_path, wiki_path))
}
```

### File Watcher Scope

- Only watches `rawPath` and its descendants
- Ignores hidden files (`.git`, `.hermes`, etc.) by default
- Ignores binary files by extension blacklist (configurable)
- Max file size: 10MB per file (configurable); larger files skipped with warning

---

## 4. Content Sanitization

### Markdown Rendering Safety

Wiki Browser renders Markdown to HTML. Defense layers:

1. **No raw HTML**: Markdown parser strips `<script>`, `<iframe>`, `<object>`, `on*` event handlers
2. **No external resources**: `![img](http://...)` blocked; only `file://` and `data:` allowed
3. **CSP equivalent**: WebView configured with `contentSecurityPolicy` restricting inline scripts
4. **Link handling**: `[[Wiki Links]]` and relative `[links](path.md)` only; absolute URLs open in external browser

```javascript
// Tauri WebView configuration
tauri.conf.json:
{
  "app": {
    "windows": [{
      "label": "main",
      "url": "...",
      "additionalBrowserArgs": "--disable-features=InterestFeedContentSuggestions,..."
    }]
  },
  "security": {
    "csp": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: file:; connect-src 'self'"
  }
}
```

### LLM Output Sanitization

Before saving LLM-generated queries to DB:

1. **JSON Schema validation**: Reject responses with missing required fields
2. **Choice deduplication**: Remove duplicate `id` values, dedupe `label` case-insensitively
3. **Length limits**: Truncate `question` > 2000 chars, `context` > 1000 chars, `label` > 256 chars
4. **Injection check**: If raw content contains strings like `"system":`, `"role":`, `"function":`, flag for review instead of auto-saving

---

## 5. Error Handling Strategy

### Rust Error Hierarchy

```rust
// src-tauri/src/error.rs
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("PROJECT_NOT_FOUND: {0}")]
    ProjectNotFound(String),
    
    #[error("QUERY_NOT_FOUND: {0}")]
    QueryNotFound(String),
    
    #[error("PATH_INVALID: {0}")]
    PathInvalid(String),
    
    #[error("LLM_TIMEOUT: request exceeded {0}s")]
    LlmTimeout(u64),
    
    #[error("LLM_RATE_LIMITED")]
    LlmRateLimited,
    
    #[error("LLM_INVALID_RESPONSE: {0}")]
    LlmInvalidResponse(String),
    
    #[error("DB_ERROR: {0}")]
    DbError(String),
    
    #[error("INTERNAL: {0}")]
    Internal(String),
}

// Serializes to JSON for Frontend
impl serde::Serialize for AppError {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where S: serde::Serializer {
        use serde::ser::SerializeStruct;
        let mut state = serializer.serialize_struct("AppError", 2)?;
        state.serialize_field("code", &self.code())?;
        state.serialize_field("message", &self.to_string())?;
        state.end()
    }
}
```

### Retry Strategy

| Operation | Max Retries | Backoff | Terminal Error |
|---|---|---|---|
| LLM API call | 3 | 1s, 2s, 4s | `LLM_TIMEOUT`, `LLM_RATE_LIMITED` |
| File read | 2 | 100ms, 200ms | `PATH_INVALID` |
| SQLite write | 2 | 50ms, 100ms | `DB_ERROR` |

### User-Facing Error Messages

All error messages shown to users are in Japanese, actionable, and never expose internals:

| Error Code | User Message | Action |
|---|---|---|
| `LLM_TIMEOUT` | 「LLM APIへの接続がタイムアウトしました。ネットワーク接続を確認し、再試行してください。」 | Retry button |
| `LLM_RATE_LIMITED` | 「リクエスト制限に達しました。しばらく待ってから再試行してください。」 | Auto-retry countdown |
| `PATH_INVALID` | 「指定されたフォルダパスが無効です。存在するフォルダを選択してください。」 | Open file picker |
| `DB_ERROR` | 「データベース処理中にエラーが発生しました。アプリを再起動してください。」 | Restart button |
| `PROJECT_NOT_FOUND` | 「プロジェクトが見つかりません。プロジェクトリストを確認してください。」 | Navigate to home |

---

## 6. Logging & Privacy

### What is logged

```
INFO:  App startup, project create/delete, generation start/complete
WARN:  File too large skipped, LLM rate limited (no key logged)
ERROR: DB errors, path validation failures (paths logged, not content)
DEBUG: SQL queries (parameterized, no content logged in production)
```

### What is NEVER logged

- LLM API Keys
- raw file full content (only paths and hashes)
- User answers (stored in SQLite only)
- Wiki page content (stored in filesystem only)

### Log destination

- macOS: `~/Library/Logs/com.llm-wiki-builder/`
- Linux: `~/.local/share/llm-wiki-builder/logs/`
- Windows: `%APPDATA%\com.llm-wiki-builder\logs\`

Max log size: 10MB, auto-rotation.

---

## 7. Audit Checklist (Pre-Release)

- [ ] API Key never appears in SQLite, logs, or crash dumps
- [ ] `fs:allow-*` permissions scoped to project paths only
- [ ] All SQL queries use parameterized statements (grep for `format!` in SQL context → zero results)
- [ ] Markdown renderer strips `<script>`, `on*=` attributes
- [ ] LLM JSON output validated against schema before DB write
- [ ] No absolute `fs` access outside `rawPath`/`wikiPath`/app data dir
- [ ] Log files contain no sensitive content
- [ ] Binary releases signed (macOS notarization + Windows code signing planned for Phase 2)
