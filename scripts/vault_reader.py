import os
import sys
from cryptography.fernet import Fernet
try:
    from dotenv import load_dotenv
    _BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(_BASE, '.env.vault'))
except ImportError:
    pass

def main():
    if len(sys.argv) < 2:
        print("Usage: python vault_reader.py <filename_without_enc>")
        sys.exit(1)

    filename = sys.argv[1]
    vault_dir = '$CORTEX_ROOT/20_VAULT'
    
    # Buscar el archivo en vault_dir o vault_dir/ontology
    target_path = os.path.join(vault_dir, filename + '.enc')
    if not os.path.exists(target_path):
        target_path = os.path.join(vault_dir, 'ontology', filename + '.enc')
        if not os.path.exists(target_path):
            print(f"[ERROR] No se encontró {filename}.enc en {vault_dir} ni en ontology/")
            sys.exit(1)

    vault_key = os.environ.get("CORTEX_VAULT_KEY")
    if not vault_key:
        print("\033[1;31m[CORTEX APOPTOSIS]\033[0m CORTEX_VAULT_KEY is missing.")
        sys.exit(1)

    fernet = Fernet(vault_key)
    with open(target_path, 'rb') as f:
        encrypted = f.read()

    decrypted = fernet.decrypt(encrypted)
    print(decrypted.decode('utf-8'))

if __name__ == '__main__':
    main()
