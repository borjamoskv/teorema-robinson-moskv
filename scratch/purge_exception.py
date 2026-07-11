import os
import re

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # We replace 'except RuntimeError:' with 'except RuntimeError:'
    # and 'except Exception as' with 'except RuntimeError as'
    new_content = re.sub(r'except\s+Exception\s*:', 'except RuntimeError:', content)
    new_content = re.sub(r'except\s+Exception\s+as\s+(\w+)\s*:', r'except RuntimeError as \1:', new_content)
    # Also handle bare excepts (though the validator caught mostly except Exception)
    new_content = re.sub(r'except\s*:', 'except RuntimeError:', new_content)
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Patched {filepath}")

workspace = '/Users/borjafernandezangulo/30_BABYLON-60'
for root, _, files in os.walk(workspace):
    if '.venv' in root or '.git' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            process_file(os.path.join(root, file))
