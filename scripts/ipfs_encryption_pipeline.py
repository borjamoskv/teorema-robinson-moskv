import json
import hashlib
import os
import secrets
from cryptography.fernet import Fernet

def generate_tenant_key() -> bytes:
    return Fernet.generate_key()

def encrypt_payload(payload: dict, key: bytes) -> bytes:
    f = Fernet(key)
    raw_bytes = json.dumps(payload, separators=(',', ':'), sort_keys=True, ensure_ascii=False).encode('utf-8')
    return f.encrypt(raw_bytes)

def upload_to_ipfs(ciphertext: bytes) -> str:
    h = hashlib.sha256(ciphertext).hexdigest()
    return f'QmMock{h[:40]}'

def pipeline(manifest_batch: list, tenant_key: bytes):
    print(f'Encrypting batch of {len(manifest_batch)} receipts...')
    encrypted_batch = encrypt_payload({'batch': manifest_batch}, tenant_key)
    cid = upload_to_ipfs(encrypted_batch)
    print(f'Uploaded to IPFS: ipfs://{cid}')
    metadata_uri_content = {'schema': 'max-router-batch-manifest/v1', 'encrypted_blob_cid': cid, 'batch_size': len(manifest_batch), 'encryption_algorithm': 'AES-128-CBC (Fernet)', 'note': 'Content is encrypted. Tenant key required for decryption.'}
    metadata_cid = upload_to_ipfs(json.dumps(metadata_uri_content, separators=(',', ':'), sort_keys=True, ensure_ascii=False).encode('utf-8'))
    print(f'Metadata URI to anchor on-chain: ipfs://{metadata_cid}/batch-manifest.json')
    return metadata_cid
if __name__ == '__main__':
    dummy_batch = [{'receipt_id': 'rcpt_123'}, {'receipt_id': 'rcpt_124'}]
    key = generate_tenant_key()
    pipeline(dummy_batch, key)
