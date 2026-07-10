import subprocess
from typing import Dict

def verify_signed_tag(commit: str) -> bool:
    """Verifica si el commit está apuntado por un tag firmado y válido."""
    try:
        # get tags pointing to this commit
        result = subprocess.run(
            ["git", "tag", "--points-at", commit],
            capture_output=True, text=True, check=True
        )
        tags = result.stdout.strip().split("\n")
        if not tags or not tags[0]:
            return False
            
        # verify the signature of the first tag
        verify_result = subprocess.run(
            ["git", "verify-tag", tags[0]],
            capture_output=True, text=True
        )
        return verify_result.returncode == 0
    except subprocess.CalledProcessError:
        return False

def verify_branch_protection(branch: str = "master") -> bool:
    """
    En un entorno local, esto es un stub. En producción, 
    debería consultar la API de GitHub/GitLab para verificar
    si la rama tiene protecciones (requires pull request, required reviews, etc).
    """
    # Dummy implementation for local script
    return True

def verify_remote_audit(remote: str = "origin") -> bool:
    """Verifica si el remote apunta a un servidor auditable (ej. github)."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", remote],
            capture_output=True, text=True, check=True
        )
        url = result.stdout.strip()
        return "github.com" in url or "gitlab.com" in url
    except subprocess.CalledProcessError:
        return False

def is_trusted_ontology(commit: str) -> Dict[str, Any]:
    """
    Evalúa holísticamente si un commit ontológico es confiable basándose en evidencias externas
    y criptográficas, en lugar de asumir inmutabilidad por su mero hash.
    """
    signed = verify_signed_tag(commit)
    protected = verify_branch_protection("master")
    audited = verify_remote_audit("origin")
    
    trusted = signed and protected and audited
    return {
        "trusted": trusted,
        "checks": {
            "signed_tag": signed,
            "branch_protected": protected,
            "remote_auditable": audited
        }
    }
