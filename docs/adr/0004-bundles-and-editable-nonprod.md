# ADR 0004: Bundles y carpetas editables no productivas

- Estado: Aceptado
- Fecha: 2026-10-08

## Decisión

Desplegar `proyecto_test/` mediante Declarative Automation Bundles a una carpeta normal
`/Workspace/data/proyecto_test`. Dev y QA permiten edición para debugging; Prod no. Después de cada
despliegue, un manifiesto elimina extras y verifica rutas, tipos y hashes contra el SHA promovido.

El estado del Bundle vive bajo `/Workspace/.cicd`, fuera de la carpeta editable. Las guardas rechazan
cualquier operación destructiva sobre `/Workspace`, `/Workspace/data` o rutas con subproyectos.

## Motivo

Los desarrolladores conservan una experiencia rápida de diagnóstico sin convertir el workspace en
fuente de verdad. El siguiente despliegue restaura Git, evita archivos huérfanos y mantiene promoción
inmutable. Bundle administra también Jobs, eliminando la necesidad de copiar JSON de workflows.

## Consecuencias

- Un cambio manual útil debe copiarse a una rama antes del siguiente despliegue.
- No existe sincronización automática workspace → Git.
- El workflow común se mantiene local hasta validar Dev y luego se extraerá a un repositorio central.
