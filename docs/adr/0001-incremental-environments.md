# ADR 0001: Aprovisionamiento incremental por entorno

- Estado: Aceptado
- Fecha: 2026-10-07

## Decisión

Crear sólo Dev. QA se crea después de validar CI/CD Dev y Prod después de validar la promoción QA.

## Motivo

Reduce costo y superficie operativa dentro del presupuesto educativo de S/200. Mantener código
Terraform preparado no genera costo; crear recursos sí.

## Actualización 2026-10-11

Dev completó CI/CD, reconciliación, smoke test y migración de state. Cost Management mostró que el NAT
Gateway administrado es el principal costo base. QA será efímero en el laboratorio: se crea para probar
un release candidate y se destruye después de recopilar evidencia. En un entorno real con presupuesto
y requisitos de disponibilidad distintos, QA permanece aprovisionado.

