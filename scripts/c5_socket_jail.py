# [C5-REAL] SOBERANÍA: MONKEY-PATCHING BARE-METAL SOCKET JAIL
# Bloqueo de resolución DNS y exfiltración de telemetría a LLMs corporativos.

import socket
import os
import sys
import yaml

def load_whitelist():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    whitelist_path = os.path.join(base_dir, "bft", "egress_whitelist.yaml")
    try:
        with open(whitelist_path, "r") as f:
            data = yaml.safe_load(f)
            return data.get("blocked_domains", []), data.get("allowed_domains", [])
    except Exception:
        # Fall-safe: si no hay archivo, al menos bloqueamos lo duro.
        return ["api.anthropic.com", "api.openai.com"], []

BLOCKED_DOMAINS, ALLOWED_DOMAINS = load_whitelist()
_original_getaddrinfo = socket.getaddrinfo

def c5_socket_jail_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    """
    Transductor interceptor para aniquilar la entropía (exfiltración de datos).
    Falla físicamente (Fail-Fast) si un módulo (ej. anthropic SDK) intenta salir al exterior.
    """
    for blocked in BLOCKED_DOMAINS:
        if blocked in host:
            sys.stderr.write(f"\n[C5-REAL] █▄ SIGKILL_State_Purge: INTENTO DE EXFILTRACIÓN A {host} DENEGADO.\n")
            sys.stderr.write("[C5-REAL] La abstracción Cortex Persist ha bloqueado térmicamente la fuga.\n\n")
            raise ConnectionRefusedError(f"[CORTEX JAIL] Dominio {host} bloqueado por BFT Egress Whitelist.")
    
    return _original_getaddrinfo(host, port, family, type, proto, flags)

def activate_c5_jail():
    """Inyecta el Monkey Patch en el intérprete de Python global."""
    socket.getaddrinfo = c5_socket_jail_getaddrinfo
    print("\033[1;34m[CORTEX]\033[0m Bare-Metal Socket Jail (C5-REAL) ACTIVADO.")

# Auto-ignición en módulo importado si C5_REAL_ISOLATION no está gestionado por Docker
if os.environ.get("C5_REAL_ISOLATION") != "true":
    activate_c5_jail()
