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

Restringe el environment a la rama protegida `main`. El subject OIDC configurado por Terraform es:

```text
repo:OWNER/REPOSITORY:environment:dev
```

Si se renombra o transfiere el repositorio, primero actualiza Terraform; de lo contrario OIDC fallará,
que es el comportamiento seguro.

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
