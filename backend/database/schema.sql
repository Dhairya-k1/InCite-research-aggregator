-- ====================================================================
-- Research Platform - MySQL 8.0 Schema (Kapil's Part)
-- Tables:
--   1. papers
--   2. authors
--   3. paper_authors
--   4. sources
--   5. paper_versions
--   6. ingestion_jobs
--   7. processing_jobs
-- ====================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Table: sources
CREATE TABLE IF NOT EXISTS sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE,
    base_url VARCHAR(255) NOT NULL,
    rate_limit_per_minute INT DEFAULT 60,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_sources_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Table: authors
CREATE TABLE IF NOT EXISTS authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    author_id VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    affiliation VARCHAR(512) NULL,
    orcid VARCHAR(64) NULL,
    email VARCHAR(255) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_authors_author_id (author_id),
    INDEX ix_authors_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Table: papers
CREATE TABLE IF NOT EXISTS papers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paper_id VARCHAR(64) NOT NULL UNIQUE,
    title VARCHAR(512) NOT NULL,
    abstract TEXT NULL,
    published_at DATETIME NOT NULL,
    source VARCHAR(32) NOT NULL DEFAULT 'arxiv',
    source_id INT NULL,
    doi VARCHAR(128) NULL,
    primary_category VARCHAR(64) NULL,
    citation_count INT DEFAULT 0,
    version INT NOT NULL DEFAULT 1,
    storage_path VARCHAR(512) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX ix_papers_paper_id (paper_id),
    INDEX ix_papers_title (title),
    INDEX ix_papers_published_at_desc (published_at DESC),
    INDEX ix_papers_source (source),
    CONSTRAINT fk_papers_source FOREIGN KEY (source_id) REFERENCES sources (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Table: paper_authors (Many-to-Many junction)
CREATE TABLE IF NOT EXISTS paper_authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paper_id INT NOT NULL,
    author_id INT NOT NULL,
    author_order INT NOT NULL DEFAULT 0,
    is_corresponding BOOLEAN DEFAULT FALSE,
    INDEX ix_paper_authors_paper (paper_id),
    INDEX ix_paper_authors_author (author_id),
    CONSTRAINT uq_paper_author UNIQUE (paper_id, author_id),
    CONSTRAINT fk_pa_paper FOREIGN KEY (paper_id) REFERENCES papers (id) ON DELETE CASCADE,
    CONSTRAINT fk_pa_author FOREIGN KEY (author_id) REFERENCES authors (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Table: paper_versions (arXiv revisions v1, v2, v3, etc.)
CREATE TABLE IF NOT EXISTS paper_versions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paper_id INT NOT NULL,
    version_number INT NOT NULL,
    title VARCHAR(512) NOT NULL,
    abstract TEXT NULL,
    diff_summary TEXT NULL,
    pdf_url VARCHAR(512) NULL,
    storage_path VARCHAR(512) NULL,
    published_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_paper_versions_paper (paper_id),
    CONSTRAINT uq_paper_version UNIQUE (paper_id, version_number),
    CONSTRAINT fk_pv_paper FOREIGN KEY (paper_id) REFERENCES papers (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Table: ingestion_jobs
CREATE TABLE IF NOT EXISTS ingestion_jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL UNIQUE,
    source_name VARCHAR(64) NOT NULL,
    source_id INT NULL,
    external_id VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    attempts INT NOT NULL DEFAULT 0,
    max_retries INT NOT NULL DEFAULT 3,
    idempotency_key VARCHAR(128) NOT NULL UNIQUE,
    payload JSON NULL,
    error_log TEXT NULL,
    started_at DATETIME NULL,
    completed_at DATETIME NULL,
    duration_ms DOUBLE DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_ingest_job_id (job_id),
    INDEX ix_ingest_status (status),
    INDEX ix_ingest_idempotency (idempotency_key),
    CONSTRAINT fk_ij_source FOREIGN KEY (source_id) REFERENCES sources (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Table: processing_jobs
CREATE TABLE IF NOT EXISTS processing_jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL UNIQUE,
    paper_id VARCHAR(64) NOT NULL,
    paper_internal_id INT NULL,
    job_type VARCHAR(64) NOT NULL, -- pdf_processing, embedding, summarization
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    attempts INT NOT NULL DEFAULT 0,
    max_retries INT NOT NULL DEFAULT 3,
    idempotency_key VARCHAR(128) NOT NULL UNIQUE,
    payload JSON NULL,
    result JSON NULL,
    error_log TEXT NULL,
    started_at DATETIME NULL,
    completed_at DATETIME NULL,
    duration_ms DOUBLE DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_proc_job_id (job_id),
    INDEX ix_proc_paper_id (paper_id),
    INDEX ix_proc_status (status),
    INDEX ix_proc_idempotency (idempotency_key),
    CONSTRAINT fk_pj_paper FOREIGN KEY (paper_internal_id) REFERENCES papers (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;

-- Seed default sources
INSERT IGNORE INTO sources (id, name, base_url, rate_limit_per_minute, is_active)
VALUES 
    (1, 'arxiv', 'https://export.arxiv.org/api/query', 30, TRUE),
    (2, 'openalex', 'https://api.openalex.org/works', 100, TRUE);
