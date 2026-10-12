# ADR 0010: QA persistente durante la fase de laboratorio

- Estado: Aceptado
- Fecha: 2026-10-11
- Reemplaza: ADR 0009

## Contexto

Dev está validado de extremo a extremo y Cost Management registra USD 2.42 acumulados. Crear y
destruir un workspace QA por Pull Request añadiría latencia, riesgo de recursos huérfanos y poco valor:
un PR todavía no es un release candidate. Omitir QA reduciría el aprendizaje de promoción inmutable,
separación de identidades, permisos y pruebas previas a Prod.

El NAT Gateway de cada workspace clásico genera costo horario aunque no haya clústeres activos. Por
eso «persistente» significa durante la fase QA del laboratorio, no indefinidamente ni durante todo el
mes.

## Decisión

QA se aprovisionará una sola vez después de estabilizar Dev y permanecerá disponible durante las
prácticas de release candidates. Tendrá workspace, state remoto, identidad OIDC, GitHub Environment,
catálogo/esquema y permisos propios. Sólo recibirá tags `vX.Y.Z-rc.N` asociados a un SHA de `main` ya
validado en Dev.

Los Pull Requests continuarán ejecutando CI sin credenciales cloud y no crearán workspaces. Al cerrar
la fase QA, o si el forecast amenaza el budget de USD 58, se revisarán planes de destrucción y se
eliminará primero la configuración Databricks y después la infraestructura Azure.

## Consecuencias

- Las pruebas QA se pueden repetir sin esperar un nuevo aprovisionamiento.
- Se practica una arquitectura más cercana a una plataforma empresarial.
- Dev y QA pueden generar simultáneamente costos base de red.
- Cost Analysis se revisará después de cada sesión y se definirá una fecha de teardown.
- No se creará Prod hasta medir el costo conjunto de Dev y QA.
- En producción real, la permanencia y el aislamiento se decidirían por disponibilidad, integración,
  regulación y recuperación, no únicamente por el presupuesto del laboratorio.
