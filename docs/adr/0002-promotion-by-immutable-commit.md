# ADR 0002: Promoción mediante commit inmutable

- Estado: Aceptado
- Fecha: 2026-10-07

## Decisión

Usar PRs `feature/*`/`fix/*` hacia `main`, despliegue automático Dev, tags `vX.Y.Z-rc.N` para QA y tag
final `vX.Y.Z` para Prod. QA y Prod reciben el mismo SHA.

## Motivo

Conserva aprobaciones y evidencias similares a un entorno regulado sin la divergencia de ramas
permanentes `develop`, `release` y `main`. Un candidato fallido no cambia Prod; se corrige con otro PR.

