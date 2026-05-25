use rusqlite::Connection;

use crate::error::Result;

pub fn run_migrations(conn: &Connection) -> Result<()> {
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT DEFAULT (datetime('now'))
        )",
        [],
    )?;

    let current_version: i32 = conn
        .query_row(
            "SELECT MAX(version) FROM schema_version",
            [],
            |row| row.get(0),
        )
        .unwrap_or(0);

    if current_version < 1 {
        migration_001_initial(conn)?;
        conn.execute(
            "INSERT INTO schema_version (version) VALUES (?1)",
            [1],
        )?;
    }

    Ok(())
}

fn migration_001_initial(conn: &Connection) -> Result<()> {
    conn.execute_batch(
        "
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS projects (
            id              TEXT PRIMARY KEY,
            name            TEXT NOT NULL UNIQUE,
            raw_path        TEXT NOT NULL,
            wiki_path       TEXT NOT NULL,
            llm_endpoint    TEXT NOT NULL,
            llm_model       TEXT NOT NULL,
            settings        TEXT NOT NULL DEFAULT '{}',
            created_at      TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS queries (
            id              TEXT PRIMARY KEY,
            project_id      TEXT NOT NULL,
            question        TEXT NOT NULL,
            context         TEXT NOT NULL DEFAULT '',
            query_type      TEXT NOT NULL CHECK(query_type IN ('yes_no', 'single_select', 'multi_select', 'scale')),
            choices         TEXT NOT NULL,
            priority_score  REAL NOT NULL CHECK(priority_score >= 0 AND priority_score <= 1),
            status          TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'answered', 'skipped', 'archived')),
            llm_generated   INTEGER NOT NULL DEFAULT 1,
            raw_file_refs   TEXT NOT NULL DEFAULT '[]',
            created_at      TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_queries_project_status ON queries(project_id, status);
        CREATE INDEX IF NOT EXISTS idx_queries_priority ON queries(priority_score DESC);

        CREATE TABLE IF NOT EXISTS answers (
            id                  TEXT PRIMARY KEY,
            query_id            TEXT NOT NULL UNIQUE,
            selected_choice_ids TEXT NOT NULL,
            free_text           TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            integrated_at       TEXT,
            FOREIGN KEY (query_id) REFERENCES queries(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS raw_documents (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id      TEXT NOT NULL,
            file_path       TEXT NOT NULL,
            content_hash    TEXT NOT NULL,
            content_text    TEXT,
            indexed_at      TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(project_id, file_path),
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_raw_docs_project ON raw_documents(project_id);

        CREATE TABLE IF NOT EXISTS wiki_pages (
            id              TEXT PRIMARY KEY,
            project_id      TEXT NOT NULL,
            file_path       TEXT NOT NULL,
            title           TEXT NOT NULL,
            content         TEXT NOT NULL,
            last_modified   TEXT NOT NULL DEFAULT (datetime('now')),
            created_at      TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(project_id, file_path),
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_wiki_project ON wiki_pages(project_id);

        CREATE TABLE IF NOT EXISTS integration_batches (
            id              TEXT PRIMARY KEY,
            project_id      TEXT NOT NULL,
            status          TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'processing', 'done', 'failed')),
            affected_pages  TEXT NOT NULL DEFAULT '[]',
            diff_summary    TEXT,
            created_at      TEXT NOT NULL DEFAULT (datetime('now')),
            completed_at    TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        "
    )?;
    Ok(())
}
