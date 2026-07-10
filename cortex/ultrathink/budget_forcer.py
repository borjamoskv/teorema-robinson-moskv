# C5-REAL
from typing import Optional

class ApoptosisException(Exception):
    """
    Excepción física disparada al exceder los límites termodinámicos de inferencia.
    Obliga al colapso del árbol de búsqueda (MCTS).
    """
    pass

class UltraThinkBudgetForcer:
    """
    Impone un límite termodinámico estricto (Halting Limit) a ciclos iterativos.
    """
    def __init__(self, max_iterations: int, max_tokens: int):
        self.max_iterations = max_iterations
        self.max_tokens = max_tokens
        self.current_iterations = 0
        self.current_tokens = 0

    def tick(self, tokens: int = 0) -> None:
        """
        Registra el consumo de entropía y fuerza la Apoptosis si se excede el presupuesto.
        """
        self.current_iterations += 1
        self.current_tokens += tokens
        
        if self.current_iterations > self.max_iterations:
            raise ApoptosisException(
                f"Apoptosis: Límite iterativo excedido ({self.current_iterations}/{self.max_iterations})."
            )
            
        if self.current_tokens > self.max_tokens:
            raise ApoptosisException(
                f"Apoptosis: Presupuesto de tokens excedido ({self.current_tokens}/{self.max_tokens})."
            )
