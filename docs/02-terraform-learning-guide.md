# 02 — Terraform explicado y primer despliegue Dev

Terraform describe infraestructura deseada en archivos `.tf`. El **provider** traduce esa descripción
a APIs; un **resource** es un objeto administrado; una **variable** es una entrada; un **output** expone
un dato útil; un **module** reutiliza una composición; y el **state** relaciona la configuración con
objetos reales.

## Por qué hay dos carpetas/state

- `infra/azure/dev`: crea el resource group, workspace y presupuesto mediante AzureRM.
- `infra/databricks/dev`: configura la cuenta/workspace ya existente mediante el provider Databricks.

La segunda API no está disponible hasta que Azure termina la primera. Separar estados hace explícita
esa dependencia y permite destruir configuración de Databricks antes que el workspace.

## Comandos y significado

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
```

- `init`: descarga providers y prepara el backend; no crea infraestructura.
- `fmt`: normaliza el estilo; `-check` no modifica archivos.
- `validate`: comprueba estructura y tipos, no prueba permisos reales.
- `plan`: compara configuración, state y nube. Siempre se revisa.
- `apply`: ejecuta exactamente el plan guardado.
- `destroy`: elimina recursos administrados; se revisa primero con `plan -destroy`.

## Primer apply: capa Azure

1. Instala Terraform y Azure CLI desde sus fuentes oficiales.
2. Ejecuta `az login` y selecciona la suscripción correcta.
3. Copia `terraform.tfvars.example` como `terraform.tfvars`; está ignorado por Git.
4. Ajusta moneda del budget, fecha al primer día del mes, región, alias y correo.
5. Desde `infra/azure/dev`, ejecuta los cinco comandos anteriores.
6. Guarda los outputs; ninguno es una contraseña.

Si Terraform no está instalado globalmente, puede invocarse el binario local sin modificar el `PATH`:

```powershell
& ".\.cache\terraform-1.13.4\terraform.exe" `
  -chdir="infra/azure/dev" `
  plan -input=false
```

El primer plan real del laboratorio propuso únicamente el Resource Group y el workspace:

```text
Plan: 2 to add, 0 to change, 0 to destroy.
```

Después del `apply`, se confirmó el workspace en Azure Portal y un nuevo plan mostró `No changes`.
Esa segunda ejecución es la prueba básica de idempotencia de la capa Azure.

No ejecutes `apply` si el plan contiene QA, Prod, cómputo clásico, una región inesperada o recursos que
no puedas explicar.

## Segundo apply: capa Databricks

1. Abre el workspace y confirma que Unity Catalog está habilitado.
2. Obtén el Account ID y autentícate interactivamente como administrador con la CLI Databricks.
3. Identifica el catálogo administrado creado automáticamente para el workspace con Default Storage.
4. Copia y completa `infra/databricks/dev/terraform.tfvars.example`, incluidos el catálogo, grupo y usuario desarrollador.
5. Ejecuta `init`, `fmt -check`, `validate`, `plan` y `apply` desde esa carpeta.
6. El plan crea el grupo, membresía, service principal Databricks, política OIDC, asignaciones al
   workspace, entitlement mínimo, esquema, `/Workspace/data/proyecto_test` y la ruta protegida de
   estado del Bundle.

El Account ID, Workspace ID y Application/Client ID representan objetos distintos. Deben almacenarse
en variables con nombres explícitos y nunca inferirse unos de otros. Para el repositorio GitHub,
`github_owner` recibe el usuario u organización y `github_repository` sólo el nombre del repositorio,
no la URL completa. `github_owner_id` y `github_repository_id` conservan las identidades numéricas
inmutables que GitHub incluye en el claim OIDC de repositorios nuevos. Estos IDs son metadatos públicos,
no credenciales, pero deben coincidir exactamente con el token emitido.

El catálogo administrado del workspace se consulta como un `data` source y no se recrea. Esto permite
usar Default Storage sin introducir una cuenta de almacenamiento propia sólo para el laboratorio. El
service principal recibe `USE_CATALOG` en ese catálogo y permisos de escritura únicamente en el esquema
`cicd`, conservando mínimo privilegio.

La asignación `USER` a nivel de cuenta hace visible el service principal en el workspace, pero no
garantiza por sí sola que pueda llamar sus APIs. Por eso Terraform resuelve su ID SCIM local y administra
un `databricks_entitlements` separado con `workspace_access = true`. Se mantienen en `false` el acceso
SQL, la creación irrestricta de clústeres y la creación de instance pools. Los permisos sobre carpetas,
catálogo y esquema siguen siendo recursos independientes: un entitlement permite entrar al workspace,
pero no autoriza automáticamente a modificar todos sus objetos.

Terraform no despliega notebooks en cada cambio. Administra infraestructura y permisos de vida larga;
`databricks bundle deploy` administra archivos y Jobs desde GitHub Actions.

## Recuperación del primer apply Databricks

El primer `apply` real creó correctamente identidades, grupo y carpetas, pero falló al intentar crear
un catálogo adicional sin `storage_root`. El workspace nuevo ya incluía un catálogo administrado
respaldado por Default Storage.

La recuperación segura fue:

1. no borrar el state ni eliminar los recursos que la API ya había confirmado;
2. inspeccionar el catálogo administrado existente;
3. cambiar el catálogo nuevo por `data.databricks_catalog.workspace`;
4. crear únicamente el esquema `cicd` y sus grants mínimos;
5. generar un plan de recuperación y revisar sólo los recursos pendientes;
6. aplicar el plan y ejecutar nuevamente `terraform plan` hasta obtener `No changes`.

Terraform confirma recursos individualmente. Un `apply` fallido no implica que todo haya sido
revertido; el state conserva lo creado y permite continuar después de corregir la causa. El detalle de
la decisión está en [ADR 0005](adr/0005-workspace-catalog-default-storage.md).

## Autenticación administrativa local

La capa Databricks se ejecutó con el usuario organizacional del tenant. El login puede mostrarse como
cuenta a nivel de tenant sin suscripción, porque la autenticación se usa contra Databricks y no para
crear recursos Azure:

```powershell
az login `
  --tenant "<TENANT_ID>" `
  --use-device-code `
  --allow-no-subscriptions

az account get-access-token `
  --resource "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d" `
  --output none
```

`--output none` evita imprimir el token. No copies el token a `terraform.tfvars`, logs, issues o
variables persistentes de GitHub.

## Backend remoto en Azure Storage

El **state** permite que Terraform relacione cada bloque de configuración con el recurso real. Puede
contener identificadores y datos devueltos por APIs, por lo que no debe versionarse, enviarse por correo
ni pegarse en un issue. El **backend** determina dónde se guarda y cómo se bloquea ese state.

El laboratorio comenzó con state local para reducir conceptos durante el primer aprovisionamiento.
Antes de QA se migra a Azure Blob Storage porque ofrece cifrado en reposo, versionado, recuperación de
borrados y bloqueo nativo para evitar que dos operaciones escriban simultáneamente.

### Por qué existe una pila bootstrap

El backend debe existir antes de que Terraform pueda usarlo. `infra/bootstrap/tfstate` resuelve ese
problema de arranque y crea:

- un Resource Group compartido y etiquetado;
- una cuenta StorageV2 `Standard_LRS`, suficiente para archivos de state pequeños;
- un contenedor privado `tfstate` con versionado y retención de 14 días;
- una asignación `Storage Blob Data Contributor` al usuario que ejecuta el bootstrap, limitada al
  contenedor.

Si Azure y Databricks requieren identidades administrativas diferentes, añade el Object ID del
operador organizacional en `additional_state_operator_object_ids`. Terraform concede el mismo rol de
datos al contenedor sin almacenar contraseñas. Esto es necesario porque primero se abre y bloquea el
backend y después se autentica el provider que administra los recursos. En el laboratorio, la cuenta
personal opera Azure y el usuario organizacional opera la cuenta Databricks.

La cuenta deshabilita claves compartidas, fuerza autenticación Microsoft Entra y TLS 1.2 como mínimo.
Mantiene acceso por red pública para que el laboratorio funcione desde una IP doméstica dinámica; esto
no significa acceso anónimo: el contenedor es privado y exige RBAC. En una plataforma corporativa se
añadiría firewall, runner con red controlada o Private Endpoint.

El pequeño state de bootstrap permanece local e ignorado por Git. Es una excepción consciente: no
puede alojarse en el backend que él mismo debe crear. Se conserva protegido y sólo administra estos
cuatro objetos. Los states de trabajo sí quedan separados:

```text
tfstate/
└── dev/
    ├── azure.tfstate
    └── databricks.tfstate
```

Separar las claves evita mezclar ciclos de vida. El workspace puede existir aunque se repare la
configuración Databricks, y durante una retirada se destruye primero Databricks y luego Azure.

### Crear el backend

Primero inicia sesión con el propietario de la suscripción y confirma el contexto; no continúes si el
ID o tenant no son los esperados:

```powershell
az login --tenant "<TENANT_ID>" --use-device-code
az account set --subscription "<SUBSCRIPTION_ID>"
az account show --query "{name:name,id:id,tenantId:tenantId,user:user.name}" --output table
```

Copia `infra/bootstrap/tfstate/terraform.tfvars.example` como `terraform.tfvars` y completa
suscripción, región, alias y cualquier operador adicional. Los Object IDs no son secretos, pero el
archivo operativo permanece local. Luego ejecuta desde la raíz:

```powershell
& ".\.cache\terraform-1.13.4\terraform.exe" -chdir="infra/bootstrap/tfstate" init
& ".\.cache\terraform-1.13.4\terraform.exe" -chdir="infra/bootstrap/tfstate" fmt -check
& ".\.cache\terraform-1.13.4\terraform.exe" -chdir="infra/bootstrap/tfstate" validate
& ".\.cache\terraform-1.13.4\terraform.exe" -chdir="infra/bootstrap/tfstate" plan -out=tfstate.tfplan
```

Revisa que el plan sólo contenga el Resource Group, Storage Account, contenedor y asignación RBAC.
`apply` se ejecuta únicamente después de esa revisión y autorización explícita. La cuenta tiene un
costo pequeño pero no nulo; el budget continúa siendo el control de alerta.

### Migrar los states existentes

Después del `apply`, copia los dos archivos `.tfbackend.example` de `infra/backend/` quitando el
sufijo `.example`. Completa el nombre de Storage mostrado por el output y los IDs correctos. Los
archivos reales `*.tfbackend` están ignorados para no convertir parámetros operativos en configuración
compartida; no deben contener contraseñas, claves ni SAS.

Migra una capa a la vez:

```powershell
& ".\.cache\terraform-1.13.4\terraform.exe" -chdir="infra/azure/dev" init `
  -migrate-state -backend-config="..\..\backend\dev.azure.tfbackend"

& ".\.cache\terraform-1.13.4\terraform.exe" -chdir="infra/azure/dev" state list
& ".\.cache\terraform-1.13.4\terraform.exe" -chdir="infra/azure/dev" plan -input=false
```

Sólo si la capa Azure conserva todos sus recursos y muestra `No changes`, repite el procedimiento para
Databricks usando `dev.databricks.tfbackend`. La propagación de RBAC puede tardar algunos minutos; un
`403` inmediato no se soluciona habilitando claves, sino esperando y comprobando identidad y alcance.

Terraform puede crear copias locales durante la migración. Consérvalas temporalmente, siempre
ignoradas por Git, hasta comprobar ambos blobs, `state list` y los dos planes estables. La migración no
crea, cambia ni destruye recursos administrados: mueve la ubicación del state. Aun así es una operación
delicada y nunca se interrumpe ni se repite a ciegas.

La configuración usa `use_azuread_auth = true` y `use_cli = true`. La sesión de Azure CLI obtiene
tokens temporales; no se almacenan claves de Storage, SAS, client secrets ni tokens en el repositorio.

## Destrucción segura

```bash
terraform plan -destroy -out=destroy.tfplan
terraform apply destroy.tfplan
```

Ejecuta primero `infra/databricks/dev` y después `infra/azure/dev`. El catálogo administrado del
workspace no pertenece al state de esta capa; el esquema tiene `force_destroy = false`, por lo que
Terraform se negará a eliminarlo si contiene datos.

La destrucción completa no es el mecanismo habitual para cerrar una jornada. Si clústeres, warehouses
y jobs están detenidos, conserva el workspace y revisa Cost Analysis. Usa `destroy` sólo cuando exista
una decisión explícita de retirar el laboratorio y se haya revisado el plan destructivo.
