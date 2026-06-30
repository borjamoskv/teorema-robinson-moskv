import os
import re
import glob

DIR = "$CORTEX_ROOT/borjamoskv/Teorema-Robinson-Moskv/cortex/agents/ontology"

def get_ids(content):
    table_declarations = re.findall(r"\|\s*([A-Z]+(?:-CAT)?-\d{3})\s*\|", content)
    list_declarations = re.findall(r"\*\s*\*\*\[([A-Z]+(?:-CAT)?-\d{3})\]\*\*", content)
    return set(table_declarations + list_declarations) - {"ID"}

# 1. Map Master files
master_files = {
    "PRIM": "01_PRIMITIVAS_DE_COLAPSO.md",
    "INV": "02_INVARIANTES_TERMODINAMICAS.md",
    "ANTI": "03_ANTIPATRONES_ESTOCASTICOS.md",
    "RED": "04_REDUNDANCIAS_ACTIVAS.md",
    "VEC": "05_VECTORES_ADVERSARIALES.md"
}

master_ids = set()
for m in master_files.values():
    path = os.path.join(DIR, m)
    if os.path.exists(path):
        with open(path, "r") as f:
            master_ids.update(get_ids(f.read()))

# 2. Process Batches
for batch_file in glob.glob(os.path.join(DIR, "batch_*.md")):
    with open(batch_file, "r") as f:
        content = f.read()
    b_ids = get_ids(content)
    
    # Are there new IDs?
    new_ids = b_ids - master_ids
    if new_ids:
        # Find which master it belongs to based on the prefix of the first new ID
        prefix = list(new_ids)[0].split('-')[0]
        if prefix in master_files:
            m_path = os.path.join(DIR, master_files[prefix])
            print(f"Appending new IDs from {os.path.basename(batch_file)} to {master_files[prefix]}")
            with open(m_path, "a") as f:
                f.write("\n\n" + content)
            master_ids.update(new_ids)
            os.remove(batch_file)
        else:
            print(f"Unknown prefix {prefix} in {batch_file}")
    else:
        print(f"Deleting fully redundant batch: {os.path.basename(batch_file)}")
        os.remove(batch_file)

# 3. Add signatures to all .md files
for fpath in glob.glob(os.path.join(DIR, "*.md")):
    with open(fpath, "r") as f:
        content = f.read()
    if "borjamoskv" not in content.lower() and "borja moskv" not in content.lower():
        content = "<!-- Author: Borja Moskv (SYS_ID: borjamoskv) -->\n\n" + content
        with open(fpath, "w") as f:
            f.write(content)
        print(f"Added signature to {os.path.basename(fpath)}")

print("Resolution complete.")
