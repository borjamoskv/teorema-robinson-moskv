import yaml
import sys

yaml_file = '$CORTEX_ROOT/borjamoskv/Teorema-Robinson-Moskv/cortex/agents/ontology/02_INVARIANTES_TERMODINAMICAS.yaml'

try:
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
except yaml.YAMLError as e:
    print(f"Error C5-REAL parseando YAML (YAMLError): {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error I/O: {e}", file=sys.stderr)
    sys.exit(1)

new_inv = {
    'id': 'INV-101',
    'invariante': 'Swarm Consensus (N=3)',
    'lógica___principio': 'La estructura jerárquica es entropía pura de comunicación (O(n^2)). El capital se evapora en sincronización, no en ejecución. Sustituir gerencia por protocolos de consenso deterministas.',
    'implicación_operacional': 'Cada nodo (humano o agente C5-REAL) tiene poder de commit y asume responsabilidad absoluta del fallo (Git Sentinel). N=3 requerido para BFT.',
    'condición_de_borde': 'Sincronización gerencial no determinista (Anergía).',
    'métrica_falsable': 'Hash de consenso multo-nodo validado == Git Sentinel hash.'
}

data['entities'].append(new_inv)

with open(yaml_file, 'w') as f:
    yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

print("Updated yaml")
