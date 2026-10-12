# 01 — Alta de Azure y control de costos

Esta guía se ejecuta antes de Terraform. Abrir una suscripción implica aceptar facturación; por eso es
una acción manual del propietario y nunca debe automatizarse con credenciales compartidas.

## Estado confirmado del laboratorio

El 9 de octubre de 2026 se completó el bootstrap inicial con este resultado:

- suscripción Pay-As-You-Go `Azure_Databricks_CICD_Lab` activa;
- región Dev seleccionada: East US 2 (`eastus2`);
- presupuesto mensual `budget-proyecto-databricks-dev` de USD 58;
- alertas de costo real al 50 %, 75 %, 90 % y 100 %;
- Resource Group y workspace Dev creados mediante Terraform;
- QA y Prod todavía no aprovisionados.

Los IDs completos, correos de alerta y datos de facturación se conservan fuera de la documentación
versionada. Esta sección registra el resultado operativo, no reemplaza las variables locales.

## Alta segura

1. Crea o reutiliza una cuenta Microsoft personal dedicada al laboratorio.
2. Crea la cuenta gratuita y conviértela a **Pay-As-You-Go** antes de intentar crear Azure Databricks;
   una suscripción Free Trial no admite el workspace requerido por este laboratorio.
3. Activa MFA para la cuenta.
4. Copia únicamente el `Subscription ID`; no compartas tokens, contraseñas ni datos de tarjeta.
5. Confirma que tu usuario tiene `Owner` o `Contributor` y permisos para presupuestos.
6. Comprueba disponibilidad de Azure Databricks y cuota en la región candidata. Para este laboratorio
   se validó y seleccionó `eastus2`; vuelve a revisar disponibilidad y precios antes de cambiarla.

## Azure CLI, tenant y MFA

El primer `az login` puede responder con `AADSTS50076` cuando MFA requiere interacción adicional. No
copies códigos temporales ni tokens en archivos o capturas. Usa Device Code y selecciona después la
suscripción explícitamente:

```powershell
az login `
  --tenant "<TENANT_ID>" `
  --use-device-code

az account set --subscription "<SUBSCRIPTION_ID>"

az account show `
  --query "{name:name, id:id, state:state, tenantId:tenantId}" `
  --output table
```

Antes de ejecutar Terraform Azure, confirma que el nombre, estado y tenant corresponden a la
suscripción del laboratorio. Un login exitoso en un tenant no garantiza que la identidad vea una
suscripción.

## Dos identidades durante el bootstrap

El alta real mostró dos contextos diferentes que no deben confundirse:

1. La **cuenta propietaria de Azure** ve la suscripción y autoriza Terraform sobre Resource Groups y
   el workspace.
2. El **usuario organizacional de Microsoft Entra ID** accede al Databricks Account Console y
   configura objetos a nivel de cuenta. Puede aparecer como una cuenta a nivel de tenant sin
   suscripciones Azure, lo cual es válido para esa función.

La cuenta Microsoft personal fue rechazada por el Account Console con `AADSTS500200`, porque esa
aplicación requería una identidad organizacional. Se creó un usuario organizacional de bootstrap y se
le concedió temporalmente Global Administrator.

> **Acción de seguridad posterior al bootstrap:** retirar Global Administrator al usuario
> organizacional. Ese rol no es necesario para la operación cotidiana y retirarlo no elimina el
> usuario, el workspace, el service principal ni los permisos específicos de Databricks.

## S/200 no es la moneda del budget

Azure registra el presupuesto en la moneda de facturación de la suscripción. Antes del primer plan:

1. abre **Cost Management + Billing**;
2. identifica la moneda de facturación;
3. convierte S/200 usando un margen conservador;
4. coloca ese valor en `budget_amount`.

La plantilla usa `50` como valor cauteloso de ejemplo. En la suscripción real se creó manualmente un
budget de USD 58. Las alertas al 50 %, 75 %, 90 % y 100 % no detienen servicios automáticamente. El
control real consiste en cómputo serverless/efímero, revisar costos y detener el cómputo cuando termine
la práctica.

El budget manual no se duplica desde Terraform: `manage_budget` permanece desactivado. Sólo debe
activarse si se decide importar o sustituir deliberadamente el presupuesto existente.

## Ritual de cierre de cada laboratorio

- Revisa **Jobs & Pipelines** y confirma que no existan runs en ejecución.
- Revisa **Compute** y confirma que todos los clústeres estén `TERMINATED`.
- Revisa **SQL Warehouses** y confirma que estén `STOPPED`.
- Comprueba que no haya endpoints de serving, pools o recursos de red permanentes inesperados.
- Revisa el costo diario y el forecast del mes.
- Conserva el workspace sin actividad sólo si su costo observado lo permite.
- No uses `terraform destroy` como rutina de apagado: para detener el costo diario normalmente basta
  con detener el cómputo.
- Si decides eliminar el laboratorio completo, ejecuta primero un `terraform plan -destroy`, revisa
  la lista y solicita autorización explícita antes de aplicar la destrucción en la capa Databricks y
  finalmente en la capa Azure.
- Confirma en Azure Portal que no quedaron recursos fuera de Terraform.

### Evidencia del cierre del 9 de octubre de 2026

La consulta de sólo lectura a las APIs de Databricks confirmó:

```text
Clústeres registrados:         1
Clústeres en ejecución:        0
SQL warehouses registrados:   1
SQL warehouses en ejecución:  0
Jobs activos:                  0
```

Por este motivo no fue necesario eliminar el workspace ni el Resource Group durante la noche. El
workspace sin cómputo activo puede producir cargos pequeños de almacenamiento o red, por lo que Cost
Analysis sigue siendo la evidencia final y puede mostrar consumo con retraso.

> Un presupuesto es una alarma, no un freno. Ante un gasto inesperado, detén jobs/cómputo y revisa
> Cost Analysis antes de continuar.

### Evidencia de costos del 11 de octubre de 2026

Cost Management mostró USD 1.96 acumulados: USD 1.76 de NAT Gateway, USD 0.20 de Virtual Network y
USD 0.00 de Storage en `rg-databricks-cicd-dev-managed`. Los datos pueden aparecer con retraso.

El NAT Gateway pertenece a la red administrada que Azure Databricks crea para Secure Cluster
Connectivity. Su costo continúa mientras el workspace existe, aunque los clústeres estén apagados.
El costo acumulado observado después aumentó a USD 2.42. Dev permanece estable y QA se conservará
durante una ventana corta y explícita del laboratorio para repetir pruebas de release candidates. No
se crea por PR y se destruirá al finalizar la fase QA o si el forecast amenaza el budget. Prod no se
creará hasta medir el costo conjunto. En un entorno empresarial, la permanencia de QA responde a
disponibilidad, integraciones y gobierno, no únicamente al presupuesto.

## Frontera manual y automática

La cuenta, MFA, aceptación de términos, método de pago, presupuesto inicial, selección de suscripción
y autorización del primer `apply` son acciones humanas. Después, Terraform crea el Resource Group y
el workspace Dev. No crees manualmente recursos administrados por Terraform porque aparecería drift
entre Azure y el state.
