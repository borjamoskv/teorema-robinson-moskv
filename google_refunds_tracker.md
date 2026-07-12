# █ Google Refunds Tracker — 25 Accounts Management

Este documento permite realizar el seguimiento sistemático de las solicitudes de reembolso para evitar colisiones de estado en la pasarela de pagos de Google y prevenir el bloqueo preventivo de la tarjeta de crédito.

## 📊 Resumen de Estado
- **Total Cuentas:** 25
- **Cargos Duplicados Detectados (21.99 €):** 0 / 25
- **Cargos Huérfanos Pendientes:** 0
- **Total Reembolsado:** 0.00 €

---

## 🗂️ Matriz de Seguimiento de Cuentas

| ID | Cuenta de Gmail | ID de Transacción (GPA) | Estado del Cargo | Estado del Reembolso (g.co/play/refund) | Soporte Google One (Chat) | Notas / Hito |
|----|-----------------|-------------------------|------------------|-----------------------------------------|---------------------------|--------------|
| 01 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 02 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 03 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 04 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 05 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 06 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 07 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 08 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 09 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 10 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 11 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 12 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 13 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 14 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 15 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 16 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 17 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 18 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 19 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 20 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 21 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 22 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 23 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 24 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |
| 25 |                 |                         | [ ] Cobrado / [ ] Reservado | [ ] No Iniciado / [ ] Solicitado / [ ] Aprobado | [ ] N/A / [ ] Chat Iniciado / [ ] Resuelto | |

---

## ⚡ Pasos de Contingencia Inmediatos

1. **Localizar el código GPA:** Busca en el extracto del banco el ID de transacción con el formato `GPA.XXXX-XXXX-XXXX-XXXXX`.
2. **Reembolso Automático:** Accede a [g.co/play/refund](https://g.co/play/refund) desde cada cuenta.
3. **Control de Daños de Tarjeta:** Si el banco bloquea la tarjeta por sospecha de fraude, contacta al soporte del banco para autorizar los cobros y evitar el bloqueo permanente en la red de pagos de Google.