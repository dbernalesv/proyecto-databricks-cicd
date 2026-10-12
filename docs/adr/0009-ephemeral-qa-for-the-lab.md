# ADR 0009: QA efímero para el laboratorio

- Estado: Aceptado
- Fecha: 2026-10-11

## Contexto

Dev está validado de extremo a extremo. Cost Management registró USD 1.96, principalmente por el NAT
Gateway de la red administrada. Un segundo workspace permanente duplicaría parte del costo base aun
sin ejecutar pruebas y reduciría demasiado el margen del budget mensual de USD 58.

## Decisión

QA conservará aislamiento real, identidad OIDC, GitHub Environment y state propios, pero su workspace
será efímero. Terraform lo creará para probar un tag `vX.Y.Z-rc.N`; después del despliegue, pruebas y
captura de evidencia, se destruirá primero la configuración Databricks y luego la infraestructura
Azure. Los tags, logs, resultados y state remoto permanecen.

Prod queda fuera de alcance hasta medir una sesión QA completa. En una plataforma empresarial, QA
normalmente sería permanente; esta decisión responde exclusivamente al presupuesto del laboratorio.

## Consecuencias

- Se conserva aislamiento entre Dev y QA sin pagar un workspace QA todo el mes.
- Cada sesión debe incluir planes de creación y destrucción revisados y autorizados.
- QA tarda algunos minutos en estar disponible y no conserva debugging manual después del teardown.
- Las pruebas deben crear datos temporales y no depender de estado previo.
- Un fallo de QA nunca modifica Prod y requiere un nuevo release candidate.
