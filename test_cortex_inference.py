import pytest
from cortex_inference import CortexInferenceEngine
import os

def test_engine_initialization():
    engine = CortexInferenceEngine()
    assert engine.db is not None
    assert engine.config is not None

def test_parse_query():
    engine = CortexInferenceEngine()
    scores = engine.parse_query("¿Por qué falló esto?")
    assert "causal" in scores
    assert scores["causal"] > 0

def test_retrieve_primitives():
    engine = CortexInferenceEngine()
    scores = engine.parse_query("test causal")
    primitives, isomorphisms = engine.retrieve_primitives("MODE-01-CAUSAL-DEDUCTION", scores, "test causal")
    assert isinstance(primitives, list)
    assert isinstance(isomorphisms, list)

def test_execute_inference():
    engine = CortexInferenceEngine()
    result = engine.execute_inference("¿Cuál es la dinámica del proceso?")
    assert "query" in result
    assert "mode_activated" in result
    assert "reasoning_steps" in result
