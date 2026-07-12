import pytest
import asyncio
from cortex.voice_engine.acoustic_kernel import AcousticKernel
from cortex.voice_engine.voice_ledger import VoiceLedger
import cortex_strike


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
