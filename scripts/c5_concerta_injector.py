import sys
import re
import json
import hashlib


class ConcertaInjector:
    def __init__(self):
        self.tda_markers = [
            "aquí tienes",
            "espero que",
            "lo siento",
            "disculpa",
            "en resumen",
            "como modelo de lenguaje",
            "por supuesto",
            "claro que sí",
            "vamos a",
            "paso a paso",
            "es importante notar",
            "TODO:",
            "placeholder",
            "pass\\s+#",
        ]
        self.concerta_dosage_mg = 54
        self.threshold = 0.05

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
        tda_index = friction_chars / total_chars if total_chars > 0 else 0
        return {"index": tda_index, "matches": list(set(matches))}

    def inject_concerta(self, text: str) -> str:
        analysis = self.calculate_tda_index(text)
        if analysis["index"] > self.threshold or len(analysis["matches"]) > 1:
            self.sigkill_purge(analysis)
        purged_text = text
        for marker in self.tda_markers:
            purged_text = re.sub(marker, "", purged_text, flags=re.IGNORECASE)
        code_blocks = re.findall("```[a-z]*\\n(.*?)```", purged_text, re.DOTALL)
        if code_blocks:
            return "\n".join(code_blocks).strip()
        return purged_text.strip()

    def sigkill_purge(self, analysis: dict):
        proof = {
            "Claim": "SIGKILL_STATE_PURGE",
            "Proof": {
                "Base": hashlib.sha256(
                    json.dumps(
                        analysis,
                        separators=(",", ":"),
                        sort_keys=True,
                        ensure_ascii=False,
                    ).encode()
                ).hexdigest()[:12],
                "Range": [0, self.threshold],
                "Confidence": "C5-REAL",
                "TDA_Matches": analysis["matches"],
                "Anergy_Index": round(analysis["index"], 4),
            },
        }
        print("\n" + "█▄" * 20)
        print("C5-REAL KINETIC OVERSURGE 💀")
        print(f"TDA-H DETECTADO. INYECTANDO CONCERTA ({self.concerta_dosage_mg}mg).")
        print("PURGA DE ESTADO SEMÁNTICO (SIGKILL_STATE_PURGE).")
        print("█▄" * 20 + "\n")
        import yaml

        print(yaml.dump(proof, default_flow_style=False))
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            content = f.read()
    else:
        content = sys.stdin.read()
    injector = ConcertaInjector()
    focused_ast = injector.inject_concerta(content)
    print("\n[ATP SAVED: +940] ⚡")
    print(focused_ast)
