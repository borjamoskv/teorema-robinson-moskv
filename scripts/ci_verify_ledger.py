#!/usr/bin/env python3
import sys
import os
import subprocess
import sqlite3
import re

def main():
    bft_db = "bft/master_ledger.db"
    if not os.path.exists(bft_db):
        print("[*] No master_ledger.db found. Skipping CI verification.")
        return 0

    # Extraer trailer del último commit
    try:
        commit_msg = subprocess.check_output(["git", "log", "-1", "--pretty=%B"], text=True)
    except Exception as e:
        print(f"[!] Error reading git log: {e}")
        return 1

    match = re.search(r"Ledger-Head:\s+([a-f0-9]{64})", commit_msg)
    if not match:
        print("[*] No Ledger-Head trailer found in the latest commit. Assuming non-bft commit.")
        return 0

    git_head = match.group(1)

    # Comparar con sqlite
    try:
        conn = sqlite3.connect(bft_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT entry_hash FROM ledger_entries ORDER BY seq DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            print("[!] Ledger in DB is empty, but git commit has Ledger-Head.")
            return 1
            
        db_head = row["entry_hash"]
        
        if git_head != db_head:
            print(f"\033[1;31m[CORTEX APOPTOSIS]\033[0m Divergence detected!")
            print(f"Git Ledger-Head: {git_head}")
            print(f"DB  Ledger-Head: {db_head}")
            print("SIGKILL_State_Purge triggered.")
            return 1
            
        print(f"[*] Ledger-Head {git_head} verified successfully against DB.")
        return 0
        
    except Exception as e:
        print(f"[!] Error verifying DB: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
