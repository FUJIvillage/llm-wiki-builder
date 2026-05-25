use std::fs;
use walkdir::WalkDir;

const SUPPORTED_EXTS: &[&str] = &["md", "txt", "mdown", "markdown"];
const MAX_FILE_SIZE: u64 = 10 * 1024 * 1024; // 10MB

#[derive(Debug, Clone)]
pub struct IndexResult {
    pub scanned_files: usize,
    pub indexed_files: usize,
    pub skipped_files: usize,
    pub total_bytes: u64,
    pub duration_ms: u64,
}

pub fn index_raw_files(raw_path: &str) -> Result<IndexResult, Box<dyn std::error::Error>> {
    let start = std::time::Instant::now();
    let mut scanned = 0usize;
    let mut indexed = 0usize;
    let mut skipped = 0usize;
    let mut total_bytes = 0u64;

    for entry in WalkDir::new(raw_path).follow_links(false) {
        let entry = entry?;
        if !entry.file_type().is_file() {
            continue;
        }

        let path = entry.path();
        let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("");
        if !SUPPORTED_EXTS.contains(&ext) {
            continue;
        }

        scanned += 1;
        let metadata = entry.metadata()?;
        if metadata.len() > MAX_FILE_SIZE {
            skipped += 1;
            continue;
        }

        let content = fs::read_to_string(path).unwrap_or_default();
        let _content_hash = format!("{:x}", md5::compute(&content));
        // TODO: store in DB
        total_bytes += metadata.len();
        indexed += 1;
    }

    let duration_ms = start.elapsed().as_millis() as u64;

    Ok(IndexResult {
        scanned_files: scanned,
        indexed_files: indexed,
        skipped_files: skipped,
        total_bytes,
        duration_ms,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_index_sample_raw() {
        let raw_path = std::env::var("RAW_PATH").unwrap_or_else(|_| "./sample-raw".to_string());
        if !std::path::Path::new(&raw_path).exists() {
            eprintln!("Skipping test: RAW_PATH not found: {}", raw_path);
            return;
        }

        let result = index_raw_files(&raw_path).expect("indexing failed");
        println!("Scanned: {}", result.scanned_files);
        println!("Indexed: {}", result.indexed_files);
        println!("Skipped: {}", result.skipped_files);
        println!("Total bytes: {}", result.total_bytes);
        println!("Duration: {}ms", result.duration_ms);

        assert!(result.scanned_files > 0, "should find markdown files");
    }
}
