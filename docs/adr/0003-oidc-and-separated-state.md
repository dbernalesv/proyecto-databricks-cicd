# ADR 0003: OIDC y estados Terraform separados

- Estado: Aceptado
- Fecha: 2026-10-07

## Decisión

GitHub se autentica como service principal Databricks mediante OIDC, sin PAT. Azure y Databricks usan
states separados. El state comenzó local y se migró a Azure Storage antes de QA.

## Motivo

OIDC elimina secretos de larga duración. Separar estados respeta el orden de creación y reduce el radio
de impacto. El state local simplifica el primer aprendizaje, pero no escala de forma segura al equipo.

## Actualización 2026-10-10: identidad inmutable de GitHub

El repositorio usa el `sub` inmutable de GitHub con nombres e IDs numéricos del propietario y del
repositorio. Databricks exige coincidencia exacta y la política se limita además al Environment `dev`.
El `audience` se deriva del endpoint OIDC anunciado por el workspace, el mismo que utiliza la CLI
oficial al autenticar con `github-oidc`.

Esta decisión evita confiar sólo en nombres reutilizables y conserva autenticación sin secretos. Los
IDs se mantienen como variables no sensibles para que una transferencia o recreación del repositorio
produzca un plan explícito y requiera revisión.

## Actualización 2026-10-11: backend remoto

La migración anunciada se implementa según [ADR 0008](0008-remote-terraform-state.md). Azure y
Databricks conservan states separados en el mismo contenedor privado, autenticado con Microsoft Entra.
Sólo el state mínimo de la pila bootstrap permanece local como excepción documentada. La migración de
ambas capas Dev terminó con inventarios completos y planes `No changes`.

