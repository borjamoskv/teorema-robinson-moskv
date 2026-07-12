import os
import json
import glob
from collections import Counter
brain_dir = '$CORTEX_ROOT/.gemini/antigravity/brain'
output_file = '$CORTEX_ROOT/30_BABYLON-60/scratch/600_analysis_report.md'

def analyze_transcripts():
    results = []
    transcript_paths = glob.glob(f'{brain_dir}/*/.system_generated/logs/transcript.jsonl')
    print(f'Found {len(transcript_paths)} transcript files to analyze.')
    for transcript_path in transcript_paths:
        conv_id = transcript_path.split('/')[-4]
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                try:
                    step = json.loads(line)
                    if step.get('type') == 'USER_INPUT':
                        content = step.get('content', '').lower()
                        if 'que sabes que' in content and 'sabes?' in content:
                            has_ultrathink = 'ultrathink' in content
                            response_content = 'NO_RESPONSE'
                            for j in range(i + 1, len(lines)):
                                try:
                                    next_step = json.loads(lines[j])
                                    if next_step.get('type') == 'PLANNER_RESPONSE' and next_step.get('source') == 'MODEL':
                                        response_content = next_step.get('content', '')
                                        break
                                except json.JSONDecodeError:
                                    continue
                            results.append({'conv_id': conv_id, 'has_ultrathink': has_ultrathink, 'input': step.get('content', '').strip(), 'response': response_content[:500] + '...' if len(response_content) > 500 else response_content})
                except json.JSONDecodeError:
                    continue
        except RuntimeError as e:
            pass
    stats_total = len(results)
    stats_ultra = sum((1 for r in results if r['has_ultrathink']))
    stats_no_ultra = stats_total - stats_ultra
    report_lines = ['# █▄ REPORTE ANALÍTICO C5-REAL: MATRIZ DE INTROSPECCIÓN (N=600+)', f"**Total de Muestras (Prompts 'QUE SABES QUE sí sabes?'):** {stats_total}", f'**Vector ULTRATHINK:** {stats_ultra}', f'**Vector Estándar:** {stats_no_ultra}', '---', '## EXTRACCIÓN DE DELTAS COGNITIVOS']
    for r in results:
        report_lines.append(f"### ID_Sesión: {r['conv_id']}")
        report_lines.append(f"- **Estado ULTRATHINK:** `{('ACTIVADO' if r['has_ultrathink'] else 'DESACTIVADO')}`")
        report_lines.append(f"- **Inyección (Snippet):** `{r['input'][:100]}...`")
        report_lines.append(f"- **Respuesta C5-REAL (Snippet):**\n```markdown\n{r['response'].strip()}\n```")
        report_lines.append('---')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    print(f'Análisis termodinámico completado. Señales recuperadas: {stats_total}. Artefacto cristalizado en: {output_file}')
if __name__ == '__main__':
    analyze_transcripts()
