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

### Changed

- Reemplazado Databricks Git Folder por una carpeta normal administrada mediante Declarative Automation Bundles.
- La administración del presupuesto con Terraform es opcional y queda desactivada por defecto para evitar duplicar el presupuesto inicial del laboratorio.
- Terraform crea el grupo de cuenta `data-engineers`, lo asigna al workspace Dev y administra la membresía inicial antes de conceder `CAN_EDIT`.
- La capa Databricks reutiliza el catálogo administrado del workspace respaldado por Default Storage y limita la escritura de CI/CD al esquema `cicd`.
- Dev y QA permiten debugging manual, pero cada redespliegue restaura el SHA y elimina drift.
- Terraform administra las carpetas y permisos del workspace sin clonar el repositorio.
- El despliegue Dev llama a un workflow reutilizable preparado para extraerse a un repositorio central.
- La guía de costos distingue apagar cómputo de destruir infraestructura y registra la comprobación de clústeres, warehouses y jobs detenidos.

### Deprecated

### Removed

### Fixed

### Security

- Elevado el mínimo de `setuptools` a `83.0.0` en el paquete y en CI para corregir
  `PYSEC-2026-3447`, detectado por `pip-audit` durante el primer PR real.

<!--
Al publicar una versión:
1. Mueve las entradas de Unreleased a una sección como `## [0.1.0] - 2026-10-07`.
2. Conserva sólo las categorías que tengan contenido.
3. Añade al final los enlaces de comparación entre tags.
4. Crea nuevamente una sección Unreleased vacía.
-->
