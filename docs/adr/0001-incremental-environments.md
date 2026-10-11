# ADR 0001: Aprovisionamiento incremental por entorno

- Estado: Aceptado
- Fecha: 2026-10-07

## Decisión

Crear sólo Dev. QA se crea después de validar CI/CD Dev y Prod después de validar la promoción QA.

## Motivo

Reduce costo y superficie operativa dentro del presupuesto educativo de S/200. Mantener código
Terraform preparado no genera costo; crear recursos sí.

