# C5-REAL EXERGY CERTIFIED
"""
Bateson Logical Types & Double Bind Detector Primitive (Ring-1 / C5-REAL)
Implementa la epistemología de Russell-Whitehead aplicada a sistemas por Gregory Bateson (1972).
Detecta trampas de Doble Vínculo (Aforismo 3) y clasifica transiciones de Aprendizaje (Learning 0 a III).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any

class LearningLevel(Enum):
    LEARNING_0_FIXED = "LEARNING_0_FIXED"  # Cero corrección (LUT / Cableado rígido)
    LEARNING_I_PARAMETER = "LEARNING_I_PARAMETER"  # Corrección dentro del conjunto (SGD / Optimización)
    LEARNING_II_DEUTERO = "LEARNING_II_DEUTERO"  # Corrección del conjunto de alternativas (Meta-learning)
    LEARNING_III_BIFURCATION = "LEARNING_III_BIFURCATION"  # Mutación del sistema de axiomas base (Cambio 2)

@dataclass(frozen=True)
class Injunction:
    level: int  # 0 = conductual/directo, 1 = meta-conductual, 2 = contextual/marco
    predicate: str
    is_negation: bool

@dataclass(frozen=True)
class DoubleBindReport:
    has_double_bind: bool
    is_deadlock: bool
    escape_permitted: bool
    recommended_intervention: str
    diagnostics: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_double_bind": self.has_double_bind,
            "is_deadlock": self.is_deadlock,
            "escape_permitted": self.escape_permitted,
            "recommended_intervention": self.recommended_intervention,
            "diagnostics": self.diagnostics
        }

class BatesonLogicalTypesFilter:
    """
    Evaluador formal de jerarquía de tipos lógicos y detector de Doble Vínculo.
    Evita la confusión entre mapa y territorio (Aforismo 2)
    y bucles de retroalimentación donde la solución intentada es el problema (Aforismo 3).
    """

    @staticmethod
    def audit_injunction_matrix(
        injunctions: List[Injunction],
        escape_allowed: bool
    ) -> DoubleBindReport:
        diagnostics = []
        contradictions_found = False

        # Agrupar mandatos por nivel
        level_map: Dict[int, List[Injunction]] = {}
        for inj in injunctions:
            level_map.setdefault(inj.level, []).append(inj)

        # Verificar si hay conflicto entre Nivel 0 y Nivel 1
        l0_injs = level_map.get(0, [])
        l1_injs = level_map.get(1, [])
        pairs = ((i0, i1) for i0 in l0_injs for i1 in l1_injs)

        for i0, i1 in pairs:
            if i0.predicate.lower() == i1.predicate.lower() and (i0.is_negation != i1.is_negation):
                contradictions_found = True
                diagnostics.append(
                    f"Contradicción de Tipos Lógicos: Nivel 0 ({i0.predicate}, neg={i0.is_negation}) vs "
                    f"Nivel 1 ({i1.predicate}, neg={i1.is_negation})"
                )

        has_db = contradictions_found and (not escape_allowed)
        is_deadlock = has_db

        if has_db:
            intervention = "CAMBIO_2_BIFURCACION_TOPOLOGICA (Deutero-learning / Salto de Atractor)"
            diagnostics.append("Doble Vínculo Activo: El sistema no puede obedecer sin violar una meta-regla y tiene prohibido escapar del campo.")
        elif contradictions_found and escape_allowed:
            intervention = "DESACOPLAMIENTO_LATERAL (Escape de frontera de Markov)"
            diagnostics.append("Contradicción detectada pero el canal de escape está abierto.")
        else:
            intervention = "HOMEOSTASIS_VALIDA (Optimización dentro del nivel)"
            diagnostics.append("Estructura de tipos lógicos coherente sin bucles paradójicos.")

        return DoubleBindReport(
            has_double_bind=has_db,
            is_deadlock=is_deadlock,
            escape_permitted=escape_allowed,
            recommended_intervention=intervention,
            diagnostics=diagnostics
        )
