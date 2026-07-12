import os
import re

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    new_content = re.sub('except\\s+Exception\\s*:', 'except RuntimeError:', content)
    new_content = re.sub('except\\s+Exception\\s+as\\s+(\\w+)\\s*:', 'except RuntimeError as \\1:', new_content)
    new_content = re.sub('except\\s*:', 'except RuntimeError:', new_content)
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f'Patched {filepath}')
workspace = '$CORTEX_ROOT/30_BABYLON-60'
for root, _, files in os.walk(workspace):
    if '.venv' in root or '.git' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            process_file(os.path.join(root, file))
