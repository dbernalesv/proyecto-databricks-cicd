# ADR 0007: Target Bundle Dev compartido y administrado por CI

## Estado

Aceptado.

## Contexto

El primer `bundle validate` autenticado rechazó la configuración porque `mode: development` exige que
las rutas internas y los prefijos incluyan al usuario actual. Esa protección evita colisiones cuando
cada desarrollador despliega su propia copia. En este proyecto existe una única copia Dev compartida:
GitHub Actions despliega siempre con el mismo service principal y Git prevalece sobre el drift manual.

## Decisión

El target llamado `dev` no declara un modo de despliegue predefinido. Los modos de Bundle son
opcionales y no equivalen necesariamente al nombre del ambiente. Se mantienen explícitamente:

- `default: true`;
- el prefijo de recursos `[dev] `;
- la raíz protegida `/Workspace/.cicd/proyecto_test/dev`;
- la concurrencia del workflow por ambiente;
- la reconciliación estricta de `/Workspace/data/proyecto_test` contra el SHA.

No se usa `mode: production` como solución incidental. Ese modo añade controles de `run_as` y permisos
que deben diseñarse y probarse de forma explícita, no introducirse sólo para superar una validación.

## Consecuencias

El Bundle puede usar una ruta estable y compartida sin interpolar un usuario. Los nombres mantienen un
prefijo legible de Dev. La exclusión mutua depende tanto del lock estándar del Bundle como del grupo de
`concurrency` de GitHub Actions. Si en el futuro cada desarrollador necesita una copia aislada, se
creará otro target personal con `mode: development` y rutas basadas en
`${workspace.current_user.short_name}`.
