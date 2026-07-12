from typing import Any, Union
import unicodedata


def _escape_unicode_char(char: str) -> str:
    code_point = ord(char)
    if char == '"':
        return '\\"'
    elif char == "\\":
        return "\\\\"
    elif code_point < 32:
        if char == "\x08":
            return "\\b"
        if char == "\t":
            return "\\t"
        if char == "\n":
            return "\\n"
        if char == "\x0c":
            return "\\f"
        if char == "\r":
            return "\\r"
        return f"\\u{code_point:04x}"
    else:
        return char


def _canonicalize_string(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    result = []
    for char in s:
        result.append(_escape_unicode_char(char))
    return '"' + "".join(result) + '"'


def _canonicalize_number(n: Union[int, float]) -> str:
    if isinstance(n, bool):
        return "true" if n else "false"
    if isinstance(n, int):
        return str(n)
    if isinstance(n, float):
        if n != n:
            raise ValueError("NaN is not allowed in canonical JSON")
        if n == float("inf") or n == float("-inf"):
            raise ValueError("Infinity is not allowed in canonical JSON")
        s = repr(n)
        s = s.replace("E", "e")
        if "." in s and "e" not in s:
            s = s.rstrip("0").rstrip(".")
            if "." not in s:
                s += ".0"
        return s
    raise TypeError(f"Unsupported number type: {type(n)}")


def _canonicalize_value(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return _canonicalize_number(v)
    if isinstance(v, str):
        return _canonicalize_string(v)
    if isinstance(v, list):
        return "[" + ",".join((_canonicalize_value(item) for item in v)) + "]"
    if isinstance(v, dict):
        return _canonicalize_object(v)
    raise TypeError(f"Unsupported type for canonicalization: {type(v)}")


def _canonicalize_object(obj: dict) -> str:
    if not obj:
        return "{}"
    sorted_keys = sorted(obj.keys(), key=lambda k: [ord(c) for c in k])
    pairs = []
    for key in sorted_keys:
        canonical_key = _canonicalize_string(key)
        canonical_value = _canonicalize_value(obj[key])
        pairs.append(f"{canonical_key}:{canonical_value}")
    return "{" + ",".join(pairs) + "}"


def canonicalize(obj: Any) -> str:
    return _canonicalize_value(obj)


def canonical_hash(obj: Any) -> str:
    import hashlib

    canonical = canonicalize(obj)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
