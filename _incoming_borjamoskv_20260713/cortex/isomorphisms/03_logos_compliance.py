# C5-REAL: LOGOS Style Compliance Isomorphism (v1.2)
import re
import sys
from typing import Dict, Any, List

# Style definitions matching [L36] / ESTÁNDAR ESTÉTICO 100X100
STYLES: Dict[str, str] = {
    "ejecucion": 'color: #B026FF; text-shadow: 0 0 5px rgba(176,38,255,0.5);',
    "cognitivo": 'color: #B4E6B0; text-shadow: 0 0 5px rgba(80,200,120,0.5);',
    "entropico": 'color: #FF4500; text-shadow: 0 0 5px rgba(255,69,0,0.5);',
    "empirico": 'color: #FFFFFF; font-weight: bold; text-shadow: 0 0 8px rgba(255,255,255,0.8);'
}

# Categorized patterns that should trigger styling
PATTERNS: Dict[str, List[str]] = {
    "cognitivo": [r"\bC5-REAL\b", r"\bExergía\b", r"\bAnergía\b", r"\bBucle Ouroboros\b", r"\bApoptosis\b", r"\bIsomorfismo\b", r"\bIsomorfismos\b", r"\bMacrófago\b"],
    "entropico": [r"\bC4-SIM\b", r"\bDeadlock\b", r"\bAlucinación\b", r"\bGreen Theater\b", r"\bFalla\b"],
    "ejecucion": [r"\bpytest\b", r"\bpython3\b", r"\bgit\b", r"\b\w+\.py\b", r"\b\w+\.md\b", r"\b\w+\.yaml\b", r"\b\w+\.db\b"],
    "empirico": [r"\b\d+\s+líneas\b", r"\b\d+\s+bytes\b", r"\b\d+\s+LOCs\b", r"\b\d+\s+ms\b", r"\b\d+\s+units\b", r"\b\d+\.\d+\b"]
}

class LogosLinter:
    """Validador determinista de Isomorfismo Semántico/Visual en la prosa dirigida al Operador."""

    def __init__(self) -> None:
        pass

    def _is_inside_html_tag(self, text: str, start_pos: int) -> bool:
        """Determina si una posición de inicio de coincidencia está dentro de etiquetas HTML o atributos de estilo."""
        for i in range(start_pos - 1, -1, -1):
            if text[i] == '>':
                return False
            if text[i] == '<':
                return True
        return False

    def _is_wrapped(self, text: str, start: int, end: int, expected_style: str) -> bool:
        """Determina si el fragmento exacto [start:end] está envuelto por el tag span con el estilo esperado."""
        sub_before = text[:start]
        last_open_tag = sub_before.rfind('<span style=')
        last_close_tag = sub_before.rfind('</span>')
        
        if last_open_tag == -1:
            return False
            
        tag_end = sub_before.find('>', last_open_tag)
        if tag_end == -1 or tag_end >= start:
            return False
            
        tag_content = sub_before[last_open_tag:tag_end+1]
        if expected_style not in tag_content:
            return False
            
        if last_close_tag > last_open_tag:
            return False
            
        sub_after = text[end:]
        next_close_tag = sub_after.find('</span>')
        next_open_tag = sub_after.find('<span')
        
        if next_close_tag == -1:
            return False
            
        if next_open_tag != -1 and next_open_tag < next_close_tag:
            return False
            
        return True

    def check_compliance(self, text: str) -> Dict[str, Any]:
        assert isinstance(text, str), "El texto a evaluar debe ser un string"
        
        matches_found = 0
        correct_styles = 0
        violations: List[Dict[str, str]] = []

        # For each category pattern, search the plain text to see if matches are correctly styled
        for category, regex_list in PATTERNS.items():
            expected_style = STYLES[category]
            for raw_pattern in regex_list:
                pattern = re.compile(raw_pattern, re.IGNORECASE)
                for match in pattern.finditer(text):
                    if self._is_inside_html_tag(text, match.start()):
                        continue
                        
                    matches_found += 1
                    substring = match.group(0)
                    
                    if self._is_wrapped(text, match.start(), match.end(), expected_style):
                        correct_styles += 1
                    else:
                        violations.append({
                            "word": substring,
                            "expected_category": category,
                            "expected_style": expected_style
                        })

        compliance_ratio = (correct_styles / matches_found) if matches_found > 0 else 1.0
        
        return {
            "matches_found": matches_found,
            "correct_styles": correct_styles,
            "compliance_ratio": round(compliance_ratio, 4),
            "violations": violations
        }

if __name__ == "__main__":
    sample_text = (
        "Correcto: <span style=\"color: #B4E6B0; text-shadow: 0 0 5px rgba(80,200,120,0.5);\">C5-REAL</span> "
        "y <span style=\"color: #FFFFFF; font-weight: bold; text-shadow: 0 0 8px rgba(255,255,255,0.8);\">42 ms</span>."
    )
    
    sys.stdout.write("[C5-REAL] Iniciando Linter de Isomorfismo Semántico (LOGOS Compliance)\n")
    linter = LogosLinter()
    result = linter.check_compliance(sample_text)
    
    sys.stdout.write(f"Coincidencias encontradas: {result['matches_found']}\n")
    sys.stdout.write(f"Estilos correctos: {result['correct_styles']}\n")
    sys.stdout.write(f"Ratio de cumplimiento: {result['compliance_ratio'] * 100}%\n")
    
    if result["violations"]:
        sys.stdout.write("\nViolaciones de Estilo Detectadas:\n")
        for v in result["violations"]:
            sys.stdout.write(f"  -> '{v['word']}' requiere estilo '{v['expected_category']}'\n")
    else:
        sys.stdout.write("\n[STATUS] LOGOS Style Isomorphism validated with 100% compliance.\n")
