import pytest
from math_kernel import calculate_exergy, DB_PATH
from decimal import Decimal
import sqlite3

def count_letters_deterministically(word: str, char: str) -> int:
    """Verifiable character counter executing in C5-REAL CPU space."""
    return word.lower().count(char.lower())

def test_bpe_blindness_prevention():
    """Verify that counting the letters in 'diecisiete' is 3, backed by ledger registration."""
    target_word = "diecisiete"
    target_char = "e"
    
    count = count_letters_deterministically(target_word, target_char)
    assert count == 3, f"Failed deterministic check: {target_word} count of {target_char} is not 3"
    
    # Anchor the calculation into the physical ledger
    node = calculate_exergy(count, Decimal("1.0"))
    assert node.exergy == Decimal("300.0")
    
    # Audit log validation
    with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tokens FROM exergy_ledger WHERE causal_hash = ?", (node.causal_hash,))
        res = cursor.fetchone()
        assert res is not None
        assert res[0] == 3
