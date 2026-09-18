# C5-REAL EXERGY CERTIFIED
"""
CAM-5.0 (C5 Abstract Effect Observation Machine) Package.
"""

from scitt_python.aem.isa import (
    Handle,
    InstructionFamily,
    ExecutionError,
    CapabilityError,
    IntegrityError,
    ImplementationError,
)
from scitt_python.aem.effects import AlgebraicEffect, EffectProgram, CapabilitySet
from scitt_python.aem.space import ObjectSpace
from scitt_python.aem.machine import AbstractEffectMachine

__all__ = [
    "Handle",
    "InstructionFamily",
    "ExecutionError",
    "CapabilityError",
    "IntegrityError",
    "ImplementationError",
    "AlgebraicEffect",
    "EffectProgram",
    "CapabilitySet",
    "ObjectSpace",
    "AbstractEffectMachine",
]
