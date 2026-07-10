# Especificación de Trust Store y Criptografía (v0.2.2)

Este documento define la infraestructura criptográfica y las reglas de validación necesarias para garantizar la no repudiación, integridad y trazabilidad en el flujo de enrutamiento shadow.

## 1. Trust Store de Identidades

El router no acepta firmas de claves arbitrarias. Debe existir una base de confianza (`Trust Store`) descentralizada o local que asocie `key_id` con emisores autenticados.

### Formato de Clave en el Trust Store
```json
{
  "issuer": "did:web:router.cortex.internal",
  "keys": {
    "did:key:z6MkpTHR8VNsBxRcmStjecrxVCoVdPk2yFw6J22tCSZazn1x": {
      "algorithm": "Ed25519",
      "public_key_hex": "2b3be5d4...",
      "valid_from": "2026-07-01T00:00:00Z",
      "valid_until": "2026-12-31T23:59:59Z",
      "revoked": false,
      "roles": ["router", "evaluator"]
    }
  }
}
```

### Reglas de Validación
1. **Fallo Cerrado (Fail-Closed):** Si la clave no está en el Trust Store, si ha expirado, o si tiene la bandera `revoked: true`, el recibo se considera inválido.
2. **Validación del Algoritmo:** Solo se permite `"Ed25519"`. Cualquier intento de degradación de algoritmo (ej. `none` o claves simétricas débiles) aborta el proceso de validación.

---

## 2. Especificación del Envelope Criptográfico

Para garantizar que no haya manipulación física del DAG de recibos, la firma se calcula sobre el Envelope completo y su payload canonicalizado bajo la especificación JCS (RFC 8785).

```
+-------------------------------------------------------------+
| Envelope (v0.2.2)                                           |
| - schema_version: "proof-of-route/envelope/v0.2.2"          |
| - parent_signed_receipt_hash: "sha256:previous_envelope"    |
| - payload_hash: "sha256:jcs_payload"                        |
| - signature: { algorithm, key_id, value, signed_at }        |
|                                                             |
| +---------------------------------------------------------+ |
| | Payload JCS (RFC 8785)                                  | |
| | - receipt_type: "decision_receipt" / "execution_receipt"| |
| | - (Campos del recibo sin floats, usando enteros)        | |
| +---------------------------------------------------------+ |
+-------------------------------------------------------------+
```

---

## 3. Test Vectors para Canonicalización JCS (RFC 8785)

Para asegurar la interoperabilidad sin importar el lenguaje de ejecución (Python, Rust, JavaScript), se definen los siguientes vectores de prueba:

### Vector 1: Payload Simple sin anidamiento
- **Input:**
  ```json
  {"z": 1, "a": 2, "cost_microusd": 4200}
  ```
- **JCS Canonical (Bytes):**
  ```json
  {"a":2,"cost_microusd":4200,"z":1}
  ```
- **SHA-256 Hash:** `04e578c772ea5a5bd2b0eb6ceb34b172a6b2bc4f3a74efba1bf425adff3ab857`

### Vector 2: Payload con caracteres especiales Unicode
- **Input:**
  ```json
  {"mensaje": "Exergía y Causalidad", "orden": ["primario", "sombra"]}
  ```
- **JCS Canonical (Bytes):**
  ```json
  {"mensaje":"Exerg\u00eda y Causalidad","orden":["primario","sombra"]}
  ```
- **SHA-256 Hash:** `667c29e71e72d6ff175d658c70ca09540026e6de3bb74fcf37537b08d4b3eb0b`
