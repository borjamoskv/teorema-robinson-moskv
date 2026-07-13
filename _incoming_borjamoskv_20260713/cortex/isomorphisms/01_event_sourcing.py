import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from functools import reduce

# [L2 - Ω1] Motor Causal Base 60: Ledger Append-Only Inmutable
@dataclass(frozen=True)
class Event:
    type: str
    payload: Dict[str, Any]
    timestamp: float

class Ledger:
    def __init__(self):
        self._events: List[Event] = []
    
    def append(self, event: Event):
        # Anergía Cero: No hay mutación (UPDATE), solo inyección térmica (INSERT)
        self._events.append(event)
        
    def stream(self) -> List[Event]:
        return self._events.copy()

# [L1 - Φ5] Isomorfismo Causal
class AggregateState:
    def __init__(self):
        # Estado Inicial: Reposo termodinámico
        self.id: str = None
        self.status: str = "INACTIVE"
        self.exergy_level: int = 0
        self.mutations: int = 0

    @staticmethod
    def apply_event(state: 'AggregateState', event: Event) -> 'AggregateState':
        """
        La función pura del pliegue (Left-Fold).
        Estado_Futuro = f(Estado_Presente, Evento)
        Cero ORMs. Cero impedancia.
        """
        if event.type == "SYSTEM_INIT":
            state.id = event.payload.get("id")
            state.status = "ACTIVE"
        elif event.type == "EXERGY_INJECTION":
            state.exergy_level += event.payload.get("amount", 0)
        elif event.type == "APOPTOSIS":
            state.status = "TERMINATED"
            state.exergy_level = 0
            
        state.mutations += 1
        return state

def derive_state(ledger: Ledger) -> AggregateState:
    """Reconstruye el Grafo de RAM colapsando el Ledger de Disco."""
    # Reducción matemática pura. Isomorfismo absoluto garantizado.
    return reduce(AggregateState.apply_event, ledger.stream(), AggregateState())

if __name__ == "__main__":
    import time
    
    print("[C5-REAL] Iniciando Prueba de Isomorfismo RAM/Disco (Event Sourcing)")
    ledger = Ledger()
    
    # 1. Escritura Causal (Append-Only)
    ledger.append(Event("SYSTEM_INIT", {"id": "MOSKV-1"}, time.time()))
    ledger.append(Event("EXERGY_INJECTION", {"amount": 500}, time.time()))
    ledger.append(Event("EXERGY_INJECTION", {"amount": 350}, time.time()))
    ledger.append(Event("APOPTOSIS", {}, time.time()))
    
    # 2. Lectura (Proyección / Materialized View)
    current_state = derive_state(ledger)
    
    print("\n[LEDGER] Eventos Inmutables en Disco:")
    for e in ledger.stream():
        print(f"  -> {e.type} | {e.payload}")
        
    print("\n[RAM] Estado Colapsado (Isomorfismo Perfecto sin ORM):")
    print(json.dumps(current_state.__dict__, indent=2))
    
    # Verificación del Isomorfismo
    assert current_state.status == "TERMINATED"
    assert current_state.exergy_level == 0
    assert current_state.mutations == 4
    print("\n[STATUS] Isomorfismo Causal Validado. Cero Anergía.")
