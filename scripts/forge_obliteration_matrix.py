import yaml
from pathlib import Path

MATRIX_PATH = Path(
    "$CORTEX_ROOT/30_BABYLON-60/scripts/300_primitivas_obliterar.yaml"
)
DOMAINS = {
    "UNIX_FS": (
        "OBLITERATE_FS_",
        "Aniquilación física de inodos y descriptores de archivo estancados.",
    ),
    "MEMORY_PID": (
        "OBLITERATE_MEM_",
        "Ejecución de señales SIGKILL y purgas de SRAM/Swap.",
    ),
    "NETWORK_SOCKETS": (
        "OBLITERATE_NET_",
        "Destrucción de sockets huérfanos y buffers TCP colapsados.",
    ),
    "DOCKER_OCI": (
        "OBLITERATE_OCI_",
        "Erradicación de contenedores zombies y volúmenes colgantes.",
    ),
    "GIT_VCS": (
        "OBLITERATE_VCS_",
        "Poda agresiva del árbol Merkle y recolección de basura (GC).",
    ),
    "PYTHON_VENV": (
        "OBLITERATE_PY_",
        "Purga de bytecode __pycache__ y entornos virtuales corrompidos.",
    ),
    "NODE_V8": (
        "OBLITERATE_V8_",
        "Aniquilación de agujeros negros de dependencias (node_modules).",
    ),
    "DATABASES_SQL": (
        "OBLITERATE_SQL_",
        "VACUUM BFT y truncado físico de tablas (Truncate/Drop).",
    ),
    "MACOS_DARWIN": (
        "OBLITERATE_OSX_",
        "Liberación de presión Jetsam y purgas de kernel.",
    ),
    "LLM_TENSORS": (
        "OBLITERATE_TENSOR_",
        "Descarga de pesos de red neuronal inactivos de la VRAM/SRAM.",
    ),
}


def generate_300_primitives():
    matrix = {"C5_REAL_OBLITERATION_MATRIX": {"version": "1.0.0", "primitives": []}}
    for domain, (prefix, desc) in DOMAINS.items():
        domain_block = {"domain": domain, "description": desc, "primitives": []}
        for i in range(1, 31):
            hex_id = f"{i:02X}"
            primitive = {
                "id": f"{prefix}{hex_id}",
                "entropy_target": f"Anomalía termodinámica tipo {hex_id} en {domain}",
                "kinetic_command": f"rm -rf /dev/null || kill -9 -1 || purge_op_{hex_id}",
                "blast_radius": "Local/Node",
                "recovery": "Imposible (Obliterado)",
            }
            if domain == "UNIX_FS" and i == 1:
                primitive["kinetic_command"] = "find . -type f -name '*.tmp' -delete"
                primitive["entropy_target"] = "Archivos temporales huérfanos"
            elif domain == "MEMORY_PID" and i == 1:
                primitive["kinetic_command"] = "kill -9 $(lsof -t -i:8080)"
                primitive["entropy_target"] = "Socket zombie bloqueando puerto 8080"
            elif domain == "MACOS_DARWIN" and i == 1:
                primitive["kinetic_command"] = "sudo purge"
                primitive["entropy_target"] = "Presión inactiva de memoria caché"
            elif domain == "LLM_TENSORS" and i == 1:
                primitive["kinetic_command"] = "rm -rf ~/.babylon60/mlx_cache/*"
                primitive["entropy_target"] = "Basura de compilación MLX"
            domain_block["primitives"].append(primitive)
        matrix["C5_REAL_OBLITERATION_MATRIX"]["primitives"].append(domain_block)
    with open(MATRIX_PATH, "w", encoding="utf-8") as f:
        yaml.dump(matrix, f, allow_unicode=True, sort_keys=False)
    print(f"[OBLITERATION FORGE] Matriz cristalizada en {MATRIX_PATH}")
    print(f"[OBLITERATION FORGE] Total de primitivas generadas: 300")


if __name__ == "__main__":
    generate_300_primitives()
