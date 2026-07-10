import pytest
import json
from dataclasses import dataclass
from typing import Optional

@dataclass
class EvaluationReceipt:
    quality_proxy_basis_points: int
    utility_basis_points: int
    observed_proxy_regret_basis_points: int
    evaluator_hash: str
    utility_spec_hash: str

@dataclass
class AggregateEvaluationReport:
    cohort_id: str
    metric: str
    estimate_basis_points: float
    confidence_interval_95_basis_points: list
    sample_size: int
    estimator: str

def test_evaluation_receipt_has_no_confidence_interval():
    """
    EvaluationReceipt (individual) should NOT have confidence intervals.
    """
    receipt = EvaluationReceipt(
        quality_proxy_basis_points=8900,
        utility_basis_points=8300,
        observed_proxy_regret_basis_points=120,
        evaluator_hash="sha256:...",
        utility_spec_hash="sha256:..."
    )
    
    assert not hasattr(receipt, 'confidence_interval_95_basis_points')
    assert not hasattr(receipt, 'sample_size')
    
    json_str = json.dumps(receipt.__dict__)
    assert "confidence_interval" not in json_str
    assert "sample_size" not in json_str

def test_aggregate_report_has_confidence_interval():
    """
    AggregateEvaluationReport SHOULD have confidence intervals.
    """
    report = AggregateEvaluationReport(
        cohort_id="coding-us-east-2026-w28",
        metric="mean_observed_proxy_regret",
        estimate_basis_points=120,
        confidence_interval_95_basis_points=[80, 160],
        sample_size=12480,
        estimator="hajek_weighted_paired_difference"
    )
    
    assert hasattr(report, 'confidence_interval_95_basis_points')
    assert report.sample_size == 12480
    
    json_str = json.dumps(report.__dict__)
    assert "confidence_interval_95_basis_points" in json_str
    assert "sample_size" in json_str
