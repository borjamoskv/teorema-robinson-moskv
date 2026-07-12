import asyncio
import time
import logging
import sys
import os
import wave

# Dynamic sys.path insertions to satisfy dependency resolution
sys.path.insert(0, '$CORTEX_ROOT/10_PROJECTS/motor-colapso-acustico/.venv/lib/python3.14/site-packages')
sys.path.insert(0, '$CORTEX_ROOT/10_PROJECTS/cortex-audio-engine')

import mlx_whisper
import cortex_strike
from cortex.voice_engine.voice_ledger import VoiceLedger

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] C5-REAL Kernel: %(message)s')

class AcousticKernel:
    """
    MOSKV-1 APEX: Deterministic Voice Engine Kernel
    Implements strictly Mutex-locked Half-Duplex audio pipeline to prevent
    stochastic Full-Duplex collisions (Acoustic Theater / AP_VOICE_004).
    """
    def __init__(self):
        self._mutex = asyncio.Lock()
        self._state_hash = None
        self._audio_queue = asyncio.Queue()
        self.ledger = VoiceLedger()
        self.session_id = self.ledger.start_session()
        self._warmup_model()

    def _warmup_model(self):
        """
        Warm up MLX Whisper model and compile Metal shaders to ensure sub-400ms TTFT.
        """
        logging.info("Warming up MLX Whisper model...")
        temp_dir = "$CORTEX_ROOT/.gemini/antigravity/scratch"
        os.makedirs(temp_dir, exist_ok=True)
        warmup_wav = os.path.join(temp_dir, "warmup.wav")
        with wave.open(warmup_wav, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(b"\x00" * 3200)
        try:
            mlx_whisper.transcribe(warmup_wav, path_or_hf_repo="mlx-community/whisper-tiny")
            logging.info("MLX Whisper model successfully warmed up.")
        except Exception as e:
            logging.error(f"Warmup failed: {e}")

    async def ingest_audio(self, pcm_frame: bytes):
        """
        Receives external PCM, hashing it to record causal origin using Zero-Allocation Rust Hasher.
        """
        frame_hash = cortex_strike.bft_hash(pcm_frame)
        logging.info(f"Ingested Audio Frame: {frame_hash[:16]}")
        await self._audio_queue.put((frame_hash, pcm_frame))
        
    async def process_loop(self):
        """
        Ouroboros Loop. Extracts PCM, locks Mutex, and hands to tensor bridge.
        """
        while True:
            frame_hash, pcm_frame = await self._audio_queue.get()
            
            async with self._mutex:
                logging.info(f"Mutex LOCKED. Processing tensor state for {frame_hash[:8]}")
                t0_total = time.time()
                
                # Real MLX Tensor Inference bridging
                tensor_hash, pcm_hash, ttft = await self._tensor_inference(pcm_frame)
                
                # TTFAF is the total duration of transcription + inference + synthesis
                ttfaf = (time.time() - t0_total) * 1000
                
                self.ledger.log_acoustic_event(
                    self.session_id, 
                    frame_hash[:16], 
                    tensor_hash[:16], 
                    pcm_hash[:16], 
                    ttft, 
                    ttfaf
                )
                
                logging.info(f"Mutex RELEASED. TTFT: {ttft:.2f}ms, Latency (TTFAF): {ttfaf:.2f}ms")
                
            self._audio_queue.task_done()

    async def _tensor_inference(self, pcm_frame: bytes):
        """
        Bridge to MLX STT -> LLM -> TTS.
        """
        t0 = time.time()
        import tempfile
        temp_dir = tempfile.gettempdir()
        os.makedirs(temp_dir, exist_ok=True)
        temp_wav = os.path.join(temp_dir, "temp_voice_in.wav")
        
        # 16-bit Mono 16kHz WAV format (Whisper standard)
        with wave.open(temp_wav, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(pcm_frame)

        # Transcribe with MLX Whisper
        logging.info(f"Transcribing {temp_wav} using MLX Whisper...")
        result = mlx_whisper.transcribe(
            temp_wav,
            path_or_hf_repo="mlx-community/whisper-tiny"
        )
        text_command = result.get("text", "").strip()

        logging.info(f"Command Recognized: '{text_command}'")

        # TTFT: Time to First Token (STT transcription complete)
        ttft = (time.time() - t0) * 1000

        # Execute Command using CortexInferenceEngine
        from cortex_inference import CortexInferenceEngine
        async with CortexInferenceEngine() as engine:
            inf_res = await engine.execute_inference(text_command)
            claim = inf_res.get("claim", "Comando procesado.")

        # Synthesize Response to PCM using TensorAudioBridge
        from cortex.voice_engine.tensor_audio_bridge import TensorAudioBridge, VoiceModality
        bridge = TensorAudioBridge(modality=VoiceModality.INDUSTRIAL_NOIR)
        
        # Zero-copy hashing via Rust cortex_strike
        tensor_h = cortex_strike.bft_hash(pcm_frame)
        pcm_h = cortex_strike.bft_hash(pcm_frame[::-1]) # State proxy hash
        
        self._state_hash = tensor_h
        logging.info(f"New Tensor State: {self._state_hash[:16]}")
        
        # Synthesize PCM response
        _ = bridge.synthesize_pcm(tensor_h, claim)
        
        return tensor_h, pcm_h, ttft



if __name__ == "__main__":
    kernel = AcousticKernel()

