from typing import List, Dict
from cortex.protocols.shadow_router.protocol.schemas import PrivacyDecision, PrivacyEligibilityResult

def check_shadow_eligibility_per_route(
    data_classification: str,
    region: str,
    allowed_regions: List[str],
    allowed_classifications: List[str],
    approved_providers: List[str],
    shadow_candidates: List[Dict[str, str]],  # [{"route_id": "...", "provider": "...", "region": "..."}]
    has_consent_or_legal_basis: bool,
    security_incident_active: bool,
    sensitive_tool_context: bool,
) -> PrivacyEligibilityResult:
    blocked_reasons = []
    reasons = []
    
    # Global checks
    if not has_consent_or_legal_basis:
        blocked_reasons.append("No consent or legal basis")
    if security_incident_active:
        blocked_reasons.append("Security incident active")
    if sensitive_tool_context:
        blocked_reasons.append("Sensitive tool context detected")
    if data_classification not in allowed_classifications:
        blocked_reasons.append(f"Classification {data_classification} blocked")
        
    privacy_decisions = {}
    
    for route in shadow_candidates:
        r_id = route["route_id"]
        r_provider = route["provider"]
        r_region = route["region"]
        
        provider_approved = r_provider in approved_providers
        region_allowed = r_region in allowed_regions
        classification_allowed = data_classification in allowed_classifications
        
        decision = PrivacyDecision(
            provider_approved=provider_approved,
            processing_region_allowed=region_allowed,
            data_classification_allowed=classification_allowed,
            legal_basis_present=has_consent_or_legal_basis
        )
        
        privacy_decisions[r_id] = decision
        
    shadow_allowed = (
        len(blocked_reasons) == 0 and 
        all(d.provider_approved and d.processing_region_allowed for d in privacy_decisions.values())
    )
    
    return PrivacyEligibilityResult(
        shadow_allowed=shadow_allowed,
        reasons=reasons,
        blocked_reasons=blocked_reasons,
        data_classification=data_classification,
        region=region,
        privacy_decisions=privacy_decisions
    )
