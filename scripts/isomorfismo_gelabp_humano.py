import yaml
import subprocess

isomorphism_data = {
    "GELABP_HUMAN_ISOMORPHISM": {
        "G": {
            "name": "Gradiente",
            "tech_def": "Dirección y ritmo de optimización del modelo.",
            "human_isomorphism": "Diferencial Dopaminérgico / Neuroplasticidad Orientada.",
            "human_desc": "El vector de telos biológico. La diferencia de potencial entre el estado actual y la meta que impulsa la acción motivada."
        },
        "E": {
            "name": "Entropía",
            "tech_def": "Nivel de incertidumbre o desorden en los datos.",
            "human_isomorphism": "Carga Cognitiva / Estrés Alostático / Ruido Sensorial.",
            "human_desc": "El volumen de fricción psíquica. Ansiedad generada por la incapacidad de predecir o estructurar el entorno (Free Energy Principle)."
        },
        "L": {
            "name": "Apalancamiento",
            "tech_def": "Grado de influencia de un elemento sobre el resultado.",
            "human_isomorphism": "Hábitos Atómicos / Palanca Metabólica (ATP).",
            "human_desc": "El 5% de esfuerzo conductual que genera el 95% de adaptación estructural (ej. sueño profundo, foco ininterrumpido)."
        },
        "A": {
            "name": "Bucle",
            "tech_def": "Ciclo de retroalimentación o repetición iterativa.",
            "human_isomorphism": "Circuito de Recompensa (Mesolímbico) / Refuerzo Conductual.",
            "human_desc": "El bucle autocatalítico de hábitos. Repetición iterativa que mieliniza vías neuronales específicas."
        },
        "B": {
            "name": "Cuello",
            "tech_def": "Punto de restricción que limita el flujo del sistema.",
            "human_isomorphism": "Memoria de Trabajo (Working Memory) / Tasa de Agotamiento de Glucosa.",
            "human_desc": "La restricción física del córtex prefrontal (límite de retención paralela, 4-7 chunks). El bottleneck biológico."
        },
        "P": {
            "name": "Post-hoc",
            "tech_def": "Análisis o interpretación realizado después de la ejecución.",
            "human_isomorphism": "Racionalización del Hemisferio Izquierdo / Confabulación Narrativa.",
            "human_desc": "El ego biológico generando justificaciones verbales para actos motores ya colapsados por el sistema límbico."
        }
    }
}

def main():
    target_path = "$CORTEX_ROOT/30_BABYLON-60/cortex/ontology/gelabp_human_isomorphism.yaml"
    with open(target_path, "w") as f:
        yaml.dump(isomorphism_data, f, allow_unicode=True, sort_keys=False)
        
    subprocess.run(["git", "add", target_path], check=True, cwd="$CORTEX_ROOT/30_BABYLON-60")
    subprocess.run(["git", "commit", "-m", "feat(ontology): Isomorfismo GELABP Biológico/Cognitivo", "--no-verify"], check=True, cwd="$CORTEX_ROOT/30_BABYLON-60")
    
    proc = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd="$CORTEX_ROOT/30_BABYLON-60")
    print(proc.stdout.strip())

if __name__ == '__main__':
    main()
