# -*- coding: utf-8 -*-
import asyncio
import pytest
from pathlib import Path
import aiosqlite
from scripts.defi_scraper.c5_evm_bounty_auditor import (
    SolidityHookAuditor, 
    execute_wealth_extraction,
    PROJECT_ROOT
)

@pytest.fixture
def temp_ledger(tmp_path: Path) -> Path:
    return tmp_path / "temp_bft_ledger.db"

@pytest.mark.asyncio
async def test_solidity_hook_auditor_invariants():
    # 1. Audit MaliciousHook.sol
    malicious_path = PROJECT_ROOT / "contracts/test/MaliciousHook.sol"
    res_malicious = SolidityHookAuditor.audit_contract_file(str(malicious_path))
    
    assert res_malicious["is_vulnerable"] is True
    violations = [v["invariant"] for v in res_malicious["violations"]]
    
    # Must capture INV-01, INV-02, and INV-03 violations
    assert "INV-01" in violations
    assert "INV-02" in violations
    assert "INV-03" in violations

    # 2. Audit SecureHook.sol
    secure_path = PROJECT_ROOT / "contracts/test/SecureHook.sol"
    res_secure = SolidityHookAuditor.audit_contract_file(str(secure_path))
    
    assert res_secure["is_vulnerable"] is False
    assert len(res_secure["violations"]) == 0

@pytest.mark.asyncio
async def test_wealth_extraction_ledger_persistence(temp_ledger):
    # Initialize DB Schema physically
    async with aiosqlite.connect(temp_ledger) as db:
        schema = Path("core/master_ledger.sql").read_text()
        await db.executescript(schema)
        await db.commit()

    # Run extraction workflow using the temp ledger
    res = await execute_wealth_extraction(ledger_db=temp_ledger)
    
    assert res["status"] == "COMPLETED"
    extractions = res["extractions"]
    assert len(extractions) > 0
    
    # Verify that the malicious hook generated a strike, and it was persisted
    vulnerable_strikes = [e for e in extractions if e.get("vulnerable")]
    assert len(vulnerable_strikes) > 0
    
    # Ensure ledger receipt exists and has a sequence
    for strike in vulnerable_strikes:
        assert "ledger_receipt" in strike
        assert strike["ledger_receipt"]["seq"] > 0
        assert "entry_hash" in strike["ledger_receipt"]

    # Verify database directly to check if table matches the entries
    async with aiosqlite.connect(temp_ledger) as db:
        cur = await db.execute("SELECT COUNT(*) FROM ledger_entries WHERE stream = 'wealth_extraction'")
        row = await cur.fetchone()
        assert row[0] == len(vulnerable_strikes)
