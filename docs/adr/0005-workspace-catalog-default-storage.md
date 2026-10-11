# ADR 0005: reutilizar el catálogo del workspace con Default Storage

## Estado

Aceptado.

## Contexto

El workspace Dev nuevo incluye Default Storage y un catálogo administrado llamado
`dbw_databricks_cicd_dev`. La API de creación de catálogos rechazó un catálogo adicional sin
`storage_root`, aunque la interfaz puede aprovisionarlo sobre Default Storage. Crear una cuenta de
almacenamiento, access connector, credencial y external location sólo para este laboratorio ampliaría
el costo y el alcance operativo.

## Decisión

Terraform consulta el catálogo administrado existente mediante `data.databricks_catalog.workspace` y
crea dentro de él el esquema `cicd`. La identidad CI/CD obtiene `USE_CATALOG` en el catálogo y permisos
de tabla únicamente en ese esquema. El catálogo no se incorpora al state porque su ciclo de vida
pertenece al workspace.

## Consecuencias

- Se conserva automatización declarativa para esquema, permisos e identidades sin crear almacenamiento
  adicional.
- Dev queda aislado por workspace y por esquema, suficiente para la fase inicial de bajo costo.
- QA y Prod tendrán sus propios workspaces y catálogos administrados cuando sean aprovisionados.
- Si el proyecto requiere ubicaciones externas o gobierno multiespacio, se añadirá almacenamiento
  dedicado, credenciales y external locations mediante Terraform antes de producción.
