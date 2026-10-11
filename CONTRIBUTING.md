# Guía de contribución

Gracias por contribuir. Este proyecto utiliza desarrollo basado en una rama principal protegida y promoción por versiones. El objetivo es que `main` siempre sea desplegable y que QA y Prod reciban exactamente el código validado.

## Estrategia de ramificación

### Ramas permanentes

- `main`: única rama permanente, protegida y fuente de las versiones desplegables.
- No se mantienen ramas `develop`, `qa` o `prod`. Los entornos representan etapas de promoción, no líneas de código diferentes.

### Ramas de trabajo

Crea ramas cortas desde un `main` actualizado:

- `feature/<descripcion>` para funcionalidad nueva.
- `fix/<descripcion>` para correcciones.
- `docs/<descripcion>` para documentación.
- `chore/<descripcion>` para mantenimiento.
- `hotfix/<descripcion>` para una corrección urgente que igualmente requiere PR.

Ejemplo:

```bash
git switch main
git pull --ff-only
git switch -c feature/agregar-ingesta-clientes
```

Evita ramas de larga duración. Sincroniza tu rama con `main` antes de solicitar la revisión final y resuelve los conflictos localmente.

## Ciclo de Pull Request y Dev

Todo cambio llega a `main` mediante Pull Request:

1. Desarrolla en una rama de trabajo.
2. Ejecuta linters y pruebas localmente.
3. Actualiza documentación y `CHANGELOG.md` si el cambio es relevante.
4. Abre el PR usando un título claro y una descripción verificable.
5. CI ejecuta lint, pruebas, controles de seguridad y validación en Dev.
6. Una persona distinta al autor revisa el cambio cuando las reglas del repositorio así lo exijan.
7. Sólo se permite el merge con todos los checks requeridos en verde.
8. Tras el merge, el SHA de `main` se sincroniza/despliega en Dev.

El despliegue usa Databricks Bundles y reconstruye `/Workspace/data/proyecto_test` desde ese SHA.

Se recomienda **squash merge** para conservar un historial legible. El título final debe describir el cambio y ser apto para notas de versión.

## Promoción a QA y Prod

Una versión candidata se identifica con SemVer y un sufijo, por ejemplo `v1.2.0-rc.1`. El tag debe
apuntar a un commit ya integrado en `main` y validado en Dev. QA prueba ese SHA sin modificar Prod.

```bash
git switch main
git pull --ff-only
git tag -a v1.2.0-rc.1 -m "Release candidate v1.2.0-rc.1"
git push origin v1.2.0-rc.1
```

El tag o la publicación de una GitHub Release inicia la promoción:

1. El pipeline resuelve y registra el SHA inmutable del release candidate.
2. Despliega ese SHA en QA.
3. Ejecuta pruebas de integración y notebooks de humo en QA.
4. Si QA falla, el pipeline se detiene; Prod no comienza.
5. Si QA falla, se corrige mediante un nuevo PR y se crea `v1.2.0-rc.2`; no se mueve el tag anterior.
6. Si QA pasa, se crea el tag final `v1.2.0` sobre exactamente el mismo SHA.
7. El job de Prod espera la aprobación configurada en el GitHub Environment `prod`.
8. Prod recibe exactamente el mismo SHA validado en QA.
9. Se ejecutan verificaciones de humo no destructivas y se registra el resultado.

No muevas ni reutilices tags publicados. Si una versión tiene un error, crea una nueva versión, por ejemplo `v1.2.1`.

`main` representa código integrado, no necesariamente lo que está en Prod. Prod permanece en el último
tag final aprobado mientras se corrige un candidato fallido. Sólo se crea temporalmente una rama
`release/X.Y` si es necesario estabilizar una versión mientras `main` continúa avanzando.

## Versionado

Este proyecto sigue [Semantic Versioning](https://semver.org/):

- **MAJOR**: cambio incompatible.
- **MINOR**: funcionalidad compatible nueva.
- **PATCH**: corrección compatible.

Mientras el proyecto esté en una fase inicial puede utilizar versiones `0.y.z`. Registra cambios en `CHANGELOG.md` bajo `Unreleased` y muévelos a una sección versionada al publicar.

## Requisitos de un Pull Request

La descripción debe incluir:

- propósito y alcance;
- issue relacionado, si existe;
- archivos, notebooks o procesos afectados;
- evidencia de lint y pruebas;
- impacto esperado por entorno;
- riesgos, migración y plan de rollback;
- capturas o logs sanitizados cuando aporten valor.

Lista mínima:

- [ ] El cambio es pequeño y enfocado.
- [ ] No contiene secretos, PII ni datos productivos.
- [ ] `ruff check .` y `ruff format --check .` pasan cuando aplica.
- [ ] `sqlfluff lint sql/` pasa cuando aplica.
- [ ] `pytest` pasa cuando aplica.
- [ ] Los notebooks no contienen salidas sensibles o innecesarias.
- [ ] La documentación y las pruebas están actualizadas.
- [ ] `CHANGELOG.md` incluye el cambio visible.
- [ ] Existe un plan de reversión para cambios de riesgo.

## Convenciones para código y notebooks

- Coloca lógica Python reutilizable en `src/` y cúbrela con pruebas.
- Mantén los notebooks como orquestadores delgados y en formato fuente revisable.
- Parametriza catálogo, esquema, rutas y recursos por entorno.
- No fijes en código hosts, IDs de workspace, tokens ni nombres productivos.
- Escribe SQL compatible con el dialecto Databricks configurado en SQLFluff.
- Evita efectos destructivos en pruebas. Usa recursos aislados y limpieza idempotente.

## Debugging manual en Dev y QA

Los desarrolladores pueden editar notebooks y archivos en Dev y QA para investigar un fallo. Esa
edición es un experimento temporal, no un despliegue:

1. reproduce y corrige el problema en el workspace;
2. copia la corrección a una rama `feature/*` o `fix/*`;
3. ejecuta las validaciones y abre un PR;
4. permite que CI/CD vuelva a desplegar el SHA aprobado.

Cada despliegue restaura archivos modificados o eliminados y borra archivos o carpetas que no están
en `proyecto_test/`. No existe sincronización automática workspace → Git. Si no guardas la solución
en una rama antes del siguiente despliegue, se perderá deliberadamente. Prod no permite este flujo.

## Seguridad de la cadena de suministro

- No añadas acciones de GitHub o dependencias sin revisar su origen y necesidad.
- Fija las acciones a SHA completo en workflows productivos.
- Limita `GITHUB_TOKEN` mediante `permissions` explícitos.
- Un workflow de PR no confiable no puede acceder a secretos de despliegue.
- Prefiere OIDC a secretos persistentes y separa la identidad de cada entorno.

## Hotfix y rollback

Un hotfix parte de `main`, pasa por PR y por los mismos checks. Tras el merge se crea una nueva versión PATCH y se promueve normalmente. La urgencia no autoriza cambios manuales sin trazabilidad.

Para revertir una versión:

1. identifica el último tag conocido como estable;
2. vuelve a promover ese SHA mediante el pipeline autorizado;
3. abre un PR que corrija o revierta el cambio en `main`;
4. publica una versión nueva y documenta el incidente.

No reescribas la historia de `main`, no fuerces el push y no alteres un tag ya publicado.
