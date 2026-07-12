import pytest

pytest.importorskip("babylon60", reason="módulo nativo babylon60 no compilado")
from cortex_inference import CortexInferenceEngine


@pytest.mark.asyncio
async def test_engine_initialization():
    engine = CortexInferenceEngine()
    await engine.initialize()
    assert engine.db is not None
    assert engine.config is not None
    await engine.close()


def test_parse_query():
    engine = CortexInferenceEngine()
    scores = engine.parse_query("¿Por qué falló esto?")
    assert "causal" in scores
    assert scores["causal"] > 0


@pytest.mark.asyncio
async def test_retrieve_primitives():
    engine = CortexInferenceEngine()
    await engine.initialize()
    scores = engine.parse_query("test causal")
    primitives, isomorphisms = await engine.retrieve_primitives(
        "MODE-01-CAUSAL-DEDUCTION", scores, "test causal"
    )
    assert isinstance(primitives, list)
    assert isinstance(isomorphisms, list)
    await engine.close()


@pytest.mark.asyncio
async def test_execute_inference():
    engine = CortexInferenceEngine()
    await engine.initialize()
    result = await engine.execute_inference("¿Cuál es la dinámica del proceso?")
    assert "query" in result
    assert "mode_activated" in result
    assert "reasoning_steps" in result
    await engine.close()


@pytest.mark.asyncio
async def test_engine_context_manager():
    async with CortexInferenceEngine() as engine:
        assert engine.db is not None
        result = await engine.execute_inference("¿Por qué falló esto?")
        assert result is not None
