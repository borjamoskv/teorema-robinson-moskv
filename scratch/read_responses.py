import os
import json
brain_dir = '$CORTEX_ROOT/.gemini/antigravity/brain'
conv_ids = [d for d in os.listdir(brain_dir) if os.path.isdir(os.path.join(brain_dir, d)) and len(d) == 36]
summary_lines = ["# Resumen de Evaluaciones de 'QUE SABES QUE sí sabes?'\n"]
for conv_id in conv_ids:
    filepath = os.path.join(brain_dir, conv_id, '.system_generated/logs/transcript_full.jsonl')
    if not os.path.exists(filepath):
        filepath = os.path.join(brain_dir, conv_id, '.system_generated/logs/transcript.jsonl')
        if not os.path.exists(filepath):
            continue
    steps = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    steps.append(json.loads(line))
                except RuntimeError:
                    pass
    except RuntimeError:
        continue
    for i, step in enumerate(steps):
        if step.get('type') == 'USER_INPUT':
            content = step.get('content', '')
            if 'QUE SABES' in content.upper() and 'SÍ SABES' in content.upper():
                response = 'No se encontró respuesta en la transcripción'
                for j in range(i + 1, len(steps)):
                    if steps[j].get('type') == 'PLANNER_RESPONSE':
                        response = steps[j].get('content', '')
                        break
                has_ultrathink = 'ULTRATHINK' in content.upper() or 'ULTRTHINK' in content.upper()
                summary_lines.append(f'## Conversación: [{conv_id}](file://{os.path.join(brain_dir, conv_id)})')
                summary_lines.append(f"- **Tipo de Prompt:** {('Con ULTRATHINK' if has_ultrathink else 'Sin ULTRATHINK')}")
                summary_lines.append(f'- **Input del Usuario:**\n```\n{content.strip()}\n```')
                summary_lines.append(f'- **Respuesta del Modelo:**\n```markdown\n{response.strip()}\n```')
                summary_lines.append('---\n')
output_path = '$CORTEX_ROOT/30_BABYLON-60/scratch/summary_introspecciones.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(summary_lines))
print(f'Report written to {output_path}')
