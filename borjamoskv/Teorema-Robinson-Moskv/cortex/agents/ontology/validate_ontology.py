#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Borja Moskv (SYS_ID: borjamoskv)
# Reality Level: C5-REAL
# Description: Verifies markdown file formats, structural tables, and references inside the ontology registry.

import os
import re
import sys
import glob

ONTOLOGY_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_TO_CHECK = [os.path.basename(f) for f in glob.glob(os.path.join(ONTOLOGY_DIR, "*.md"))]

def validate_file(filename, all_ids):
    filepath = os.path.join(ONTOLOGY_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[-] Missing file: {filename}")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    errors = 0
    print(f"[*] Auditing {filename}...")

    # Check for empty files
    if not content.strip():
        print(f"  [ERROR] File is empty.")
        return False

    # Check for creator signature (Borja Moskv / borjamoskv)
    if "borjamoskv" in content.lower() or "borja moskv" in content.lower():
        print(f"  [OK] Creator signature verified.")
    else:
        print(f"  [ERROR] Missing creator signature (Rule Γ1).")
        errors += 1

    # Extract declared IDs only:
    # 1. Inside table cell as first column: | ID-001 |
    # 2. Inside list items: * **[ID-001]**
    table_declarations = re.findall(r"\|\s*([A-Z]+(?:-CAT)?-\d{3})\s*\|", content)
    list_declarations = re.findall(r"\*\s*\*\*\[([A-Z]+(?:-CAT)?-\d{3})\]\*\*", content)
    declarations = table_declarations + list_declarations

    # Ignore header row names like "ID"
    declarations = [d for d in declarations if d != "ID"]

    for item_id in declarations:
        if item_id in all_ids:
            print(f"  [ERROR] Duplicate definition of ID: {item_id}")
            errors += 1
        else:
            all_ids.add(item_id)

    # Check file link integrity (e.g. [name](./file#anchor) or [name](file.md))
    link_pattern = re.compile(r"\[.*?\]\(([^)]+)\)")
    links = link_pattern.findall(content)
    for link in links:
        # Strip query/anchor parameters
        clean_path = link.replace("file://", "").split("#")[0]
        
        # If relative, resolve relative to ONTOLOGY_DIR
        if not os.path.isabs(clean_path):
            clean_path = os.path.join(ONTOLOGY_DIR, clean_path)
            
        if not os.path.exists(clean_path):
            print(f"  [ERROR] Link path does not exist: {clean_path}")
            errors += 1

    return errors == 0

def main():
    success = True
    all_ids = set()
    for f in FILES_TO_CHECK:
        if not validate_file(f, all_ids):
            success = False
    
    if not success:
        print("[-] Ontology audit failed.")
        sys.exit(1)
    
    print(f"[+] All core ontology documents successfully verified. Integrity = 1.0 (Checked {len(all_ids)} declared IDs)")

if __name__ == "__main__":
    main()


