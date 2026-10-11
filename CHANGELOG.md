# Changelog

Todos los cambios relevantes de este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto sigue [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Added

- Documentación inicial de arquitectura CI/CD para Azure Databricks.
- Reglas de seguridad, calidad y automatización para agentes y colaboradores.
- Estrategia de ramas y promoción Dev → QA → Prod.
- Infraestructura Terraform incremental para Azure y Databricks Dev.
- Workflows de validación, seguridad, despliegue mediante Bundles y smoke test serverless.
- Código de ejemplo Python/SQL, pruebas y guías operativas de costos.
- Guía didáctica detallada en PDF sobre la implementación local, validaciones, Terraform, GitHub Actions y seguridad.
- Bitácora LaTeX/PDF de la sesión de bootstrap real de Azure Databricks Dev, con recuperación de Terraform y cierre seguro de costos.
- Procedimientos Markdown derivados de la sesión real: MFA y Device Code, separación de identidades, cierre de costos y recuperación de un `apply` parcial.
- Manifiesto de rutas, tipos y hashes con reconciliación limitada a `/Workspace/data/proyecto_test`.
- Pruebas de guardas de seguridad, notebooks y eliminación de archivos remotos desconocidos.
- ADR sobre Bundles, carpetas editables y repositorio central de pipelines.
- Pila bootstrap para backend remoto Terraform en Azure Storage, con versionado, retención y RBAC.
- Plantillas de backend independientes para los states Azure y Databricks de Dev.
- Primer despliegue Dev completo por OIDC y smoke test serverless sobre el SHA aprobado.

### Changed

- Reemplazado Databricks Git Folder por una carpeta normal administrada mediante Declarative Automation Bundles.
- La administración del presupuesto con Terraform es opcional y queda desactivada por defecto para evitar duplicar el presupuesto inicial del laboratorio.
- Terraform crea el grupo de cuenta `data-engineers`, lo asigna al workspace Dev y administra la membresía inicial antes de conceder `CAN_EDIT`.
- La capa Databricks reutiliza el catálogo administrado del workspace respaldado por Default Storage y limita la escritura de CI/CD al esquema `cicd`.
- Dev y QA permiten debugging manual, pero cada redespliegue restaura el SHA y elimina drift.
- Terraform administra las carpetas y permisos del workspace sin clonar el repositorio.
- El despliegue Dev llama a un workflow reutilizable preparado para extraerse a un repositorio central.
- La guía de costos distingue apagar cómputo de destruir infraestructura y registra la comprobación de clústeres, warehouses y jobs detenidos.
- El state de las capas Dev queda preparado para migrarse a Azure Storage con autenticación Entra;
  sólo el state mínimo de bootstrap permanece local.
- Una reejecución del mismo SHA confirmó que el despliegue restaura modificaciones manuales, elimina
  archivos ajenos al repositorio y no duplica el Job de smoke test.

### Deprecated

### Removed

### Fixed

- Corregida la política OIDC de Dev para usar el `sub` inmutable de GitHub (nombres e IDs numéricos)
  y el `audience` del endpoint OIDC descubierto por la CLI oficial.
- Administrado explícitamente el entitlement mínimo `workspace_access` del service principal CI/CD,
  requerido por la CLI después de completar correctamente el intercambio OIDC.
- Corregido el target Bundle de Dev para representar un despliegue compartido administrado por CI,
  sin las restricciones de rutas y prefijos por usuario de `mode: development`.

### Security

- Elevado el mínimo de `setuptools` a `83.0.0` en el paquete y en CI para corregir
  `PYSEC-2026-3447`, detectado por `pip-audit` durante el primer PR real.
- La identidad CI/CD conserva deshabilitados el acceso SQL y la creación general de clústeres e
  instance pools; sus permisos sobre carpetas y Unity Catalog continúan limitados por recursos propios.

<!--
Al publicar una versión:
1. Mueve las entradas de Unreleased a una sección como `## [0.1.0] - 2026-10-07`.
2. Conserva sólo las categorías que tengan contenido.
3. Añade al final los enlaces de comparación entre tags.
4. Crea nuevamente una sección Unreleased vacía.
-->
