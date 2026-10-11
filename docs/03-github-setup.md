# 03 — Configuración de GitHub

## Repositorio y rama

1. Crea un repositorio público vacío y añade este checkout como `origin`.
2. Publica el commit inicial en `main`.
3. En **Settings → Branches**, protege `main`:
   - Pull Request obligatorio;
   - una aprobación;
   - conversación resuelta;
   - rama actualizada antes del merge;
   - checks `Python, SQL and YAML`, `Security checks` y `Terraform static validation`;
   - sin force push ni eliminación.
4. Usa squash merge y elimina ramas después del merge.

## Environment Dev

Crea un GitHub Environment llamado exactamente `dev` y añade variables, no secrets:

| Variable | Origen |
|---|---|
| `DATABRICKS_HOST` | output de `infra/azure/dev` |
| `DATABRICKS_CLIENT_ID` | output de `infra/databricks/dev` |
| `DATABRICKS_WORKSPACE_ROOT` | valor fijo `/Workspace/data/proyecto_test` |
| `DATABRICKS_CATALOG` | output de `infra/databricks/dev` |
| `DATABRICKS_SCHEMA` | output de `infra/databricks/dev` |

Restringe el environment a la rama protegida `main`. Para repositorios creados, renombrados o
transferidos desde el 15 de julio de 2026, GitHub emite un `sub` inmutable que incorpora los IDs
numéricos del propietario y del repositorio. Terraform configura exactamente ese formato:

```text
repo:OWNER@OWNER_ID/REPOSITORY@REPOSITORY_ID:environment:dev
```

Los nombres facilitan la lectura y los IDs impiden que un repositorio distinto herede la confianza si
se reutiliza un nombre. Se obtienen del claim real o de la API de GitHub; no son secretos. Databricks
compara el `sub` de forma exacta. El `audience` se deriva del host como
`https://<workspace>/oidc/v1/token`, que es el valor que la CLI obtiene de los metadatos del workspace.

Si se renombra o transfiere el repositorio, primero actualiza y aplica Terraform; de lo contrario OIDC
fallará, que es el comportamiento seguro. No relajes el patrón ni sustituyas los IDs por comodines.

### Diagnóstico del primer intercambio OIDC

El primer despliegue real llegó hasta `databricks current-user me` y falló antes de modificar el
workspace. El log mostró `TOKEN_SUBJECT_INVALID`: la política usaba el formato antiguo por nombre,
pero el JWT contenía el formato inmutable. También mostró el `audience` resuelto automáticamente por
la CLI. La corrección se hizo en Terraform, no mediante una credencial persistente ni una excepción
manual, para mantener la política auditable e idempotente.

El segundo intento superó el intercambio OIDC y llegó nuevamente a `databricks current-user me`. Esta
vez la API respondió que la identidad no tenía `workspace-access`, `workspace-consume` ni
`databricks-sql-access`. Ese mensaje demuestra que el token ya identificaba al service principal; el
bloqueo estaba en su autorización dentro del workspace. La solución de mínimo privilegio es administrar
únicamente `workspace_access = true` mediante Terraform. No se habilita SQL ni creación irrestricta de
cómputo. El job volvió a detenerse antes del Bundle, la reconciliación y el smoke test.

### Diagnóstico de la primera validación del Bundle

Después de conceder `workspace_access`, OIDC y `databricks current-user me` finalizaron correctamente.
La validación del Bundle rechazó el target porque `mode: development` exige que `root_path` y el
prefijo incluyan al usuario actual. Ese modo está diseñado para copias personales y aisladas por
desarrollador; este laboratorio utiliza una única copia Dev compartida administrada por CI.

Los modos de despliegue son opcionales. El target Dev omite `mode`, mantiene un `name_prefix` explícito
y conserva `/Workspace/.cicd/proyecto_test/dev` como raíz estable protegida. No se cambió a
`mode: production`, porque ese modo incorpora validaciones adicionales de `run_as` y permisos que se
configurarán deliberadamente cuando el modelo de ejecución lo requiera. La decisión se documenta en
[ADR 0007](adr/0007-shared-ci-dev-bundle-target.md).

## Flujo de aprendizaje

1. Crea `feature/...` y abre PR hacia `main`.
2. CI corre sin credenciales cloud.
3. Tras aprobación y merge, `deploy-dev.yml` obtiene un token OIDC temporal.
4. El job valida variables y guardas, despliega el Bundle y reconcilia la carpeta normal del proyecto.
5. Los archivos manuales se eliminan y los modificados se restauran desde el SHA.
6. El Job serverless de humo sólo se ejecuta si el workspace coincide con el manifiesto.

Dev permite a los desarrolladores modificar `/Workspace/data/proyecto_test` para debugging. Antes de
otro despliegue deben copiar cualquier solución a una rama: el pipeline no importa cambios hacia Git.
QA seguirá la misma política cuando exista; Prod será de sólo lectura para desarrolladores.

`deploy-dev.yml` es un caller del workflow `reusable-databricks-deploy.yml`. Tras validar Dev, este
último se extraerá a un repositorio de plataforma y el caller fijará un tag estable o SHA, nunca `main`.

QA y Prod no se configuran todavía. Sus workflows se añadirán cuando Dev cumpla todos los criterios de
aceptación. Los candidatos usarán `v0.1.0-rc.N`; la versión final `v0.1.0` apuntará al mismo SHA aprobado.
