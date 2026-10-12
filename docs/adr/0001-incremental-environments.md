# ADR 0001: Aprovisionamiento incremental por entorno

- Estado: Aceptado
- Fecha: 2026-10-07

## Decisión

Crear sólo Dev. QA se crea después de validar CI/CD Dev y Prod después de validar la promoción QA.

## Motivo

Reduce costo y superficie operativa dentro del presupuesto educativo de S/200. Mantener código
Terraform preparado no genera costo; crear recursos sí.

## Actualización 2026-10-11

Dev completó CI/CD, reconciliación, smoke test y migración de state. Cost Management mostró que el NAT
Gateway administrado es el principal costo base. En ese momento se decidió que QA fuera efímero: se
crearía para probar un release candidate y se destruiría después de recopilar evidencia. Esta decisión
fue reemplazada posteriormente por el ADR 0010.

## Actualización 2026-10-11 (decisión posterior)

El ADR 0010 reemplaza la modalidad efímera: QA se creará una vez y permanecerá durante su fase de
prácticas para permitir promociones y pruebas repetibles. Tendrá revisión frecuente de costos y una
fecha de teardown. El aprovisionamiento sigue siendo incremental y Prod continúa bloqueado hasta
validar QA y medir el costo conjunto.

