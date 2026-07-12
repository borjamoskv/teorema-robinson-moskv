import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Mock mlx_whisper and CortexInferenceEngine BEFORE importing acoustic_kernel to prevent hangs
mock_mlx_whisper = MagicMock()
mock_mlx_whisper.transcribe.return_value = {"text": "Por qué falló el sistema al cambiar el estado del proceso"}
sys.modules["mlx_whisper"] = mock_mlx_whisper

# Mock CortexInferenceEngine
class MockCortexInferenceEngine:
    def __init__(self, *args, **kwargs):
        pass
    async def initialize(self):
        pass
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    async def execute_inference(self, query):
        return {"claim": "Comando procesado en modo mock."}
    async def close(self):
        pass

mock_engine_module = MagicMock()
mock_engine_module.CortexInferenceEngine = MockCortexInferenceEngine
sys.modules["cortex_inference"] = mock_engine_module

# Clean the local database to prevent UNIQUE constraint failures on tensor_state_hash
db_path = "cortex/voice_engine/voice_ledger.db"
db_shm = db_path + "-shm"
db_wal = db_path + "-wal"
for path in (db_path, db_shm, db_wal):
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass

import pytest
import asyncio
import cortex_strike
from cortex.voice_engine.acoustic_kernel import AcousticKernel
from cortex.voice_engine.voice_ledger import VoiceLedger


@pytest.mark.asyncio
async def test_acoustic_kernel_pipeline():
    test_bytes = b"C5-REAL-VOICE-PAYLOAD"
    hash_rs = cortex_strike.bft_hash(test_bytes)
    assert len(hash_rs) == 64

    kernel = AcousticKernel()
    assert kernel.session_id is not None
    
    pcm_frame = b"\x00" * (16000 * 2)
    await kernel.ingest_audio(pcm_frame)
    
    task = asyncio.create_task(kernel.process_loop())
    await kernel._audio_queue.join()
    task.cancel()
    
    ledger = VoiceLedger()
    conn = ledger._get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM acoustic_events WHERE session_id = ?", (kernel.session_id,)
    )
    events = cursor.fetchall()
    assert len(events) > 0, (
        "Acoustic event should be recorded in the C5-REAL database ledger"
    )
    event = events[0]
    print(f"Verified logged event: {event}")
    assert event[5] < 400.0, "TTFT must be below the 400ms hard thermal limit"
    conn.close()
