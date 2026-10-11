# Reglas para agentes y colaboradores automatizados

Estas instrucciones aplican a todo el repositorio. Su propósito es mantener un proyecto didáctico, seguro, reproducible y apto para evolucionar hacia producción.

## Principios obligatorios

1. **Git es la fuente de verdad.** Todo cambio desplegable debe quedar versionado, revisado y asociado a un commit.
2. **Seguridad por defecto.** Antes de proponer o modificar código, configuración o workflows, evalúa exposición de secretos, permisos, integridad de dependencias y aislamiento entre entornos.
3. **Mínimo privilegio.** Limita `permissions` de GitHub Actions y permisos de identidades Databricks al mínimo necesario para cada job y entorno.
4. **Promoción inmutable.** Dev, QA y Prod deben recibir el mismo SHA. Los cambios manuales de debugging en Dev/QA nunca se promueven.
5. **Automatización idempotente.** Los comandos deben poder reintentarse sin crear duplicados ni dejar un estado inconsistente.
6. **Explicaciones didácticas.** Documenta decisiones y comandos con lenguaje claro para un Data Engineer junior, sin ocultar los riesgos ni simplificar la seguridad.

## Credenciales y datos sensibles

- Nunca guardes tokens, contraseñas, claves privadas, secretos de clientes, cadenas de conexión ni archivos `.env` en texto plano.
- Nunca inventes valores que parezcan credenciales reales. Usa marcadores evidentes, como `${{ secrets.DATABRICKS_CLIENT_SECRET }}`.
- Prefiere OIDC/workload identity federation. Si un secreto es inevitable, almacénalo en GitHub Environment Secrets o Azure Key Vault, limita su alcance y documenta su rotación.
- No imprimas secretos ni objetos completos de autenticación en logs. Evita modos de depuración que puedan revelar cabeceras o variables.
- Antes de finalizar un cambio, busca credenciales accidentales y revisa que `.gitignore` cubra archivos locales sensibles.
- No uses Personal Access Tokens como solución productiva ni compartas una identidad entre Dev, QA y Prod.
- Trata los notebooks y datos de prueba como código: no incluyas PII, datos productivos ni resultados embebidos sensibles.

## GitHub Actions y Databricks

- Estructura los pipelines con componentes oficiales de Databricks:
  - `databricks/setup-cli` para instalar la CLI oficial y administrar operaciones soportadas.
  - `databricks/run-notebook` para pruebas controladas cuando no exista un Job administrado por Bundle.
- Prefiere la CLI oficial para ejecuciones idempotentes y autenticación OIDC. Usa
  `databricks/run-notebook` sólo cuando su modelo de autenticación y mantenimiento resulte adecuado.
- Consulta la documentación oficial antes de fijar sintaxis o versiones. En workflows productivos, fija las acciones a un SHA completo y deja un comentario con la versión legible.
- Define `permissions` explícitos por workflow o job. Para OIDC, concede `id-token: write` sólo al job que lo requiera y conserva `contents: read` cuando sea suficiente.
- Usa GitHub Environments separados: `dev`, `qa` y `prod`. Los secretos y variables son específicos de cada uno.
- Configura protección y aprobación manual para Prod. Ningún job de Prod debe ejecutarse si QA o sus pruebas fallan.
- Usa `concurrency` por entorno, `timeout-minutes` y manejo explícito de errores.
- No ejecutes código de un PR no confiable con secretos. Evita `pull_request_target` salvo que exista una justificación y revisión de seguridad específica.
- Valida que la referencia promovida sea un SHA o tag inmutable. No despliegues a Prod desde el estado mutable de una rama.
- Usa Declarative Automation Bundles para desplegar archivos, notebooks, Jobs y Pipelines.
- Mantén `/Workspace/data/proyecto_test` como carpeta normal y el estado del Bundle bajo `/Workspace/.cicd`.
- Dev y QA permiten edición manual para debugging; antes de redesplegar, recuerda que Git prevalece y el drift será eliminado.
- Prod no permite edición manual a desarrolladores.
- Toda reconciliación destructiva debe validar una ruta exacta `/Workspace/data/<proyecto>`, rechazar raíces amplias y probarse antes de usarse.
- No sincronices automáticamente cambios workspace → Git ni conserves archivos remotos ausentes del SHA.

## Calidad obligatoria

Antes de considerar completo un cambio, ejecuta o añade las validaciones aplicables:

```bash
ruff check .
ruff format --check .
sqlfluff lint sql/
pytest
```

- Python: usa `ruff` para lint y formato, tipos cuando se configure un verificador, y `pytest` para pruebas.
- SQL: usa `sqlfluff` con el dialecto Databricks configurado; evita SQL generado que no pueda revisarse o probarse.
- YAML: valida sintaxis y estructura de GitHub Actions.
- Shell/PowerShell: activa manejo estricto de errores y evita interpolaciones inseguras.
- Añade pruebas para comportamiento nuevo y para correcciones de defectos.
- No silencies una regla de lint globalmente para hacer pasar CI; justifica excepciones mínimas junto al código.

Si una herramienta todavía no está configurada, crea primero su configuración reproducible o declara con claridad que la validación está pendiente. Nunca afirmes que una prueba pasó si no fue ejecutada.

## Reglas de edición

- Lee `README.md`, `CONTRIBUTING.md` y los archivos afectados antes de modificar el repositorio.
- Conserva cambios ajenos que no formen parte de la tarea.
- Mantén PRs y commits pequeños y enfocados; evita refactorizaciones no solicitadas.
- Actualiza documentación, pruebas y `CHANGELOG.md` cuando el cambio sea visible para usuarios u operadores.
- Usa nombres descriptivos y configuración por entorno; no codifiques hosts, IDs o rutas específicas directamente en scripts compartidos.
- No realices despliegues, merges, tags o cambios en servicios externos sin autorización explícita.
- No ejecutes comandos destructivos ni sobrescribas datos o configuración sin verificar el objetivo y obtener autorización cuando corresponda.

## Lista de comprobación antes de entregar

- [ ] No hay secretos ni datos sensibles versionados o expuestos en logs.
- [ ] Los permisos de GitHub y Databricks son mínimos y explícitos.
- [ ] Python, SQL y YAML pasan sus validaciones aplicables.
- [ ] Las pruebas relevantes se ejecutaron y el resultado se informó con precisión.
- [ ] El flujo preserva el mismo commit entre Dev, QA y Prod.
- [ ] El workspace final coincide con el manifiesto del SHA y no conserva drift manual.
- [ ] El despliegue es idempotente y tiene timeout/concurrencia adecuados.
- [ ] La documentación y el changelog reflejan el cambio.
- [ ] Las acciones están fijadas de forma segura y proceden de publicadores confiables.
