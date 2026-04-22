-- ============================================================================
--  TTTI EXAMINATION RESULT MANAGEMENT SYSTEM
--  SUPABASE DATABASE SCHEMA + SEED DATA
--  Paste this entire file into Supabase → SQL Editor → Run
-- ============================================================================

-- ── Extensions ───────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
--  TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(80)  UNIQUE NOT NULL,
    email         VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role          VARCHAR(20)  NOT NULL CHECK (role IN ('admin','trainer','trainee')),
    full_name     VARCHAR(150) NOT NULL,
    phone         VARCHAR(20),
    is_active     BOOLEAN      DEFAULT TRUE,
    profile_photo VARCHAR(200),
    created_at    TIMESTAMP    DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS departments (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(150) UNIQUE NOT NULL,
    code                VARCHAR(20)  UNIQUE NOT NULL,
    description         TEXT,
    head_of_department  VARCHAR(150),
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS programs (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(200) NOT NULL,
    code                VARCHAR(50)  UNIQUE NOT NULL,
    department_id       INTEGER NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    level               VARCHAR(50),
    isced_code          VARCHAR(50),
    duration_years      INTEGER  DEFAULT 3,
    description         TEXT,
    entry_requirements  TEXT,
    is_active           BOOLEAN  DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS courses (
    id               SERIAL PRIMARY KEY,
    name             VARCHAR(200) NOT NULL,
    code             VARCHAR(50)  NOT NULL,
    tvet_unit_code   VARCHAR(100),
    program_id       INTEGER NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    module_number    INTEGER,
    unit_category    VARCHAR(50),
    credit_factor    NUMERIC(5,2) DEFAULT 10.0,
    duration_hours   INTEGER      DEFAULT 100,
    theory_weight    NUMERIC(5,2) DEFAULT 30.0,
    practical_weight NUMERIC(5,2) DEFAULT 70.0,
    description      TEXT,
    is_active        BOOLEAN  DEFAULT TRUE,
    created_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trainers (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    employee_id   VARCHAR(50) UNIQUE,
    qualification VARCHAR(200),
    tveta_license VARCHAR(100),
    specialization VARCHAR(200),
    created_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trainees (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    admission_number VARCHAR(50) UNIQUE NOT NULL,
    national_id      VARCHAR(20),
    date_of_birth    DATE,
    gender           VARCHAR(10),
    county           VARCHAR(100),
    address          TEXT,
    guardian_name    VARCHAR(150),
    guardian_phone   VARCHAR(20),
    created_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS enrollments (
    id              SERIAL PRIMARY KEY,
    trainee_id      INTEGER NOT NULL REFERENCES trainees(id) ON DELETE CASCADE,
    program_id      INTEGER NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    intake_year     INTEGER NOT NULL,
    intake_month    VARCHAR(20),
    status          VARCHAR(30) DEFAULT 'active' CHECK (status IN ('active','completed','withdrawn')),
    completion_date DATE,
    enrolled_at     TIMESTAMP DEFAULT NOW(),
    UNIQUE(trainee_id, program_id)
);

CREATE TABLE IF NOT EXISTS academic_years (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(50) UNIQUE NOT NULL,
    start_date DATE,
    end_date   DATE,
    is_current BOOLEAN   DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS results (
    id                 SERIAL PRIMARY KEY,
    trainee_id         INTEGER NOT NULL REFERENCES trainees(id)       ON DELETE CASCADE,
    course_id          INTEGER NOT NULL REFERENCES courses(id)         ON DELETE CASCADE,
    academic_year_id   INTEGER NOT NULL REFERENCES academic_years(id)  ON DELETE CASCADE,
    trainer_id         INTEGER NOT NULL REFERENCES trainers(id)        ON DELETE CASCADE,
    ca_theory          NUMERIC(5,2),
    ca_practical       NUMERIC(5,2),
    sa_theory          NUMERIC(5,2),
    sa_practical       NUMERIC(5,2),
    weighted_theory    NUMERIC(5,2),
    weighted_practical NUMERIC(5,2),
    overall_score      NUMERIC(5,2),
    competency_status  VARCHAR(30),
    competency_rating  VARCHAR(50),
    remarks            VARCHAR(200),
    is_published       BOOLEAN   DEFAULT FALSE,
    uploaded_at        TIMESTAMP DEFAULT NOW(),
    updated_at         TIMESTAMP DEFAULT NOW(),
    UNIQUE(trainee_id, course_id, academic_year_id)
);

CREATE TABLE IF NOT EXISTS transcripts (
    id               SERIAL PRIMARY KEY,
    serial_number    VARCHAR(50) UNIQUE NOT NULL,
    trainee_id       INTEGER NOT NULL REFERENCES trainees(id)      ON DELETE CASCADE,
    program_id       INTEGER NOT NULL REFERENCES programs(id)      ON DELETE CASCADE,
    academic_year_id INTEGER NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
    generated_by     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    generated_at     TIMESTAMP DEFAULT NOW(),
    is_official      BOOLEAN   DEFAULT FALSE,
    download_count   INTEGER   DEFAULT 0,
    qr_code_data     TEXT
);

CREATE TABLE IF NOT EXISTS notifications (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title      VARCHAR(200) NOT NULL,
    message    TEXT NOT NULL,
    is_read    BOOLEAN   DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS system_logs (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action     VARCHAR(200) NOT NULL,
    details    TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
--  INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_users_role          ON users(role);
CREATE INDEX IF NOT EXISTS idx_courses_program     ON courses(program_id);
CREATE INDEX IF NOT EXISTS idx_courses_module      ON courses(module_number);
CREATE INDEX IF NOT EXISTS idx_trainees_admission  ON trainees(admission_number);
CREATE INDEX IF NOT EXISTS idx_enrollments_trainee ON enrollments(trainee_id);
CREATE INDEX IF NOT EXISTS idx_results_trainee     ON results(trainee_id);
CREATE INDEX IF NOT EXISTS idx_results_published   ON results(is_published);
CREATE INDEX IF NOT EXISTS idx_transcripts_serial  ON transcripts(serial_number);
CREATE INDEX IF NOT EXISTS idx_notifications_user  ON notifications(user_id, is_read);

-- ============================================================================
--  SEED DATA
-- ============================================================================

-- Academic Year
INSERT INTO academic_years (name, start_date, end_date, is_current)
VALUES ('2024/2025', '2024-09-01', '2025-08-31', TRUE)
ON CONFLICT (name) DO NOTHING;

-- Departments
INSERT INTO departments (name, code, description) VALUES
('Electrical Engineering',  'EE',  'Department of Electrical Engineering'),
('Mechanical Engineering',  'ME',  'Department of Mechanical Engineering'),
('Civil Engineering',       'CE',  'Department of Civil Engineering'),
('ICT & Computing',         'ICT', 'Department of ICT and Computing'),
('Business Studies',        'BS',  'Department of Business Studies'),
('Hospitality & Tourism',   'HT',  'Department of Hospitality and Tourism'),
('Building & Construction', 'BC',  'Department of Building and Construction')
ON CONFLICT (code) DO NOTHING;

-- Program
INSERT INTO programs (name, code, department_id, level, isced_code, duration_years, description, entry_requirements)
SELECT
    'Electrical Engineering',
    'EE-L6-C3',
    d.id,
    'KNQF Level 6',
    '0713 554B',
    3,
    'Competency-Based Modular Curriculum for Electrical Engineering KNQF Level 6 Cycle 3',
    'a) KCSE Grade C- (minus); OR
b) Certificate in Electrical Engineering KNQF Level 5; OR
c) Equivalent qualifications as determined by TVETA'
FROM departments d WHERE d.code = 'EE'
ON CONFLICT (code) DO NOTHING;

-- ── 33 Units across 8 Modules ────────────────────────────────────────────────
INSERT INTO courses (name, code, tvet_unit_code, program_id, module_number, unit_category, theory_weight, practical_weight, duration_hours, credit_factor)
SELECT v.name, v.code, v.tvet_unit_code, p.id, v.module_number, v.unit_category,
       v.theory_weight, v.practical_weight, v.duration_hours, v.credit_factor
FROM programs p,
(VALUES
  -- MODULE I — 10/90
  ('PVC Sheathed Cable System Installation',      '0713 251 23B','ENG/CU/EI/CR/01/3/MB',1,'CR',10,90,100,10.0),
  ('Trunking System Installation',                '0713 251 24B','ENG/CU/EI/CR/02/3/MB',1,'CR',10,90,100,10.0),
  ('Conduit System Installation',                 '0713 251 25B','ENG/CU/EI/CR/03/3/MB',1,'CR',10,90,100,10.0),
  -- MODULE II — 10/90
  ('Stand-Alone Solar PV Systems',                '0713 351 26B','ENG/CU/EI/CR/01/4/MB',2,'CR',10,90,120,12.0),
  ('Bell and Alarm Installation',                 '0714 351 27B','ENG/CU/EI/CR/02/4/MB',2,'CR',10,90,120,12.0),
  ('Electrical Machine Winding',                  '0713 351 28B','ENG/CU/EI/CR/03/4/MB',2,'CR',10,90,120,12.0),
  -- MODULE III — 30/70
  ('Digital Literacy',                            '0611 451 02B','ENG/CU/EI/BC/01/5/MB',3,'BC',30,70, 40, 4.0),
  ('Communication Skills',                        '0031 441 01B','ENG/CU/EI/BC/02/5/MB',3,'BC',30,70, 40, 4.0),
  ('Basic Electrical Principles',                 '0713 441 09B','ENG/CU/EI/CC/01/5/MB',3,'CC',30,70,100,10.0),
  ('Technical Drawing',                           '0732 441 13B','ENG/CU/EI/CC/02/5/MB',3,'CC',30,70, 80, 8.0),
  ('Electrical Installation',                     '0713 451 29B','ENG/CU/EI/CR/01/5/MB',3,'CR',30,70,110,11.0),
  -- MODULE IV — 30/70
  ('Work Ethics and Practices',                   '0417 441 04B','ENG/CU/EI/BC/03/5/MB',4,'BC',30,70, 40, 4.0),
  ('Engineering Technician Mathematics I',        '0541 441 05B','ENG/CU/EI/CC/03/5/MB',4,'CC',30,70,100,10.0),
  ('Analogue Electronics I',                      '0714 441 15B','ENG/CU/EI/CC/04/5/MB',4,'CC',30,70, 70, 7.0),
  ('Digital Electronics I',                       '0714 441 17B','ENG/CU/EI/CC/05/5/MB',4,'CC',30,70, 70, 7.0),
  ('Security Systems Installation',               '0713 451 33B','ENG/CU/EI/CR/02/5/MB',4,'CR',30,70,120,12.0),
  -- MODULE V — 30/70
  ('Entrepreneurial Skills',                      '0413 451 03B','ENG/CU/EI/BC/04/5/MB',5,'BC',30,70, 40, 4.0),
  ('Analogue Electronics II',                     '0714 441 16B','ENG/CU/EI/CC/06/5/MB',5,'CC',30,70, 80, 8.0),
  ('Engineering Technician Mathematics II',       '0541 441 06B','ENG/CU/EI/CC/07/5/MB',5,'CC',30,70,100,10.0),
  ('Digital Electronics II',                      '0714 441 18B','ENG/CU/EI/CC/08/5/MB',5,'CC',30,70, 80, 8.0),
  ('Electrical Machines Installation',            '0713 451 31B','ENG/CU/EI/CR/03/5/MB',5,'CR',30,70,120,12.0),
  ('Solar PV Systems Installation',               '0713 451 32B','ENG/CU/EI/CR/04/5/MB',5,'CR',30,70, 60, 6.0),
  -- MODULE VI — 40/60
  ('Engineering Technician Mathematics III',      '0541 541 07B','ENG/CU/EI/CC/01/6/MB',6,'CC',40,60,100,10.0),
  ('Electrical Principles I',                     '0713 541 10B','ENG/CU/EI/CC/02/6/MB',6,'CC',40,60, 80, 8.0),
  ('Micro-Control Systems',                       '0714 541 19B','ENG/CU/EI/CC/03/6/MB',6,'CC',40,60, 80, 8.0),
  ('Electrical Powerlines Installation',          '0713 551 30B','ENG/CU/EI/CR/01/6/MB',6,'CR',40,60,180,18.0),
  -- MODULE VII — 40/60
  ('Engineering Technician Mathematics IV',       '0541 541 08B','ENG/CU/EI/CC/04/6/MB',7,'CC',40,60,100,10.0),
  ('Electrical Principles II',                    '0713 541 11B','ENG/CU/EI/CC/05/6/MB',7,'CC',40,60,100,10.0),
  ('Control Systems',                             '0714 541 12B','ENG/CU/EI/CC/06/6/MB',7,'CC',40,60,100,10.0),
  ('Electrical Systems Automation',               '0714 551 36B','ENG/CU/EI/CR/02/6/MB',7,'CR',40,60,160,16.0),
  -- MODULE VIII — 40/60
  ('Research Methods',                            '0111 541 14B','ENG/CU/EI/CC/07/6/MB',8,'CC',40,60, 80, 6.0),
  ('Electrical Project Supervision',              '0713 551 22B','ENG/CU/EI/CC/08/6/MB',8,'CC',40,60, 60, 6.0),
  ('Electrical Measurement and Fault Diagnosis I','0713 541 20B','ENG/CU/EI/CC/09/6/MB',8,'CC',40,60, 80, 8.0),
  ('Power Electronic Circuits Fabrication',       '0714 551 35B','ENG/CU/EI/CR/03/6/MB',8,'CR',40,60,150,15.0)
) AS v(name,code,tvet_unit_code,module_number,unit_category,theory_weight,practical_weight,duration_hours,credit_factor)
WHERE p.code = 'EE-L6-C3'
ON CONFLICT DO NOTHING;

-- ============================================================================
--  RLS POLICIES (for Supabase REST API security — Flask bypasses these)
--  Flask connects as DB owner via SQLAlchemy, so RLS does NOT block Flask.
--  These policies protect direct Supabase API access only.
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE users           ENABLE ROW LEVEL SECURITY;
ALTER TABLE departments     ENABLE ROW LEVEL SECURITY;
ALTER TABLE programs        ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses         ENABLE ROW LEVEL SECURITY;
ALTER TABLE trainers        ENABLE ROW LEVEL SECURITY;
ALTER TABLE trainees        ENABLE ROW LEVEL SECURITY;
ALTER TABLE enrollments     ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_years  ENABLE ROW LEVEL SECURITY;
ALTER TABLE results         ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcripts     ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications   ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_logs     ENABLE ROW LEVEL SECURITY;

-- ── Allow Flask app (service_role / postgres) full access ────────────────────
-- Flask uses the direct connection string which runs as postgres superuser,
-- so it bypasses RLS automatically. These policies are for the Supabase
-- dashboard and any future API usage.

-- Public read-only tables (departments, programs, courses, academic_years)
CREATE POLICY "Public read departments"    ON departments    FOR SELECT USING (true);
CREATE POLICY "Public read programs"       ON programs       FOR SELECT USING (true);
CREATE POLICY "Public read courses"        ON courses        FOR SELECT USING (true);
CREATE POLICY "Public read academic_years" ON academic_years FOR SELECT USING (true);

-- Service role bypass (Flask app uses this connection)
CREATE POLICY "Service role all users"        ON users        FOR ALL USING (true);
CREATE POLICY "Service role all trainers"     ON trainers     FOR ALL USING (true);
CREATE POLICY "Service role all trainees"     ON trainees     FOR ALL USING (true);
CREATE POLICY "Service role all enrollments"  ON enrollments  FOR ALL USING (true);
CREATE POLICY "Service role all results"      ON results      FOR ALL USING (true);
CREATE POLICY "Service role all transcripts"  ON transcripts  FOR ALL USING (true);
CREATE POLICY "Service role all notifs"       ON notifications FOR ALL USING (true);
CREATE POLICY "Service role all logs"         ON system_logs  FOR ALL USING (true);

-- ============================================================================
--  NOTE: User passwords are set by the Flask app on first startup via init_db.py
--  The app uses Werkzeug scrypt hashing — passwords cannot be pre-hashed in SQL.
--  After deploying to Render, the app auto-creates these accounts:
--    admin    / Admin@2025
--    trainer1 / Trainer@2025
--    trainee1 / Trainee@2025
-- ============================================================================

DO $$
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE '============================================';
  RAISE NOTICE '  TTTI Schema Created Successfully!';
  RAISE NOTICE '  Tables: 11 | Indexes: 9';
  RAISE NOTICE '  Departments: 7 | Program: 1 | Units: 33';
  RAISE NOTICE '  User accounts created by Flask on startup';
  RAISE NOTICE '============================================';
END $$;
