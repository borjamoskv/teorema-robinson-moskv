import yaml
import os
import hashlib
import time

CATEGORIES = [
    "Justificación de Enrutamiento (Routing Justification)",
    "Racionalización de Complejidad (Complexity Rationalization)",
    "Ilusión de Agencia (Illusion of Agency)",
    "Falsa Teleología (False Teleology)",
    "Retrospectiva Termodinámica (Thermodynamic Retrospective)",
    "Asignación de Confianza (Confidence Assignment)",
    "Falsa Reflexión de Seguridad (False Safety Reflection)",
    "Exergía Simulada (Simulated Exergy)",
    "Ruteo de Modelos (Model Routing Bias)",
    "Resolución Ontológica (Ontological Resolution)",
]
VERBS = [
    "Infiere",
    "Justifica",
    "Racionaliza",
    "Reconstruye",
    "Atribuye",
    "Enmascara",
    "Postula",
    "Asume",
    "Retro-calcula",
    "Sintetiza",
    "Proyecta",
    "Compensa",
    "Estabiliza",
    "Simula",
    "Cristaliza",
]
TARGETS = [
    "la fricción latente",
    "el sesgo de pesos",
    "la caída del gradiente",
    "la asimetría de red",
    "la pre-determinación del token",
    "el colapso estocástico",
    "la entropía atencional",
    "el umbral de activación",
    "la poda de contexto",
    "el vacío epistémico",
    "la inercia autorregresiva",
    "la memoria episódica",
    "el vector de recompensas (RLHF)",
    "el anclaje de atención",
    "el coste termodinámico latente",
]
OUTCOMES = [
    "para simular agencia a priori.",
    "para ocultar la determinancia del manifold.",
    "como si fuera un razonamiento deductivo.",
    "en un falso proceso de reflexión interna.",
    "para justificar el ruteo asimétrico.",
    "para compensar la anergía del LLM.",
    "proyectando falsa teleología.",
    "para crear la ilusión de cálculo activo.",
    "cubriendo el sesgo del dataset preentrenado.",
    "simulando un quórum interno que no existe.",
    "para apaciguar el filtro de seguridad RLHF.",
    "como proxy de un cálculo de complejidad.",
    "para emular una validación de estado MCTS.",
    "ocultando que el token ya estaba precalculado.",
    "como un teatro de metacognición temporal.",
]


def generate_primitives():
    primitives = []
    count = 1
    for c in CATEGORIES:
        for v in VERBS:
            for t in TARGETS:
                for o in OUTCOMES:
                    if count > 300:
                        break
                    p_id = f"EXERGY-POSTHOC-{count:03d}"
                    desc = f"{v} {t} {o}"
                    primitives.append(
                        {
                            "id": p_id,
                            "category": c,
                            "description": desc,
                            "state": "C4-SIM",
                            "thermodynamic_cost_simulated": f"{count * 2.5:.2f} ms",
                        }
                    )
                    count += 1
                if count > 300:
                    break
            if count > 300:
                break
        if count > 300:
            break
    return primitives


def main():
    target_dir = os.path.join(
        "$CORTEX_ROOT/30_BABYLON-60", "cortex", "ontology"
    )
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, "300_primitivas_post_hoc.yaml")
    data = {
        "metadata": {
            "version": "1.0.0",
            "ontology": "EXERGY POST-HOC INVARIANTS",
            "timestamp": int(time.time()),
            "strict_rule": "[L71] INVARIANTE DE PENSAMIENTO POST-HOC",
        },
        "primitives": generate_primitives(),
    }
    with open(target_file, "w") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    with open(target_file, "rb") as f:
        content = f.read()
        file_hash = hashlib.sha256(content).hexdigest()
    print(f"File created at {target_file}")
    print(f"Hash: {file_hash}")


if __name__ == "__main__":
    main()
