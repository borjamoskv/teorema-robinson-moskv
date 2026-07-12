import os
import yaml
import hashlib

def purge_primitives():
    file_path = '$CORTEX_ROOT/30_BABYLON-60/cortex/ontology/300_primitivas_post_hoc.yaml'
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    initial_count = len(data.get('primitives', []))
    new_primitives = []
    for p in data.get('primitives', []):
        id_str = p['id'].split('-')[-1]
        if int(id_str) >= 121:
            new_primitives.append(p)
    data['primitives'] = new_primitives
    final_count = len(new_primitives)
    with open(file_path, 'w') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    with open(file_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    print(f'Purga completa: {initial_count} -> {final_count} primitivas.')
    print(f'Hash: {file_hash}')
if __name__ == '__main__':
    purge_primitives()
