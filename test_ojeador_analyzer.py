import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts")))
from ojeador_analyzer import (
    resolve_family,
    build_markdown,
    shannon_entropy,
    saga_1_anti_obfuscation,
    canonical_hash,
)


def test_resolve_family_maps_correctly():
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


def test_shannon_entropy():
    assert shannon_entropy("AAAA") == 0.0
    assert math.isclose(shannon_entropy("ABCD"), 2.0)


def test_saga_1_anti_obfuscation():
    assert saga_1_anti_obfuscation("ｇｐｔ－４") == "gpt-4"


def test_canonical_hash():
    payload_1 = {"b": 2, "a": 1}
    payload_2 = {"a": 1, "b": 2}
    assert canonical_hash(payload_1) == canonical_hash(payload_2)


def test_build_markdown_generates_valid_structure():
    mock_data = {
        "meta": {"fetched_at": "2026-07-11T00:00:00Z", "last_updated": "Jul 11, 2026"},
        "models": [
            {
                "rank": 1,
                "model": "claude-fable-5",
                "vendor": "Anthropic",
                "license": "proprietary",
                "score": 1500,
                "votes": 5000,
            },
            {
                "rank": 2,
                "model": "gpt-4o",
                "vendor": "OpenAI",
                "license": "proprietary",
                "score": 1490,
                "votes": 4000,
            },
        ],
    }
    markdown_output = build_markdown(mock_data, latency_ms=120, entropy=7.5)
    assert "OJEADOR: LMSYS ARENA MATRIZ DE EXERGÍA" in markdown_output
    assert "claude-fable-5" in markdown_output
    assert "gpt-4o" in markdown_output
    assert "| Rango | Modelo |" in markdown_output
    assert "HASH_STAMP" in markdown_output
    assert "120ms" in markdown_output
