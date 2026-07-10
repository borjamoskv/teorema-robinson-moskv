import hashlib
from dataclasses import dataclass

@dataclass
class UtilitySpec:
    """Defines how utility is measured uniformly across primary and shadows."""
    spec_id: str
    version: str
    scale_min: float
    scale_max: float
    criteria: str
    judge_prompt_template: str

    @property
    def hash(self) -> str:
        payload = f"{self.spec_id}|{self.version}|{self.scale_min}|{self.scale_max}|{self.criteria}|{self.judge_prompt_template}"
        return hashlib.sha256(payload.encode()).hexdigest()
