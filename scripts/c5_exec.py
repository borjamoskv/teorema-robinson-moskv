import sys
import os
import hashlib

def saga_0_secret_quarantine(prompt):
    forbidden = ['sk-', 'ghp_', 'xoxb-']
    for f in forbidden:
        if f in prompt:
            raise ValueError('SAGA-0: Secret in text.')

def saga_1_anti_obfuscation(prompt):
    return prompt.replace('\u200b', '')

def main():
    prompt = sys.stdin.read()
    saga_0_secret_quarantine(prompt)
    prompt = saga_1_anti_obfuscation(prompt)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'ontology', 'c5_matriz_5_niveles.md')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        f.write('# COLAPSO C5-REAL: MATRIZ DE 5 NIVELES (EPI_08)\n')
        f.write('---\n')
        f.write('Claim: EPI_08 Calibration Matrix\n')
        f.write('Proof: { Base: "c5_exec_collapse", Range: [0, 5], Confidence: "C5-REAL" }\n')
        f.write('---\n\n')
        f.write(prompt)
    print(f'Colapso Termodinámico Completado: {os.path.abspath(out_path)}')
    print(f'Hash Causal: {hashlib.sha256(prompt.encode()).hexdigest()}')
if __name__ == '__main__':
    main()
