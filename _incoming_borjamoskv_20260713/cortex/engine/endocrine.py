# C5-REAL: Motor Endocrino Volumétrico para CORTEX (v3.0 — POSTERIDAD)
import math

class EndocrineNode:
    agent_id: str
    pos: tuple[float, float, float]
    dopamine: float
    cortisol: float

    def __init__(self, agent_id: str, x: float, y: float, z: float) -> None:
        self.agent_id: str = agent_id
        self.pos: tuple[float, float, float] = (float(x), float(y), float(z))
        self.dopamine: float = 0.1
        self.cortisol: float = 0.1

class VolumetricEndocrinology:
    nodes: dict[str, EndocrineNode]
    R: float

    def __init__(self, radius_limit: float = 50.0) -> None:
        self.nodes: dict[str, EndocrineNode] = {}
        self.R: float = float(radius_limit)

    def register_agent(self, agent_id: str, x: float, y: float, z: float) -> None:
        assert isinstance(agent_id, str), "ID de agente debe ser string"
        self.nodes[agent_id] = EndocrineNode(agent_id, x, y, z)

    def _get_distance(self, pos1: tuple[float, float, float], pos2: tuple[float, float, float]) -> float:
        assert len(pos1) == 3, "Coordenadas de origen deben ser tridimensionales"
        assert len(pos2) == 3, "Coordenadas de destino deben ser tridimensionales"
        return math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(pos1, pos2)))

    def emit_hormone_wave(self, emitter_id: str, hormone_type: str, intensity: float) -> None:
        assert isinstance(emitter_id, str), "ID de emisor debe ser string"
        assert isinstance(hormone_type, str), "Tipo de hormona debe ser string"
        if emitter_id not in self.nodes:
            return
            
        emitter: EndocrineNode = self.nodes[emitter_id]
        intensity_val: float = float(intensity)

        for target_id, target_node in self.nodes.items():
            dist: float = self._get_distance(emitter.pos, target_node.pos)
            
            if dist <= self.R:
                decay_factor: float = 1.0 - (dist / self.R)
                applied_signal: float = intensity_val * decay_factor
                
                if hormone_type.lower() == "dopamine":
                    target_node.dopamine = min(1.0, target_node.dopamine + applied_signal)
                elif hormone_type.lower() == "cortisol":
                    target_node.cortisol = min(1.0, target_node.cortisol + applied_signal)

    def get_node_state(self, agent_id: str) -> dict[str, float] | None:
        assert isinstance(agent_id, str), "ID de agente debe ser string"
        if agent_id in self.nodes:
            node: EndocrineNode = self.nodes[agent_id]
            res: dict[str, float] = {"dopamine": round(node.dopamine, 4), "cortisol": round(node.cortisol, 4)}
            return res
        return None
