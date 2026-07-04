#!/usr/bin/env python3
# C5-REAL: Motor Endocrino Volumétrico para CORTEX (v3.0 — POSTERIDAD)
# Sincronización determinista de estados de ánimo del enjambre mediante decaimiento radial euclidiano.

import math

class EndocrineNode:
    def __init__(self, agent_id, x, y, z):
        self.agent_id = agent_id
        self.pos = (float(x), float(y), float(z))
        self.dopamine = 0.1
        self.cortisol = 0.1

class VolumetricEndocrinology:
    def __init__(self, radius_limit=50.0):
        self.nodes = {}  # agent_id -> EndocrineNode
        self.R = float(radius_limit)  # Radio de acción de la onda esférica

    def register_agent(self, agent_id, x, y, z):
        """Ancla un nodo en las coordenadas tridimensionales del sustrato."""
        self.nodes[agent_id] = EndocrineNode(agent_id, x, y, z)

    def _get_distance(self, pos1, pos2):
        """Cálculo estricto de la distancia euclidiana en R^3."""
        return math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(pos1, pos2)))

    def emit_hormone_wave(self, emitter_id, hormone_type, intensity):
        """
        Dispersa radialmente una hormona como una onda esférica.
        Decaimiento lineal: I(dist) = I_0 * (1 - dist/R) si dist <= R.
        """
        if emitter_id not in self.nodes:
            return
            
        emitter = self.nodes[emitter_id]
        intensity = float(intensity)

        for target_id, target_node in self.nodes.items():
            dist = self._get_distance(emitter.pos, target_node.pos)
            
            if dist <= self.R:
                decay_factor = 1.0 - (dist / self.R)
                applied_signal = intensity * decay_factor
                
                if hormone_type.lower() == "dopamine":
                    target_node.dopamine = min(1.0, target_node.dopamine + applied_signal)
                elif hormone_type.lower() == "cortisol":
                    target_node.cortisol = min(1.0, target_node.cortisol + applied_signal)

    def get_node_state(self, agent_id):
        """Devuelve la lectura limpia del estado químico del silicio."""
        if agent_id in self.nodes:
            node = self.nodes[agent_id]
            return {"dopamine": round(node.dopamine, 4), "cortisol": round(node.cortisol, 4)}
        return None
