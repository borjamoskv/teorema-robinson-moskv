import re

with open("test_ledger_actor.py", "r") as f:
    content = f.read()

# Remove DB_PATH
content = re.sub(r'DB_PATH = Path\("test_ledger\.db"\)\n+', '', content)

# Remove _purge_db and cleanup
purge_regex = r'def _purge_db\(\):.*?@pytest\.fixture\(autouse=True\)\ndef cleanup\(\):\n    _purge_db\(\)\n    yield\n    _purge_db\(\)\n+'
content = re.sub(purge_regex, '', content, flags=re.DOTALL)

# Replace DB_PATH with db_path everywhere
content = content.replace('DB_PATH', 'db_path')

# Inject fixture after imports
imports_end = content.find('from bft.ledger_actor import BFTLedgerActor, LedgerEvent, ZERO_HASH, _canonical_json, _compute_entry_hash\n')
if imports_end != -1:
    idx = imports_end + len('from bft.ledger_actor import BFTLedgerActor, LedgerEvent, ZERO_HASH, _canonical_json, _compute_entry_hash\n')
    fixture_code = '\n@pytest.fixture\ndef db_path(tmp_path: Path) -> Path:\n    return tmp_path / "test_ledger.db"\n\n'
    content = content[:idx] + fixture_code + content[idx:]

# Add db_path argument to test functions
content = re.sub(r'(async def test_\w+)\(\):', r'\1(db_path):', content)
content = re.sub(r'(def test_\w+)\(\):', r'\1(db_path):', content)

with open("test_ledger_actor.py", "w") as f:
    f.write(content)
print("Refactored test_ledger_actor.py")
