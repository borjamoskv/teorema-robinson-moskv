import re
with open('test_ledger_actor.py', 'r') as f:
    content = f.read()
content = re.sub('DB_PATH = Path\\("test_ledger\\.db"\\)\\n+', '', content)
purge_regex = 'def _purge_db\\(\\):.*?@pytest\\.fixture\\(autouse=True\\)\\ndef cleanup\\(\\):\\n    _purge_db\\(\\)\\n    yield\\n    _purge_db\\(\\)\\n+'
content = re.sub(purge_regex, '', content, flags=re.DOTALL)
content = content.replace('DB_PATH', 'db_path')
imports_end = content.find('from bft.ledger_actor import BFTLedgerActor, LedgerEvent, ZERO_HASH, _canonical_json, _compute_entry_hash\n')
if imports_end != -1:
    idx = imports_end + len('from bft.ledger_actor import BFTLedgerActor, LedgerEvent, ZERO_HASH, _canonical_json, _compute_entry_hash\n')
    fixture_code = '\n@pytest.fixture\ndef db_path(tmp_path: Path) -> Path:\n    return tmp_path / "test_ledger.db"\n\n'
    content = content[:idx] + fixture_code + content[idx:]
content = re.sub('(async def test_\\w+)\\(\\):', '\\1(db_path):', content)
content = re.sub('(def test_\\w+)\\(\\):', '\\1(db_path):', content)
with open('test_ledger_actor.py', 'w') as f:
    f.write(content)
print('Refactored test_ledger_actor.py')
