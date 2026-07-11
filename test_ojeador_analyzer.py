import sys
import os
import sqlite3
import pytest

# Force import from the scripts directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts")))
from ojeador_analyzer import resolve_family, build_markdown, persist_run

def test_resolve_family_maps_correctly():
    """Verify that family resolver correctly classifies models based on substring match."""
    claude_info = resolve_family("claude-fable-5")
    assert claude_info["family"] == "Claude"
    assert "refusal" in claude_info["alignment_risk"].lower()
    
    gpt_info = resolve_family("gpt-4o-mini")
    assert gpt_info["family"] == "GPT-4"
    assert "sycophancy" in gpt_info["alignment_risk"].lower()

    llama_info = resolve_family("llama-3.1-405b")
    assert llama_info["family"] == "Llama"

    unmapped_info = resolve_family("random-model-v1")
    assert unmapped_info["family"] == "Other"
    assert unmapped_info["exergy_rating"] == "C"

def test_build_markdown_generates_valid_structure():
    """Verify that markdown generation correctly formats tables, alerts and limits rankings."""
    mock_data = {
        "meta": {
            "fetched_at": "2026-07-11T00:00:00Z",
            "last_updated": "Jul 11, 2026"
        },
        "models": [
            {"rank": 1, "model": "claude-fable-5", "vendor": "Anthropic", "license": "proprietary", "score": 1500, "votes": 5000},
            {"rank": 2, "model": "gpt-4o", "vendor": "OpenAI", "license": "proprietary", "score": 1490, "votes": 4000}
        ]
    }
    
    markdown_output = build_markdown(mock_data)
    
    assert "OJEADOR: LMSYS ARENA MATRIZ DE EXERGÍA" in markdown_output
    assert "claude-fable-5" in markdown_output
    assert "gpt-4o" in markdown_output
    assert "| Rango | Modelo |" in markdown_output
    assert "HASH_STAMP" in markdown_output

def test_database_persistence_prevents_duplicate_idempotency_hash():
    """Verify that multiple inserts of the same run/model do not crash and handle idempotency."""
    # Setup temporary in-memory DB
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE sync_runs (id INTEGER PRIMARY KEY AUTOINCREMENT, fetched_at TEXT, last_updated TEXT, cortex_taint TEXT)")
    conn.execute("""
        CREATE TABLE leaderboard_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            rank INTEGER,
            model TEXT,
            vendor TEXT,
            license TEXT,
            score INTEGER,
            votes INTEGER,
            cortex_taint TEXT,
            idempotency_hash TEXT UNIQUE
        )
    """)
    conn.commit()

    meta = {"fetched_at": "2026-07-11T00:00:00Z", "last_updated": "Jul 11, 2026"}
    # Pass the same model twice in the list to trigger the duplicate IntegrityError
    models = [
        {"rank": 1, "model": "claude-fable-5", "vendor": "Anthropic", "license": "proprietary", "score": 1500, "votes": 5000},
        {"rank": 1, "model": "claude-fable-5", "vendor": "Anthropic", "license": "proprietary", "score": 1500, "votes": 5000}
    ]
    taint = "test_taint_sig"

    # Insert models (contains duplicate)
    run_id = persist_run(conn, meta, models, taint)
    assert run_id == 1

    # Read from DB
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM leaderboard_snapshots")
    count = cursor.fetchone()[0]
    # The duplicate snapshot record should be caught by IntegrityError and skipped
    assert count == 1

    conn.close()
