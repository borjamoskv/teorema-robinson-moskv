from cortex.protocols.shadow_router.signing.jcs_rfc8785 import canonicalize


def test_rfc8785_vectors() -> None:
    assert canonicalize({"b": 2, "a": 1}) == '{"a":1,"b":2}'
    assert canonicalize({"c": {"b": 2, "a": 1}, "a": 0}) == '{"a":0,"c":{"a":1,"b":2}}'
    assert canonicalize({"ñ": 1, "é": 2, "a": 3}) == '{"a":3,"é":2,"ñ":1}'


def test_unicode_escaping() -> None:
    assert canonicalize({"key": "€"}) == '{"key":"€"}'
