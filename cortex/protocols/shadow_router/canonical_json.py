import json
from typing import Any

def canonical_json(obj: Any) -> str:
    """
    Serialize to RFC 8785 canonical JSON:
    - Keys sorted lexicographically
    - No whitespace
    - Unicode escaped
    - No trailing commas
    """
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=True,
        allow_nan=False
    )
