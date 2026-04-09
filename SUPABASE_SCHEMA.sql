-- ============================================================================
-- KARNATAKA HIGH COURT JUDGMENT DATABASE SCHEMA
-- ============================================================================
-- This SQL schema should be run in your Supabase project
-- Go to: Supabase Dashboard → SQL Editor → Run Query
--

-- ============================================================================
-- TABLE: cases
-- Stores judgment/case information from Karnataka High Court
-- ============================================================================
CREATE TABLE IF NOT EXISTS cases (
    id BIGSERIAL PRIMARY KEY,
    
    -- Case Information
    case_number VARCHAR(50) NOT NULL UNIQUE,
    case_type VARCHAR(20),  -- WP, CP, WA, FA, RSA, etc.
    
    -- Timeline
    judgment_date TIMESTAMP,
    filing_date TIMESTAMP,
    
    -- Parties
    petitioner TEXT,
    respondent TEXT,
    judges TEXT,  -- Comma-separated judge names
    
    -- Status and Court Info
    court_level VARCHAR(100) DEFAULT 'High Court',
    status VARCHAR(50) DEFAULT 'Decided',
    
    -- Source Information
    pdf_url TEXT,  -- Link to PDF on judiciary.karnataka.gov.in
    source VARCHAR(100) DEFAULT 'judiciary.karnataka.gov.in',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes for faster queries
    CONSTRAINT cases_case_number_unique UNIQUE(case_number)
);

CREATE INDEX idx_cases_case_type ON cases(case_type);
CREATE INDEX idx_cases_judgment_date ON cases(judgment_date DESC);
CREATE INDEX idx_cases_court_level ON cases(court_level);
CREATE INDEX idx_cases_status ON cases(status);


-- ============================================================================
-- TABLE: documents
-- Stores document/PDF references for cases
-- ============================================================================
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    
    -- Link to case
    case_number VARCHAR(50),
    
    -- Document Information
    document_type VARCHAR(100),  -- "Judgment Order", "Petition", etc.
    document_url TEXT NOT NULL,  -- Direct link to PDF
    file_type VARCHAR(20) DEFAULT 'PDF',
    file_size VARCHAR(20),
    
    -- Status
    status VARCHAR(50) DEFAULT 'Published',  -- "Published", "Pending", etc.
    upload_date TIMESTAMP,
    
    -- Source
    source VARCHAR(100) DEFAULT 'judiciary.karnataka.gov.in',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT fk_documents_case FOREIGN KEY(case_number) REFERENCES cases(case_number)
        ON DELETE CASCADE
);

CREATE INDEX idx_documents_case_number ON documents(case_number);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_type ON documents(document_type);


-- ============================================================================
-- TABLE: sync_logs
-- Track data synchronization operations
-- ============================================================================
CREATE TABLE IF NOT EXISTS sync_logs (
    id BIGSERIAL PRIMARY KEY,
    
    -- Sync Details
    source VARCHAR(100),
    sync_timestamp TIMESTAMP DEFAULT NOW(),
    
    -- Counters
    cases_synced INT DEFAULT 0,
    documents_synced INT DEFAULT 0,
    
    -- Status
    status VARCHAR(50),  -- "pending", "completed", "failed"
    details TEXT,
    
    -- Error tracking
    error_message TEXT
);

CREATE INDEX idx_sync_logs_source ON sync_logs(source);
CREATE INDEX idx_sync_logs_timestamp ON sync_logs(sync_timestamp DESC);
CREATE INDEX idx_sync_logs_status ON sync_logs(status);


-- ============================================================================
-- TABLE: search_cache
-- Store common searches for performance
-- ============================================================================
CREATE TABLE IF NOT EXISTS search_cache (
    id BIGSERIAL PRIMARY KEY,
    
    case_type VARCHAR(20),
    year INT,
    
    results_count INT,
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_search_cache_type_year ON search_cache(case_type, year);


-- ============================================================================
-- VIEW: v_case_statistics
-- Get quick statistics about cases
-- ============================================================================
CREATE OR REPLACE VIEW v_case_statistics AS
SELECT 
    COUNT(*) as total_cases,
    COUNT(CASE WHEN case_type = 'WP' THEN 1 END) as writ_petitions,
    COUNT(CASE WHEN case_type = 'CP' THEN 1 END) as civil_petitions,
    COUNT(CASE WHEN case_type = 'WA' THEN 1 END) as writ_appeals,
    COUNT(CASE WHEN judgment_date::date = CURRENT_DATE THEN 1 END) as todays_cases,
    MAX(judgment_date) as last_judgment_date,
    MAX(created_at) as last_synced
FROM cases;


-- ============================================================================
-- VIEW: v_case_documents
-- Link cases with their documents
-- ============================================================================
CREATE OR REPLACE VIEW v_case_documents AS
SELECT 
    c.id,
    c.case_number,
    c.case_type,
    c.judgment_date,
    c.petitioner,
    c.respondent,
    c.status,
    d.id as document_id,
    d.document_type,
    d.document_url,
    d.status as document_status,
    d.upload_date
FROM cases c
LEFT JOIN documents d ON c.case_number = d.case_number;


-- ============================================================================
-- ENABLE ROW LEVEL SECURITY (Optional - for future user-based access)
-- ============================================================================
-- ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sync_logs ENABLE ROW LEVEL SECURITY;


-- ============================================================================
-- INSERT SAMPLE DATA (Optional - for testing)
-- ============================================================================
-- Uncomment to add initial sample data
-- INSERT INTO cases (case_number, case_type, judgment_date, court_level, petitioner, respondent, judges, pdf_url)
-- VALUES ('WP 1983 OF 2025', 'WP', '2026-01-06', 'High Court', 'SHUPTHA APPANNA', 'SRI MILTON MUTHANNA', 'P SREE SUDHA', 'https://judiciary.karnataka.gov.in/documents/wp_1983_2025.pdf');


COMMIT;
