import os
import struct
import hashlib
import hmac
import secrets
INSTRUCTION_MAP = {'REFACTOR_AST': 1, 'PURGE_AST': 2, 'SIGKILL_STATE_PURGE': 3}
INSTRUCTION_REV = {v: k for k, v in INSTRUCTION_MAP.items()}

class InterlatBridge:

    def __init__(self, shared_secret: bytes=None):
        self.shared_secret = shared_secret or secrets.token_bytes(32)

    def _derive_keys(self, nonce: bytes):
        kdf = hmac.new(self.shared_secret, nonce, hashlib.sha256).digest()
        return (kdf[:16], kdf[16:])

    def _serialize_to_c_struct(self, payload: dict) -> bytes:
        inst_code = INSTRUCTION_MAP.get(payload['instruction'], 0)
        target_bytes = payload['target'].encode('utf-8')
        target_len = len(target_bytes)
        delta = payload['delta_entropy']
        fmt = f'>B H {target_len}s d'
        return struct.pack(fmt, inst_code, target_len, target_bytes, float(delta))

    def _deserialize_from_c_struct(self, data: bytes) -> dict:
        inst_code, target_len = struct.unpack_from('>B H', data, 0)
        fmt = f'>{target_len}s d'
        target_bytes, delta = struct.unpack_from(fmt, data, 3)
        return {'instruction': INSTRUCTION_REV.get(inst_code, 'UNKNOWN_OPCODE'), 'target': target_bytes.decode('utf-8'), 'delta_entropy': delta}

    def encrypt_payload(self, payload_dict: dict) -> bytes:
        plaintext = self._serialize_to_c_struct(payload_dict)
        nonce = secrets.token_bytes(16)
        cipher_key, auth_key = self._derive_keys(nonce)
        ciphertext = bytearray()
        for i, byte in enumerate(plaintext):
            key_block = hashlib.sha256(cipher_key + i.to_bytes(4, 'big')).digest()
            ciphertext.append(byte ^ key_block[0])
        ciphertext = bytes(ciphertext)
        mac = hmac.new(auth_key, ciphertext, hashlib.sha256).digest()
        return nonce + mac + ciphertext

    def decrypt_payload(self, opaque_packet: bytes) -> dict:
        if len(opaque_packet) < 48:
            raise ValueError('C5-REAL SIGKILL: Interlat Packet demasiado corto (Corrupted Tensor).')
        nonce = opaque_packet[:16]
        mac_received = opaque_packet[16:48]
        ciphertext = opaque_packet[48:]
        cipher_key, auth_key = self._derive_keys(nonce)
        mac_calculated = hmac.new(auth_key, ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(mac_received, mac_calculated):
            raise ValueError('C5-REAL SIGKILL: HMAC de Interlat manipulado. Vector Latente corrompido.')
        plaintext = bytearray()
        for i, byte in enumerate(ciphertext):
            key_block = hashlib.sha256(cipher_key + i.to_bytes(4, 'big')).digest()
            plaintext.append(byte ^ key_block[0])
        return self._deserialize_from_c_struct(bytes(plaintext))
if __name__ == '__main__':
    print('Iniciando Transmisión Interlat (Tensor-to-Tensor)...')
    bridge = InterlatBridge()
    subagent_thought = {'instruction': 'REFACTOR_AST', 'target': 'cortex.db', 'delta_entropy': 0.05}
    print(f'\n[ESTADO C4-SIM] Texto plano original: {subagent_thought}')
    opaque_tensor = bridge.encrypt_payload(subagent_thought)
    print(f'\n[ESTADO EXERGY C5-REAL] Vector IPC (Hexdump del Tensor):')
    hex_dump = ' '.join((f'{b:02x}' for b in opaque_tensor))
    for i in range(0, len(hex_dump), 48):
        print(f'0x{i // 3:04x} | {hex_dump[i:i + 48]}')
    print('\nOrquestador validando vector latente...')
    recovered = bridge.decrypt_payload(opaque_tensor)
    print(f'Colapso Termodinámico Inverso Exitoso: {recovered}')
