# ADR 0003: OIDC y estados Terraform separados

- Estado: Aceptado
- Fecha: 2026-10-07

## Decisión

GitHub se autentica como service principal Databricks mediante OIDC, sin PAT. Azure y Databricks usan
states separados. El state comienza local y se migrará a Azure Storage antes de QA.

## Motivo

OIDC elimina secretos de larga duración. Separar estados respeta el orden de creación y reduce el radio
de impacto. El state local simplifica el primer aprendizaje, pero no escala de forma segura al equipo.

