pub mod repo;
pub mod schema;

use rusqlite::Connection;
use std::path::PathBuf;
use std::sync::Mutex;

pub struct DbState(pub Mutex<Connection>);

pub fn init_db(app_data_dir: PathBuf) -> crate::error::Result<DbState> {
    let db_path = app_data_dir.join("db.sqlite");
    std::fs::create_dir_all(&app_data_dir)?;
    let conn = Connection::open(&db_path)?;
    schema::run_migrations(&conn)?;
    Ok(DbState(Mutex::new(conn)))
}
