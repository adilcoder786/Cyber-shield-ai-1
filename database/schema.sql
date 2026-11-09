-- ============================================================================
-- CyberShield AI — MySQL Schema
-- ============================================================================
-- Run manually with:
--   mysql -u root -p < database/schema.sql
-- Or let the backend auto-create tables on first boot via SQLAlchemy
-- (app.database.init_db). This file is provided for judges/reviewers who
-- want to inspect the schema directly, and for production deployments where
-- DB migrations should be explicit.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS cybershield_ai
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create an application user with least-privilege access (avoid using root
-- in production). Change the password before running in a real environment.
CREATE USER IF NOT EXISTS 'cybershield_user'@'%' IDENTIFIED BY 'change-this-password';
GRANT SELECT, INSERT, UPDATE, DELETE ON cybershield_ai.* TO 'cybershield_user'@'%';
FLUSH PRIVILEGES;

USE cybershield_ai;

CREATE TABLE IF NOT EXISTS scans (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    scan_type       ENUM('url', 'message', 'file') NOT NULL,
    target          VARCHAR(2048) NOT NULL,
    target_hash     VARCHAR(64) NULL,
    verdict         ENUM('safe', 'suspicious', 'malicious') NOT NULL,
    risk_score      FLOAT NOT NULL,
    explanation     JSON NOT NULL,
    details         JSON NULL,
    engine_version  VARCHAR(32) DEFAULT '1.0.0',
    source          VARCHAR(32) DEFAULT 'heuristic+ml',
    client_ip       VARCHAR(64) NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_scan_type (scan_type),
    INDEX idx_verdict (verdict),
    INDEX idx_created_at (created_at),
    INDEX idx_target_hash (target_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- Sample / demo data so the dashboard has realistic content immediately.
-- The backend's seed_data.py script inserts a richer, randomized version of
-- this via the ORM — this raw SQL version is kept here for quick manual
-- inspection or for environments where only `mysql` CLI access is available.
-- ============================================================================

INSERT INTO scans (scan_type, target, verdict, risk_score, explanation, details, source, created_at) VALUES
('url', 'http://paypal-secure-verify.tk/login', 'malicious', 92.5,
 JSON_ARRAY('Domain references a known brand (paypal) but is not that brand\'s real site',
            'Domain uses a high-risk top-level domain (.tk)',
            'URL contains sensitive action keywords (login, verify, secure)'),
 JSON_OBJECT('hostname', 'paypal-secure-verify.tk'), 'heuristic+ml', NOW() - INTERVAL 1 DAY),

('url', 'https://github.com/anthropics', 'safe', 4.0,
 JSON_ARRAY('No known phishing indicators detected in the URL structure.'),
 JSON_OBJECT('hostname', 'github.com'), 'heuristic+ml', NOW() - INTERVAL 2 DAY),

('message', 'URGENT: Your Netflix payment failed. Update your billing details immediately...', 'malicious', 88.0,
 JSON_ARRAY('Uses urgency/pressure language (immediately)', 'Requests sensitive information (card number)'),
 JSON_OBJECT('channel', 'email'), 'heuristic+ml', NOW() - INTERVAL 1 DAY),

('file', 'invoice_payment.pdf.exe', 'malicious', 95.0,
 JSON_ARRAY('Double file extension detected (\'.pdf.exe\') — a classic disguise trick',
            'File extension \'.exe\' is executable/script-based and high-risk'),
 JSON_OBJECT('extension', '.exe'), 'heuristic', NOW() - INTERVAL 3 DAY),

('url', 'https://www.wikipedia.org/wiki/Cybersecurity', 'safe', 2.0,
 JSON_ARRAY('No known phishing indicators detected in the URL structure.'),
 JSON_OBJECT('hostname', 'www.wikipedia.org'), 'heuristic+ml', NOW() - INTERVAL 4 DAY);
