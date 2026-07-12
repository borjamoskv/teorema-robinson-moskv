from typing import Optional
from cortex.protocols.shadow_router.protocol.schemas import TTFTMeasurement

def create_ttft_measurement(request_started_at_ns: int, first_byte_at_ns: int, first_content_token_at_ns: Optional[int], completed_at_ns: int, streaming_enabled: bool) -> TTFTMeasurement:
    if not request_started_at_ns <= first_byte_at_ns <= completed_at_ns:
        raise ValueError('Invariantes temporales violados: t_start <= t_first_byte <= t_completed')
    ttfb_ms = int((first_byte_at_ns - request_started_at_ns) / 1000000)
    total_latency_ms = int((completed_at_ns - request_started_at_ns) / 1000000)
    if streaming_enabled:
        if first_content_token_at_ns is None:
            raise ValueError('first_content_token_at_ns es requerido si streaming está activo.')
        if not first_byte_at_ns <= first_content_token_at_ns <= completed_at_ns:
            raise ValueError('Invariantes temporales violados en streaming: t_first_byte <= t_first_token <= t_completed')
        ttft_ms = int((first_content_token_at_ns - request_started_at_ns) / 1000000)
        ttft_status = 'client_observed'
    else:
        first_content_token_at_ns = None
        ttft_ms = None
        ttft_status = 'unobservable_non_streaming'
    return TTFTMeasurement(request_started_at_ns=request_started_at_ns, first_byte_at_ns=first_byte_at_ns, first_content_token_at_ns=first_content_token_at_ns, completed_at_ns=completed_at_ns, ttfb_ms=ttfb_ms, ttft_ms=ttft_ms, total_latency_ms=total_latency_ms, streaming_enabled=streaming_enabled, ttft_status=ttft_status, clock_source='monotonic_ns', measurement_scope='client_end_to_end')
