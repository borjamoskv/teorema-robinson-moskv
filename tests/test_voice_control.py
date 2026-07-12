import pytest
import asyncio
import os
import wave
from cortex.voice_engine.acoustic_kernel import AcousticKernel
from cortex.voice_engine.voice_ledger import VoiceLedger
import cortex_strike

# Verification Test for upgraded C5-REAL Voice Control
@pytest.mark.asyncio
async def test_acoustic_kernel_pipeline():
    # 1. Verify Rust cortex_strike hashing is working in the environment
    test_bytes = b"C5-REAL-VOICE-PAYLOAD"
    hash_rs = cortex_strike.bft_hash(test_bytes)
    assert len(hash_rs) == 64  # Blake3 hex hash length

    # 2. Initialize the kernel
    kernel = AcousticKernel()
    assert kernel.session_id is not None
    
    # 3. Load the physical test.wav file
    test_wav_path = "$CORTEX_ROOT/10_PROJECTS/motor-colapso-acustico/test.wav"
    assert os.path.exists(test_wav_path), "Test WAV file must exist in reality"
    
    with wave.open(test_wav_path, "rb") as wav_file:
        pcm_frame = wav_file.readframes(wav_file.getnframes())
        
    # 4. Ingest and run single-step process
    await kernel.ingest_audio(pcm_frame)
    
    # Spawn the process loop as a background task
    task = asyncio.create_task(kernel.process_loop())
    
    # Give it some time to run the transcription, inference, and ledger logging
    await asyncio.sleep(8.0)
    
    # Clean up the task
    task.cancel()
    
    # 5. Assertions on the DB Ledger to verify BFT consensus
    ledger = VoiceLedger()
    conn = ledger._get_conn()
    cursor = conn.cursor()
    
    # Verify the event was logged and latency is recorded
    cursor.execute("SELECT * FROM acoustic_events WHERE session_id = ?", (kernel.session_id,))
    events = cursor.fetchall()
    
    assert len(events) > 0, "Acoustic event should be recorded in the C5-REAL database ledger"
    
    event = events[0]
    # event structure: event_id, session_id, input_hash, tensor_state_hash, output_pcm_hash, ttft_ms, ttfaf_ms
    print(f"Verified logged event: {event}")
    assert event[5] < 400.0, "TTFT must be below the 400ms hard thermal limit"
    
    conn.close()
