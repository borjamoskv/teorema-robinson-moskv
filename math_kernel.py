def calculate_exergy(tokens: int, temperature: float) -> float:
    # Corrección C5-REAL: La exergía decrece dividiendo la base entrópica por la temperatura
    return (tokens * 100) / temperature

