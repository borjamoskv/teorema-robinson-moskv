# C5-REAL EXERGY CERTIFIED
"""
Beer Viable System Model (VSM) Analyzer Primitive (Ring-1 / C5-REAL)
Implementa la arquitectura recursiva de viabilidad de Stafford Beer (1972)
y diagnóstico de patologías estructurales organizacionales.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Any

class VsmSystemId(Enum):
    SYSTEM_1_OPERATIONS = "SYSTEM_1_OPERATIONS"
    SYSTEM_2_COORDINATION = "SYSTEM_2_COORDINATION"
    SYSTEM_3_CONTROL_SYNERGY = "SYSTEM_3_CONTROL_SYNERGY"
    SYSTEM_3_STAR_AUDIT = "SYSTEM_3_STAR_AUDIT"
    SYSTEM_4_INTELLIGENCE = "SYSTEM_4_INTELLIGENCE"
    SYSTEM_5_POLICY = "SYSTEM_5_POLICY"

class VsmPathology(Enum):
    RACE_CONDITION_OSCILLATION = "RACE_CONDITION_OSCILLATION"  # Falta S2
    UNVERIFIED_REPORTING_BLINDNESS = "UNVERIFIED_REPORTING_BLINDNESS"  # Falta S3*
    AUTISTIC_MYOPIA = "AUTISTIC_MYOPIA"  # Falta S4
    PURPOSE_COLLAPSE = "PURPOSE_COLLAPSE"  # Falta S5
    OPERATIONAL_IMPLOSION = "OPERATIONAL_IMPLOSION"  # Falta S1
    S3_S4_HOMEOSTATIC_DISCONNECT = "S3_S4_HOMEOSTATIC_DISCONNECT"  # Desconexión presente vs futuro

@dataclass
class VsmTopology:
    active_systems: Set[VsmSystemId] = field(default_factory=set)
    s3_s4_channel_connected: bool = True
    algedonic_channel_active: bool = True

@dataclass(frozen=True)
class VsmReport:
    is_viable: bool
    pathologies: List[VsmPathology]
    active_systems_count: int
    algedonic_bypass_ready: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_viable": self.is_viable,
            "pathologies": [p.value for p in self.pathologies],
            "active_systems_count": self.active_systems_count,
            "algedonic_bypass_ready": self.algedonic_bypass_ready
        }

class BeerVsmAnalyzer:
    """
    Analizador formal de viabilidad recursiva según el Viable System Model de Stafford Beer.
    Verifica que la topología de un agente o sistema posea los 5 subsistemas y sus canales auditores.
    """

    @staticmethod
    def audit_topology(topology: VsmTopology) -> VsmReport:
        pathologies: List[VsmPathology] = []
        active = topology.active_systems

        if VsmSystemId.SYSTEM_1_OPERATIONS not in active:
            pathologies.append(VsmPathology.OPERATIONAL_IMPLOSION)

        if VsmSystemId.SYSTEM_2_COORDINATION not in active:
            pathologies.append(VsmPathology.RACE_CONDITION_OSCILLATION)

        if VsmSystemId.SYSTEM_3_CONTROL_SYNERGY not in active:
            # Si no hay S3, S1 no tiene regulación interna
            pathologies.append(VsmPathology.OPERATIONAL_IMPLOSION)

        if VsmSystemId.SYSTEM_3_STAR_AUDIT not in active:
            pathologies.append(VsmPathology.UNVERIFIED_REPORTING_BLINDNESS)

        if VsmSystemId.SYSTEM_4_INTELLIGENCE not in active:
            pathologies.append(VsmPathology.AUTISTIC_MYOPIA)

        if VsmSystemId.SYSTEM_5_POLICY not in active:
            pathologies.append(VsmPathology.PURPOSE_COLLAPSE)

        if VsmSystemId.SYSTEM_3_CONTROL_SYNERGY in active and VsmSystemId.SYSTEM_4_INTELLIGENCE in active:
            if not topology.s3_s4_channel_connected:
                pathologies.append(VsmPathology.S3_S4_HOMEOSTATIC_DISCONNECT)

        is_viable = (len(pathologies) == 0 and topology.algedonic_channel_active)

        return VsmReport(
            is_viable=is_viable,
            pathologies=pathologies,
            active_systems_count=len(active),
            algedonic_bypass_ready=topology.algedonic_channel_active
        )
