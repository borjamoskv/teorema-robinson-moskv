from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Literal
from datetime import datetime

class SignatureBlock(BaseModel):
    model_config = ConfigDict(frozen=True)
    algorithm: Literal['Ed25519']
    key_id: str
    value: str
    signed_at: datetime
    valid_until: Optional[datetime] = None

class ReceiptEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True)
    schema_version: str = 'proof-of-route/envelope/v0.2.2'
    parent_signed_receipt_hash: Optional[str] = None
    payload_hash: str
    signature: SignatureBlock
    payload: dict

class EgressPermit(BaseModel):
    model_config = ConfigDict(frozen=True)
    schema_version: str = Field(default='proof-of-route/egress-permit/v0.2.2', alias='schema')
    issuer: str
    decision_signed_receipt_hash: str
    route_id: str
    purpose: Literal['primary', 'shadow']
    permit_id: str
    issued_at: datetime
    expires_at: datetime
    single_use: bool

class RoutingPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)
    selected_route: str
    selection_propensity_basis_points: int
    candidate_set_hash: str
    policy_version: str
    features_hash: str

class ShadowRouteSelection(BaseModel):
    model_config = ConfigDict(frozen=True)
    route_id: str
    conditional_inclusion_probability_basis_points: int

class ShadowPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)
    eligible: bool
    inclusion_probability_basis_points: int
    selection_strategy: str
    selected_shadow_routes: List[ShadowRouteSelection]

class UtilityPredictions(BaseModel):
    model_config = ConfigDict(frozen=True)
    selected_model_utility_basis_points: int
    shadow_candidates_utility_basis_points: Dict[str, int]
    utility_spec_hash: str

class PrivacyDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    provider_approved: bool
    processing_region_allowed: bool
    data_classification_allowed: bool
    legal_basis_present: bool

class PrivacyEligibilityResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    shadow_allowed: bool
    reasons: List[str]
    blocked_reasons: List[str]
    data_classification: str
    region: str
    privacy_decisions: Dict[str, PrivacyDecision]

class DecisionReceipt(BaseModel):
    model_config = ConfigDict(frozen=True)
    receipt_type: Literal['decision_receipt'] = 'decision_receipt'
    request_id: str
    routing_policy: RoutingPolicy
    shadow_policy: ShadowPolicy
    utility_predictions: UtilityPredictions
    privacy_eligibility: PrivacyEligibilityResult
    prompt_commitment: str
    config_hash: str

class TTFTMeasurement(BaseModel):
    model_config = ConfigDict(frozen=True)
    request_started_at_ns: int
    first_byte_at_ns: int
    first_content_token_at_ns: Optional[int] = None
    completed_at_ns: int
    ttfb_ms: int
    ttft_ms: Optional[int] = None
    total_latency_ms: int
    streaming_enabled: bool
    ttft_status: Literal['client_observed', 'unobservable_non_streaming']
    clock_source: Literal['monotonic_ns'] = 'monotonic_ns'
    measurement_scope: Literal['client_end_to_end'] = 'client_end_to_end'

class TelemetrySource(BaseModel):
    model_config = ConfigDict(frozen=True)
    measurement_source: Literal['client_observed', 'provider_attested']
    provider_internal_telemetry_available: bool
    provider_attestation_hash: Optional[str] = None
    internal_components: Optional[Dict[str, int]] = None

class ExecutionMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)
    tokens_in: int
    tokens_out: int
    cost_microusd: int
    model_id: str
    provider: str
    region: str
    success: bool
    error_code: Optional[str] = None
    retries: int = 0
    fallback_triggered: bool = False

class ExecutionReceipt(BaseModel):
    model_config = ConfigDict(frozen=True)
    receipt_type: Literal['execution_receipt'] = 'execution_receipt'
    decision_receipt_hash: str
    ttft_measurement: TTFTMeasurement
    telemetry_source: TelemetrySource
    execution_metrics: ExecutionMetrics
    response_commitment: str

class ObservedProxyRegret(BaseModel):
    model_config = ConfigDict(frozen=True)
    selected_route_id: str
    best_observed_route_id: str
    selected_utility_basis_points: int
    best_observed_utility_basis_points: int
    observed_proxy_regret_basis_points: int
    utility_spec_hash: str
    evaluator_hash: str

class EvaluationReceipt(BaseModel):
    model_config = ConfigDict(frozen=True)
    receipt_type: Literal['evaluation_receipt'] = 'evaluation_receipt'
    dependencies: List[Dict[str, str]]
    observed_proxy_regret: ObservedProxyRegret
    evaluation_completed_at_unix: int

class CohortDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)
    cohort_id: str
    workload: str
    region: str
    model_versions: List[str]
    slo_target: str

class ConfidenceInterval(BaseModel):
    model_config = ConfigDict(frozen=True)
    level_basis_points: int
    lower_basis_points: int
    upper_basis_points: int
    method: str

class AggregateMetric(BaseModel):
    model_config = ConfigDict(frozen=True)
    metric_name: str
    estimate_basis_points: int
    confidence_interval: ConfidenceInterval
    sample_size: int

class ProxyDifferenceEstimate(BaseModel):
    model_config = ConfigDict(frozen=True)
    estimand: str
    estimate_basis_points: int
    confidence_interval: ConfidenceInterval
    estimator: str
    assumptions: List[str]
    sample_size: int
    effective_sample_size: int
    max_weight_basis_points: int
    weight_trimming_applied: bool

class AggregateEvaluationReport(BaseModel):
    model_config = ConfigDict(frozen=True)
    receipt_type: Literal['aggregate_evaluation_report'] = 'aggregate_evaluation_report'
    cohort: CohortDefinition
    period_start: str
    period_end: str
    metrics: List[AggregateMetric]
    proxy_difference_estimates: List[ProxyDifferenceEstimate]
    dataset_hash: str
    policy_hash: str
    evaluator_hash: str
    ontology_commit: Optional[str] = None
    included_envelope_hashes: List[str]
    bootstrap_replicates: int
    random_seed: int
