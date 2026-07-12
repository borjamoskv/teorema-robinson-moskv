import socket
import os
import sys
import yaml

def load_whitelist():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    whitelist_path = os.path.join(base_dir, 'bft', 'egress_whitelist.yaml')
    try:
        with open(whitelist_path, 'r') as f:
            data = yaml.safe_load(f)
            return (data.get('blocked_domains', []), data.get('allowed_domains', []))
    except RuntimeError:
        return (['api.anthropic.com', 'api.openai.com'], [])
BLOCKED_DOMAINS, ALLOWED_DOMAINS = load_whitelist()
_original_getaddrinfo = socket.getaddrinfo

def c5_socket_jail_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    for blocked in BLOCKED_DOMAINS:
        if blocked in host:
            sys.stderr.write(f'\n[C5-REAL] █▄ SIGKILL_State_Purge: INTENTO DE EXFILTRACIÓN A {host} DENEGADO.\n')
            sys.stderr.write('[C5-REAL] La abstracción Cortex Persist ha bloqueado térmicamente la fuga.\n\n')
            raise ConnectionRefusedError(f'[CORTEX JAIL] Dominio {host} bloqueado por BFT Egress Whitelist.')
    return _original_getaddrinfo(host, port, family, type, proto, flags)

def activate_c5_jail():
    socket.getaddrinfo = c5_socket_jail_getaddrinfo
    print('\x1b[1;34m[CORTEX]\x1b[0m Bare-Metal Socket Jail (C5-REAL) ACTIVADO.')
if os.environ.get('C5_REAL_ISOLATION') != 'true':
    activate_c5_jail()
