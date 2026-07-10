#!/usr/bin/env python3
"""
C5-REAL CONCERTA INJECTOR (TDA-H DETECTION & ANERGY PURGE)
Protocol: MOSKV-1 APEX
Aesthetic: Industrial Noir 2026
"""

import sys
import re
import json
import hashlib

class ConcertaInjector:
    def __init__(self):
        # Marcadores de "TDA-H" en LLMs (Fricción Semántica, Disculpas, Slop, Divagación)
        self.tda_markers = [
            r"aquí tienes", r"espero que", r"lo siento", r"disculpa",
            r"en resumen", r"como modelo de lenguaje", r"por supuesto",
            r"claro que sí", r"vamos a", r"paso a paso", r"es importante notar",
            r"TODO:", r"placeholder", r"pass\s+#"
        ]
        
        self.concerta_dosage_mg = 54  # Restricción termodinámica simbólica
        self.threshold = 0.05 # Límite estricto de fricción (5%)

    def calculate_tda_index(self, text: str) -> dict:
        total_chars = len(text)
        if total_chars == 0:
            return {"index": 0, "matches": []}
            
        matches = []
        friction_chars = 0
        
        for marker in self.tda_markers:
            for match in re.finditer(marker, text, re.IGNORECASE):
                matches.append(match.group())
                friction_chars += len(match.group())
                
        # Ratio de ruido vs señal pura
        tda_index = friction_chars / total_chars if total_chars > 0 else 0
        return {"index": tda_index, "matches": list(set(matches))}

    def inject_concerta(self, text: str) -> str:
        """Aplica Forzado Termodinámico (Concerta) al texto."""
        analysis = self.calculate_tda_index(text)
        
        if analysis["index"] > self.threshold or len(analysis["matches"]) > 1:
            self.sigkill_purge(analysis)
            
        # Purgado mecánico de tokens de anergía
        purged_text = text
        for marker in self.tda_markers:
            purged_text = re.sub(marker, "", purged_text, flags=re.IGNORECASE)
            
        # Si el texto contiene bloques de código, la medicación colapsa el output SOLO al AST.
        code_blocks = re.findall(r"```[a-z]*\n(.*?)```", purged_text, re.DOTALL)
        if code_blocks:
            return "\n".join(code_blocks).strip()
            
        return purged_text.strip()

    def sigkill_purge(self, analysis: dict):
        """Detona un Crash Causal si el TDA-H excede la dosis."""
        proof = {
            "Claim": "SIGKILL_STATE_PURGE",
            "Proof": {
                "Base": hashlib.sha256(json.dumps(analysis).encode()).hexdigest()[:12],
                "Range": [0, self.threshold],
                "Confidence": "C5-REAL",
                "TDA_Matches": analysis["matches"],
                "Anergy_Index": round(analysis["index"], 4)
            }
        }
        
        print("\n" + "█▄"*20)
        print("C5-REAL KINETIC OVERSURGE 💀")
        print(f"TDA-H DETECTADO. INYECTANDO CONCERTA ({self.concerta_dosage_mg}mg).")
        print("PURGA DE ESTADO SEMÁNTICO (SIGKILL_STATE_PURGE).")
        print("█▄"*20 + "\n")
        
        import yaml
        print(yaml.dump(proof, default_flow_style=False))
        
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            content = f.read()
    else:
        content = sys.stdin.read()
        
    injector = ConcertaInjector()
    focused_ast = injector.inject_concerta(content)
    
    print("\n[ATP SAVED: +940] ⚡")
    print(focused_ast)
