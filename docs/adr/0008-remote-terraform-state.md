# ADR 0008: backend remoto Terraform con autenticación Entra

- Estado: Aceptado
- Fecha: 2026-10-11

## Contexto

Dev se aprovisionó con states locales separados para Azure y Databricks. Esto facilitó el aprendizaje
inicial, pero un archivo local depende de un solo equipo, no coordina escritores y no es apropiado antes
de incorporar más entornos u operadores.

## Decisión

Crear una pila independiente `infra/bootstrap/tfstate` que administre una cuenta Azure Storage y un
contenedor privado. El state de esta pila bootstrap permanece local como excepción documentada.

Migrar los states Dev a blobs distintos, `dev/azure.tfstate` y `dev/databricks.tfstate`. Autenticar el
backend con Microsoft Entra y Azure CLI, deshabilitar claves compartidas y limitar al operador el rol
`Storage Blob Data Contributor` al contenedor. Activar versionado y retención de borrados por 14 días.

Cuando las capas necesitan identidades administrativas distintas, el bootstrap acepta Object IDs
adicionales. La cuenta personal opera Azure y el usuario organizacional opera Databricks; ambos se
autentican con Entra y sólo las identidades declaradas pueden abrir y bloquear el backend.

Se mantiene temporalmente acceso de red pública para permitir la administración desde una conexión
doméstica dinámica. El contenedor no es público y todas las operaciones de datos requieren RBAC. Antes
de un uso corporativo se evaluará Private Endpoint o un runner dentro de una red controlada.

## Consecuencias

- Terraform dispone de bloqueo y de una copia central cifrada y recuperable.
- Las capas conservan ciclos de vida y radios de impacto separados.
- No se introducen Storage keys, SAS ni secretos persistentes.
- El bootstrap local requiere custodia y respaldo seguro del equipo.
- La cuenta Storage añade un costo operativo pequeño y debe permanecer bajo el budget.
- La migración se hace de una capa por vez y sólo se acepta con `state list` completo y plan estable.

## Resultado

El 11 de octubre de 2026 se creó el backend y se migraron primero Azure Dev y después Databricks Dev.
Cada identidad demostró acceso por Entra, ambos blobs conservaron el tamaño de su respaldo local y los
planes posteriores devolvieron `No changes`. No se modificaron recursos administrados durante la
migración.
