# C5-REAL EXERGY CERTIFIED
"""C5-REAL Gemini Multimodal Live API & Protocol Transducer (v1.0).

Enforces:
1. Native WebSocket (WSS) streaming configuration.
2. Audio stream format assertion: 16kHz PCM mono input, 24kHz PCM mono output.
3. Barge-in real-time audio buffer purge.
4. Caller-supplied ephemeral token handling without local token fabrication.
5. Dynamic Causal Taint tracing (Ω113).
"""

import dataclasses
import hashlib
import logging
import os
import time
from typing import Dict, Optional
from urllib.parse import urlencode

logger = logging.getLogger("larsa.gemini_live")

# Standard Audio Specifications
INPUT_SAMPLE_RATE_HZ = 16000
OUTPUT_SAMPLE_RATE_HZ = 24000
AUDIO_CHANNELS = 1  # Mono
AUDIO_BIT_DEPTH = 16  # 16-bit PCM

class GeminiLiveProtocolError(Exception):
    """Base exception for Gemini Live API protocol errors."""

    pass

class AudioFormatMismatchError(GeminiLiveProtocolError):
    """Raised when audio configuration violates 16kHz/24kHz PCM standards."""

    pass

class EphemeralTokenExpiredError(GeminiLiveProtocolError):
    """Raised when an ephemeral key or auth token expires."""

    pass

@dataclasses.dataclass(frozen=True)
class AudioStreamConfig:
    input_sample_rate: int = INPUT_SAMPLE_RATE_HZ
    output_sample_rate: int = OUTPUT_SAMPLE_RATE_HZ
    channels: int = AUDIO_CHANNELS
    bit_depth: int = AUDIO_BIT_DEPTH

    def __post_init__(self) -> None:
        if self.input_sample_rate != 16000:
            raise AudioFormatMismatchError(f"Input sample rate MUST be 16000 Hz, got {self.input_sample_rate}")
        if self.output_sample_rate != 24000:
            raise AudioFormatMismatchError(f"Output sample rate MUST be 24000 Hz, got {self.output_sample_rate}")
        if self.channels != 1:
            raise AudioFormatMismatchError(f"Audio channels MUST be 1 (Mono), got {self.channels}")
        if self.bit_depth != 16:
            raise AudioFormatMismatchError(f"Bit depth MUST be 16-bit PCM, got {self.bit_depth}")

@dataclasses.dataclass
class GeminiLiveSession:
    session_id: str
    model_name: str
    config: AudioStreamConfig
    is_active: bool = True
    buffer_bytes: bytes = b""
    cortex_taint: str = ""

    def __post_init__(self) -> None:
        if not self.cortex_taint:
            seed = f"{self.session_id}:{self.model_name}:{time.time_ns()}"
            digest = hashlib.sha3_256(seed.encode("utf-8")).hexdigest()[:16]
            self.cortex_taint = f"CORTEX-TAINT:borjamoskv:gemini_live:{digest}"

class GeminiLiveClient:
    """Client Transducer for Gemini Multimodal Live API WSS streams."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "models/gemini-2.0-flash-exp",
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model
        self.active_sessions: Dict[str, GeminiLiveSession] = {}

    def create_session(self, session_id: str, config: Optional[AudioStreamConfig] = None) -> GeminiLiveSession:
        if not session_id:
            raise ValueError("session_id cannot be empty")

        stream_config = config or AudioStreamConfig()
        session = GeminiLiveSession(session_id=session_id, model_name=self.model, config=stream_config)
        self.active_sessions[session_id] = session
        logger.info(f"Created Gemini Live Session {session_id} [Taint: {session.cortex_taint}]")
        return session

    def process_barge_in(self, session_id: str) -> int:
        """Purges active audio output buffer upon user speech interruption (Barge-in).

        Returns bytes purged.
        """
        if session_id not in self.active_sessions:
            raise KeyError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        purged_bytes = len(session.buffer_bytes)
        session.buffer_bytes = b""
        logger.info(f"Barge-in triggered for session {session_id}: purged {purged_bytes} bytes")
        return purged_bytes

    def generate_websocket_url(
        self,
        session_id: str,
        use_ephemeral_token: bool = True,
        *,
        ephemeral_token: Optional[str] = None,
    ) -> str:
        """Build a Live API URL for an active session.

        For ephemeral authentication, pass the token name issued by Gemini's
        auth_tokens API. This method does not create or validate that token.
        URLs contain credentials and must be handled as secrets.
        """
        if session_id not in self.active_sessions:
            raise KeyError(f"Session {session_id} not found")

        base_host = "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage"
        if use_ephemeral_token:
            if not ephemeral_token or not ephemeral_token.strip():
                raise ValueError("A Gemini-issued ephemeral token is required")
            if self.api_key and ephemeral_token == self.api_key:
                raise ValueError("The API key cannot be used as an ephemeral token")
            endpoint = f"{base_host}.v1beta.GenerativeService.BidiGenerateContentConstrained"
            return f"{endpoint}?{urlencode({'access_token': ephemeral_token})}"

        if ephemeral_token is not None:
            raise ValueError("ephemeral_token cannot be used with API key authentication")
        if not self.api_key:
            raise ValueError("API Key is missing and ephemeral tokens are disabled")
        endpoint = f"{base_host}.v1alpha.GenerativeService.BidiGenerateContent"
        return f"{endpoint}?{urlencode({'key': self.api_key})}"
