use rusqlite::{params, Connection};

use crate::error::{AppError, Result};
use crate::models::*;

pub fn create_project(conn: &Connection, project: &Project, api_key: &str) -> Result<()> {
    // TODO: store api_key in keyring, not here
    conn.execute(
        "INSERT INTO projects (id, name, raw_path, wiki_path, llm_endpoint, llm_model, settings, created_at, updated_at)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9)",
        params![
            project.id,
            project.name,
            project.raw_path,
            project.wiki_path,
            project.llm_endpoint,
            project.llm_model,
            serde_json::to_string(&project.settings)?,
            project.created_at,
            project.updated_at,
        ],
    )?;
    Ok(())
}

pub fn list_projects(conn: &Connection) -> Result<Vec<ProjectSummary>> {
    let mut stmt = conn.prepare(
        "SELECT 
            p.id, p.name,
            (SELECT COUNT(*) FROM queries WHERE project_id = p.id AND status = 'pending') as pending,
            (SELECT COUNT(*) FROM answers WHERE query_id IN (SELECT id FROM queries WHERE project_id = p.id)) as answers,
            p.created_at
         FROM projects p
         ORDER BY p.created_at DESC"
    )?;
    let rows = stmt.query_map([], |row| {
        Ok(ProjectSummary {
            id: row.get(0)?,
            name: row.get(1)?,
            pending_query_count: row.get(2)?,
            total_answer_count: row.get(3)?,
            last_indexed_at: None,
            created_at: row.get(4)?,
        })
    })?;
    let mut projects = Vec::new();
    for row in rows {
        projects.push(row?);
    }
    Ok(projects)
}

pub fn get_project(conn: &Connection, id: &str) -> Result<Option<Project>> {
    let mut stmt = conn.prepare(
        "SELECT id, name, raw_path, wiki_path, llm_endpoint, llm_model, settings, created_at, updated_at
         FROM projects WHERE id = ?1"
    )?;
    let mut rows = stmt.query_map([id], |row| {
        let settings_str: String = row.get(6)?;
        Ok(Project {
            id: row.get(0)?,
            name: row.get(1)?,
            raw_path: row.get(2)?,
            wiki_path: row.get(3)?,
            llm_endpoint: row.get(4)?,
            llm_model: row.get(5)?,
            settings: serde_json::from_str(&settings_str).unwrap_or_default(),
            created_at: row.get(7)?,
            updated_at: row.get(8)?,
        })
    })?;
    Ok(rows.next().transpose()?)
}

pub fn delete_project(conn: &Connection, id: &str) -> Result<()> {
    conn.execute("DELETE FROM projects WHERE id = ?1", [id])?;
    Ok(())
}

// Query operations

pub fn insert_queries(conn: &Connection, queries: &[Query]) -> Result<()> {
    for q in queries {
        conn.execute(
            "INSERT INTO queries (id, project_id, question, context, query_type, choices, priority_score, status, llm_generated, raw_file_refs, created_at, updated_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12)",
            params![
                q.id, q.project_id, q.question, q.context,
                match q.query_type {
                    QueryType::YesNo => "yes_no",
                    QueryType::SingleSelect => "single_select",
                    QueryType::MultiSelect => "multi_select",
                    QueryType::Scale => "scale",
                },
                serde_json::to_string(&q.choices)?,
                q.priority_score,
                q.status.to_string(),
                q.llm_generated as i32,
                serde_json::to_string(&q.raw_file_refs)?,
                q.created_at, q.updated_at,
            ],
        )?;
    }
    Ok(())
}

pub fn list_queries(
    conn: &Connection,
    project_id: &str,
    status: Option<&str>,
    limit: i64,
    offset: i64,
) -> Result<Vec<Query>> {
    let sql = if let Some(s) = status {
        "SELECT id, project_id, question, context, query_type, choices, priority_score, status, llm_generated, raw_file_refs, created_at, updated_at
         FROM queries WHERE project_id = ?1 AND status = ?2 ORDER BY priority_score DESC LIMIT ?3 OFFSET ?4"
    } else {
        "SELECT id, project_id, question, context, query_type, choices, priority_score, status, llm_generated, raw_file_refs, created_at, updated_at
         FROM queries WHERE project_id = ?1 ORDER BY priority_score DESC LIMIT ?2 OFFSET ?3"
    };

    let mut stmt = conn.prepare(sql)?;
    let rows = if let Some(s) = status {
        stmt.query_map(params![project_id, s, limit, offset], row_to_query)?
    } else {
        stmt.query_map(params![project_id, limit, offset], row_to_query)?
    };

    let mut queries = Vec::new();
    for row in rows {
        queries.push(row?);
    }
    Ok(queries)
}

pub fn get_query(conn: &Connection, id: &str) -> Result<Option<Query>> {
    let mut stmt = conn.prepare(
        "SELECT id, project_id, question, context, query_type, choices, priority_score, status, llm_generated, raw_file_refs, created_at, updated_at
         FROM queries WHERE id = ?1"
    )?;
    let mut rows = stmt.query_map([id], row_to_query)?;
    Ok(rows.next().transpose()?)
}

pub fn update_query_status(conn: &Connection, id: &str, status: &str) -> Result<()> {
    conn.execute(
        "UPDATE queries SET status = ?1, updated_at = datetime('now') WHERE id = ?2",
        params![status, id],
    )?;
    Ok(())
}

// Answer operations

pub fn insert_answer(conn: &Connection, answer: &Answer) -> Result<()> {
    conn.execute(
        "INSERT INTO answers (id, query_id, selected_choice_ids, free_text, created_at)
         VALUES (?1, ?2, ?3, ?4, ?5)",
        params![
            answer.id,
            answer.query_id,
            serde_json::to_string(&answer.selected_choice_ids)?,
            answer.free_text,
            answer.created_at,
        ],
    )?;
    Ok(())
}

fn row_to_query(row: &rusqlite::Row) -> std::result::Result<Query, rusqlite::Error> {
    let query_type: String = row.get(4)?;
    let status: String = row.get(7)?;
    let choices_str: String = row.get(5)?;
    let refs_str: String = row.get(9)?;

    Ok(Query {
        id: row.get(0)?,
        project_id: row.get(1)?,
        question: row.get(2)?,
        context: row.get(3)?,
        query_type: match query_type.as_str() {
            "yes_no" => QueryType::YesNo,
            "single_select" => QueryType::SingleSelect,
            "multi_select" => QueryType::MultiSelect,
            _ => QueryType::Scale,
        },
        choices: serde_json::from_str(&choices_str).unwrap_or_default(),
        priority_score: row.get(6)?,
        status: match status.as_str() {
            "pending" => QueryStatus::Pending,
            "answered" => QueryStatus::Answered,
            "skipped" => QueryStatus::Skipped,
            _ => QueryStatus::Archived,
        },
        llm_generated: row.get::<_, i32>(8)? != 0,
        raw_file_refs: serde_json::from_str(&refs_str).unwrap_or_default(),
        created_at: row.get(10)?,
        updated_at: row.get(11)?,
    })
}
