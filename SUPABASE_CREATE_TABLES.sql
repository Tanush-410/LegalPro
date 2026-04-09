-- Supabase SQL Schema for Court Ecosystem
-- Run these queries in Supabase SQL Editor to set up tables

-- Drop existing tables if needed (CAUTION: This will delete all data)
-- DROP TABLE IF EXISTS cases;
-- DROP TABLE IF EXISTS courts;
-- DROP TABLE IF EXISTS judges;

-- Create courts table
CREATE TABLE IF NOT EXISTS courts (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    location TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create judges table
CREATE TABLE IF NOT EXISTS judges (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    designation TEXT,
    court_id BIGINT REFERENCES courts(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create cases table with all required columns
CREATE TABLE IF NOT EXISTS cases (
    id BIGSERIAL PRIMARY KEY,
    case_number TEXT NOT NULL UNIQUE,
    cnr TEXT,
    case_type TEXT,
    petitioner TEXT,
    respondent TEXT,
    judge_name TEXT,
    pdf_url TEXT,
    case_status TEXT DEFAULT 'Active',
    priority INTEGER DEFAULT 1,
    court_id BIGINT REFERENCES courts(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create judgments table (if needed)
CREATE TABLE IF NOT EXISTS judgments (
    id BIGSERIAL PRIMARY KEY,
    case_id BIGINT REFERENCES cases(id) ON DELETE CASCADE,
    judge_name TEXT,
    judgment_date DATE,
    verdict TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_cases_case_number ON cases(case_number);
CREATE INDEX IF NOT EXISTS idx_cases_case_type ON cases(case_type);
CREATE INDEX IF NOT EXISTS idx_cases_judge_name ON cases(judge_name);
CREATE INDEX IF NOT EXISTS idx_judges_name ON judges(name);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE courts ENABLE ROW LEVEL SECURITY;
ALTER TABLE judges ENABLE ROW LEVEL SECURITY;

-- Create policies to allow public read (adjust as needed for your security)
CREATE POLICY "Allow public read on cases" ON cases FOR SELECT USING (true);
CREATE POLICY "Allow public read on courts" ON courts FOR SELECT USING (true);
CREATE POLICY "Allow public read on judges" ON judges FOR SELECT USING (true);

-- Insert Karnataka High Court
INSERT INTO courts (name, location) 
VALUES ('Karnataka High Court', 'Bangalore')
ON CONFLICT (name) DO NOTHING;
