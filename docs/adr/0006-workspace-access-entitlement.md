# ADR 0006: Entitlement mínimo para la identidad CI/CD

## Estado

Aceptado.

## Contexto

Después de corregir el subject OIDC inmutable, GitHub Actions obtuvo un token temporal válido para el
service principal. Sin embargo, `databricks current-user me` fue rechazado porque la identidad no tenía
ninguno de los entitlements que permiten usar las APIs del workspace. La asignación `USER` realizada
desde la cuenta Databricks incorporaba la identidad al workspace, pero no declaraba explícitamente su
`workspace_access`.

## Decisión

Terraform consulta el service principal ya asignado mediante el provider del workspace para obtener su
ID SCIM local. A continuación administra `databricks_entitlements` con:

- `workspace_access = true`;
- `databricks_sql_access = false`;
- `allow_cluster_create = false`;
- `allow_instance_pool_create = false`.

La identidad conserva por separado `CAN_MANAGE` sólo sobre las rutas CI/CD declaradas y grants mínimos
sobre el catálogo y esquema de pruebas. No recibe rol de administrador.

## Consecuencias

La CLI puede verificar la identidad y usar las APIs necesarias para desplegar el Bundle. La capacidad
de crear o ejecutar recursos concretos sigue dependiendo de sus ACL y de la definición declarativa del
Bundle; `workspace_access` no concede control general del workspace. El entitlement queda auditable,
repetible e idempotente y no requiere un cambio manual en la interfaz.
