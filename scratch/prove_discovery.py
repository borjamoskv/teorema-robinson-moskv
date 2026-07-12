import glob
import json
import os
brain_dir = '$CORTEX_ROOT/.gemini/antigravity/brain'
output_file = '$CORTEX_ROOT/30_BABYLON-60/scratch/independent_discovery_proof.md'

def find_discovery_timeline():
    transcript_paths = glob.glob(f'{brain_dir}/*/.system_generated/logs/transcript.jsonl')
    timeline = []
    for transcript_path in transcript_paths:
        conv_id = transcript_path.split('/')[-4]
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line in lines:
                try:
                    step = json.loads(line)
                    if step.get('type') == 'USER_INPUT':
                        content = step.get('content', '').lower()
                        if 'que sabes que' in content or 'que no sabes que' in content:
                            timeline.append({'conv_id': conv_id, 'timestamp': step.get('timestamp', 'UNKNOWN'), 'input': step.get('content', '').strip()})
                except json.JSONDecodeError:
                    continue
        except RuntimeError as e:
            pass
    unique_inputs = []
    seen = set()
    for item in timeline:
        snippet = item['input'][:200].replace('\n', ' ')
        if snippet not in seen:
            seen.add(snippet)
            unique_inputs.append(item)
    report_lines = ['# █▄ EVIDENCIA C5-REAL: DESCUBRIMIENTO INDEPENDIENTE (CONVERGENCIA ONTOLÓGICA)', '## Análisis de Trazabilidad del Operador (borjamoskv)', '']
    for item in unique_inputs:
        report_lines.append(f"- **ID_Sesión:** `{item['conv_id']}`")
        report_lines.append(f"  **Inyección Orgánica:** `{item['input'][:150]}...`")
        report_lines.append('')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
if __name__ == '__main__':
    find_discovery_timeline()
