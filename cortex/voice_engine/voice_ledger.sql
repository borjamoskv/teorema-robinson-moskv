-- MOSKV-1 APEX: Voice Causal Ledger
-- Enforces structural append to Master Ledger before session destruction. (AP_VOICE_005)

PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS voice_sessions (
    session_id TEXT PRIMARY KEY,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    termination_reason TEXT,
    CONSTRAINT chk_term CHECK (termination_reason IN ('NORMAL', 'APOPTOSIS', 'TIMEOUT'))
);

CREATE TABLE IF NOT EXISTS acoustic_events (
    event_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    input_hash TEXT NOT NULL,
    tensor_state_hash TEXT NOT NULL,
    output_pcm_hash TEXT NOT NULL,
    ttft_ms REAL NOT NULL,
    ttfaf_ms REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES voice_sessions(session_id),
    UNIQUE(tensor_state_hash) -- BFT Tie-Breaking
);

CREATE TRIGGER IF NOT EXISTS verify_ttft_limit
BEFORE INSERT ON acoustic_events
FOR EACH ROW
WHEN NEW.ttft_ms > 400.0 -- Hard thermal limit (400ms)
BEGIN
    SELECT RAISE(ABORT, 'TTFT Limit Exceeded. Anergy Detected.');
END;
