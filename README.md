# CI/CD para Azure Databricks con GitHub Actions

Proyecto educativo para aprender a validar y promover código versionado —archivos Python, SQL y
notebooks— hacia Azure Databricks con un presupuesto objetivo de **S/200 mensuales**. La implantación
es incremental: primero se crea **Dev**; QA y Prod sólo se aprovisionan cuando la fase anterior funciona.

La implementación usa **Databricks Declarative Automation Bundles** para publicar una carpeta normal
en cada workspace. GitHub es la fuente de verdad: en Dev y QA se permite editar temporalmente para
depurar, pero cada redespliegue restaura exactamente el contenido del SHA promovido. Prod no admite
edición manual durante la operación normal.

## Estado actual del laboratorio

El entorno Dev ya fue aprovisionado en `eastus2`. La capa Azure permanece estable (`No changes`).
Están creados el workspace, la identidad CI/CD federada, el grupo
`data-engineers`, las carpetas administradas, el catálogo del workspace y el esquema `cicd`. El budget
mensual de USD 58 se creó manualmente y Terraform no lo duplica. QA y Prod permanecen sin crear.

El rol Global Administrator temporal ya fue retirado, el repositorio y sus checks están publicados y
`main` está protegido. El primer intercambio OIDC falló de forma segura antes de modificar Databricks
porque GitHub emitió el formato inmutable nuevo del subject. La política Terraform se ajusta al claim
exacto y al audience descubierto por la CLI antes de reintentar el despliegue. No había clústeres, SQL
warehouses ni jobs en ejecución al iniciar esta corrección.

## Objetivos del proyecto

- Mantener todo el código en Git y revisarlo mediante Pull Requests.
- Ejecutar validaciones automáticas de Python, SQL y configuración antes de promover cambios.
- Desplegar exactamente el mismo commit en Dev, QA y Prod.
- Separar identidades, permisos, variables y aprobaciones por entorno.
- Evitar secretos de larga duración y credenciales dentro del repositorio.
- Conservar trazabilidad: quién aprobó, qué commit se desplegó y en qué momento.

## Arquitectura del pipeline

```text
feature/*
    │
    ├── Pull Request → main
    │       ├── lint Python/SQL
    │       ├── pruebas unitarias y validaciones de seguridad
    │       └── validación o despliegue efímero en Dev
    │
    └── merge a main
            └── sincronización/despliegue en Dev
                    │
                    └── tag candidato (vX.Y.Z-rc.N)
                            └── despliegue en QA + pruebas
                                    │
                                    └── tag final sobre el mismo SHA
                                            └── aprobación → Prod
```

### Principios de promoción

1. **Dev** valida cada PR y recibe los merges a `main`.
2. **QA** recibe candidatos como `v1.2.0-rc.1`. Un fallo genera un fix y `rc.2`, sin afectar Prod.
3. **Prod** recibe un tag final `v1.2.0` sobre el mismo SHA aprobado en QA.
4. Los despliegues a QA y Prod usan **GitHub Environments** diferentes, con permisos y variables propios. Prod exige revisores y aprobación manual.
5. Cada ejecución debe registrar el SHA, la versión, el actor y el resultado de las pruebas.

## Flujo con Databricks Bundles

El árbol local `proyecto_test/` se publica en:

```text
/Workspace/data/proyecto_test/
├── process/
├── config/
├── ddl/
└── smoke/
```

No aparece como Git Folder. `databricks.yml` define targets y rutas; `resources/` define Jobs y otros
recursos. El estado interno se guarda separado bajo `/Workspace/.cicd/proyecto_test/<target>`.

El pipeline:

1. autentica una identidad no humana mediante OIDC;
2. valida y despliega el Bundle al SHA exacto;
3. genera un manifiesto de rutas, tipos y hashes;
4. restaura archivos modificados o eliminados y elimina archivos agregados manualmente;
5. rechaza cualquier limpieza fuera de `/Workspace/data/proyecto_test`;
6. ejecuta el Job serverless `smoke_test` sólo cuando el árbol coincide con Git.

Dev y QA permiten edición para debugging. Esos cambios no se sincronizan de regreso a Git y se
perderán en el siguiente despliegue si el desarrollador no los copia a una rama y abre un PR.
El grupo de cuenta `data-engineers`, su asignación al workspace Dev y la membresía inicial se
administran con Terraform; no dependen de una creación manual previa en la interfaz.

## Separación por entorno

| Entorno | Disparador | Referencia Git | Controles recomendados |
|---|---|---|---|
| Dev | PR y merge a `main` | SHA del PR o de `main` | Validación automática, permisos de desarrollo |
| QA | Tag `vX.Y.Z-rc.N` | SHA inmutable candidato | Pruebas de integración y aprobación QA |
| Prod | Tag final `vX.Y.Z` | El mismo SHA validado en QA | Aprobación manual y mínimo privilegio |

Cada entorno debe tener su propio workspace, identidad de despliegue, GitHub Environment y configuración. Nunca reutilices un token personal ni una identidad con privilegios de administrador entre los tres.

## Prerrequisitos

### Azure y Databricks

- Una suscripción de Azure y permisos para administrar identidades y asignaciones necesarias.
- Un workspace Dev inicialmente; QA y Prod se añadirán de manera progresiva.
- Un **service principal** o identidad federada por entorno, con mínimo privilegio.
- Autenticación sin secreto mediante **OpenID Connect (OIDC)** entre GitHub Actions y Azure/Databricks, siempre que la configuración de la cuenta lo permita.
- Permisos de la identidad sobre la carpeta de destino, estado del Bundle y recursos estrictamente necesarios.
- Una política de clúster o cómputo para pruebas, preferiblemente pequeña, acotada y con autoapagado.

### GitHub

- Un repositorio GitHub con Actions habilitado.
- Protección de la rama `main`: PR obligatorio, revisiones y checks requeridos.
- GitHub Environments llamados `dev`, `qa` y `prod`.
- Reglas de protección para `prod`, incluyendo revisores obligatorios.
- Variables no sensibles por entorno, por ejemplo:
  - `DATABRICKS_HOST`
  - `DATABRICKS_WORKSPACE_ROOT`
  - identificadores de cuenta, workspace o cómputo cuando sean necesarios
- Credenciales o parámetros sensibles sólo en GitHub Secrets, Azure Key Vault o mediante OIDC. Nunca en archivos versionados.

## Modelo de autenticación recomendado

Orden de preferencia:

1. **OIDC / workload identity federation**, sin secretos persistentes.
2. Service principal con secreto almacenado en GitHub Environment Secrets y con rotación definida.
3. Token personal únicamente para una prueba local temporal; nunca para un pipeline productivo.

Los logs no deben imprimir tokens, cabeceras de autorización ni valores sensibles. Los secretos deben estar enmascarados y su alcance debe limitarse al environment que los utiliza.

## Estructura objetivo del repositorio

```text
.
├── .github/
│   └── workflows/
│       ├── validate-pr.yml
│       ├── deploy-dev.yml
│       └── reusable-databricks-deploy.yml
├── proyecto_test/       # árbol que se refleja bajo /Workspace/data/proyecto_test
├── resources/           # Jobs/Pipelines declarados por el Bundle
├── databricks.yml       # targets, rutas y variables del Bundle
├── src/                 # módulos Python reutilizables
├── sql/                 # consultas y transformaciones SQL
├── tests/               # pruebas unitarias e integración
├── scripts/             # automatización auxiliar, idempotente
├── pyproject.toml        # lint, formato y pruebas de Python
├── .sqlfluff             # reglas SQL
├── README.md
├── AGENTS.md
├── CONTRIBUTING.md
└── CHANGELOG.md
```

Preferimos notebooks en formatos de texto revisables por Git. La lógica de negocio reutilizable debe vivir en módulos bajo `src/`, no duplicada entre notebooks.

## Primeros pasos para un Data Engineer

1. Instala Git, Python, la Databricks CLI oficial y un editor con soporte para Python, YAML y SQL.
2. Clona el repositorio y crea una rama corta desde `main`:

   ```bash
   git switch main
   git pull --ff-only
   git switch -c feature/mi-primer-notebook
   ```

3. Añade el código y sus pruebas. No incluyas tokens, contraseñas, archivos `.env` ni perfiles locales.
4. Ejecuta localmente los linters y las pruebas que se incorporen al proyecto, por ejemplo:

   ```bash
   ruff check .
   ruff format --check .
   sqlfluff lint sql/
   pytest
   ```

5. Revisa `git diff` y `git status` antes de confirmar los cambios.
6. Abre un Pull Request pequeño y explica qué cambia, cómo se probó y cuál es el impacto.
7. Espera los checks automáticos y corrige cualquier fallo. El PR validará el cambio en Dev.
8. Tras la aprobación y el merge, comprueba el despliegue de `main` en Dev.
9. Una versión candidata se etiqueta `vX.Y.Z-rc.N`; tras aprobar QA, el mismo SHA recibe `vX.Y.Z`.

## Ruta de implementación

Sigue las guías en orden:

1. [Alta de Azure y control de costos](docs/01-azure-account-and-cost.md).
2. [Terraform explicado y despliegue Dev](docs/02-terraform-learning-guide.md).
3. [Configuración de GitHub](docs/03-github-setup.md).

### Qué hace la persona y qué hace Terraform

El propietario crea la cuenta Microsoft/Azure, activa MFA, registra facturación, convierte la
suscripción a Pay-As-You-Go, selecciona la suscripción en Azure CLI y autoriza cada `apply`. Una
suscripción Azure Free Trial no es suficiente para crear el workspace sin convertirla primero.

Después de ese bootstrap, no se crea manualmente el Resource Group ni el workspace Dev: Terraform
los declara y administra. Tampoco se usa Terraform para desplegar cada notebook. Terraform mantiene
infraestructura y permisos de vida larga; el Bundle mantiene código y recursos de aplicación.

Terraform se divide en dos capas. `infra/azure/dev` crea el resource group y workspace. El presupuesto
puede administrarse opcionalmente con `manage_budget = true`, pero se deja desactivado por defecto
porque el presupuesto inicial del laboratorio ya se creó en Azure Portal;
`infra/databricks/dev` configura OIDC, permisos, Unity Catalog y carpetas normales del workspace. El state comienza local
y permanece ignorado por Git; se migrará a Azure Storage antes de añadir QA.

Cuando Terraform administra un presupuesto, se define en la moneda de facturación de Azure. Las alertas
no detienen recursos: al
final de cada sesión se revisan jobs, cómputo y Cost Analysis.

## Controles de calidad y seguridad

Como mínimo, el pipeline debe incluir:

- `ruff` para lint y formato de Python.
- `sqlfluff` para lint de SQL, con dialecto configurado explícitamente.
- `pytest` para pruebas unitarias.
- Validación de YAML y de los workflows.
- Detección de secretos antes del merge.
- Dependencias fijadas y actualización controlada de acciones.
- Acciones de terceros fijadas a un SHA completo en workflows productivos.
- Concurrencia por entorno para impedir dos despliegues simultáneos.
- Timeouts, permisos explícitos y `permissions` mínimos en GitHub Actions.
- Pasos idempotentes: una reejecución no debe duplicar ni corromper recursos.

## Convenciones operativas

- `main` debe permanecer desplegable.
- Los cambios de emergencia también pasan por PR y quedan documentados.
- Dev y QA pueden editarse para debugging, pero el siguiente despliegue elimina todo drift y Git prevalece.
- Prod no se edita manualmente salvo procedimiento de emergencia; cualquier corrección vuelve después a Git.
- No se promueve una rama distinta por entorno. Se promueve el mismo commit inmutable.
- Un fallo en QA detiene Prod automáticamente.
- El rollback consiste en volver a promover una versión conocida y aprobada, no en editar Prod.

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) antes de abrir un PR y registra los cambios relevantes en [CHANGELOG.md](CHANGELOG.md).
