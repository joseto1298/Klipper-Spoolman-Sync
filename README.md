# Klipper-Spoolman-Sync

Integración y sincronización de información de filamentos entre **Klipper** y **Spoolman**.

Este proyecto proporciona un conjunto de scripts y macros para:
1.  **Analizar** el G-code en Klipper para detectar cambios de filamento definidos por el usuario.
2.  **Consultar** la API de Spoolman para obtener los detalles del filamento (nombre y material).
3.  **Enviar** notificaciones de cambio de filamento a Klipper a través de Moonraker, permitiendo la integración con macros personalizadas.

## Requisitos

Para utilizar este proyecto, necesitarás:

*   Un entorno de impresión 3D basado en **Klipper** y **Moonraker**.
*   Una instancia de **Spoolman** en funcionamiento.
*   **Python 3** con las siguientes librerías:
    *   `requests`
    *   `configparser`

Puedes instalar las dependencias de Python con el siguiente comando:

```bash
pip install -r requirements.txt
```

## Instalación y Configuración

### 1. Clonar el Repositorio

Clona este repositorio en tu máquina Klipper (por ejemplo, en `/home/pi/`):

```bash
git clone https://github.com/joseto1298/Klipper-Spoolman-Sync.git
cd Klipper-Spoolman-Sync
```

### 2. Crea y activa el entorno virtual e instala dependencias:
```ini
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuración (`config.ini`)

Edita el archivo `config.ini` para que coincida con tu configuración local:

```ini
[Spoolman]
SPOOLMAN_URL = http://<IP_SPOOLMAN>:<PUERTO>/api/v1/filament/

[Klipper]
GCODE_PATH = /home/pi/printer_data/gcodes/

[Moonraker]
MOONRAKER_BASE_URL = http://<IP_MOONRAKER>:<PUERTO>/
```

| Sección | Clave | Descripción |
| :--- | :--- | :--- |
| `[Spoolman]` | `SPOOLMAN_URL` | URL base de la API de Spoolman para filamentos. **Asegúrate de que termina en `/filament/`**. |
| `[Klipper]` | `GCODE_PATH` | Ruta absoluta donde Klipper guarda los archivos G-code. |
| `[Moonraker]` | `MOONRAKER_BASE_URL` | URL base de la API de Moonraker. **Asegúrate de que termina en `/`**. |

### 4. Macros de Klipper (`klipper_macros.cfg`)

Copia el contenido del archivo `klipper_macros.cfg` y añádelo a tu archivo de configuración de Klipper (por ejemplo, `printer.cfg`).

Este archivo contiene las siguientes macros:

| Macro | Descripción |
| :--- | :--- |
| `FILAMENT_INFO` | Macro que recibe la información del filamento (ID, Nombre, Material) desde `filamentNotice.py`. **Aquí es donde puedes añadir lógica personalizada**, como enviar notificaciones a Telegram o Discord, o actualizar una pantalla. |
| `CHECK_FILAMENT_LIST` | Macro que ejecuta `filamentList.py` para analizar el G-code y obtener la secuencia de filamentos. |
| `FILAMENT_CHANGE_NOTICE` | Macro que ejecuta `filamentNotice.py` para consultar Spoolman y notificar a Klipper. |

### 5. Integración con el Slicer

Para que el sistema funcione, debes añadir un comando de cambio de filamento en tu *slicer* (por ejemplo, PrusaSlicer o Cura) que incluya el ID del filamento de Spoolman.

El comando debe tener el formato:

```gcode
ASSERT_ACTIVE_FILAMENT ID=<ID_DE_SPOOLMAN>
```

**Ejemplo:** Si el filamento que vas a usar tiene el ID `123` en Spoolman, el comando en el G-code debe ser:

```gcode
ASSERT_ACTIVE_FILAMENT ID=123
```
### 6. Integración con moonraker

Añadir en el fichero moonraker.conf

```ini
[update_manager Klipper-Spoolman-Sync]
type: git_repo
primary_branch: main
path: /home/pi/Klipper-Spoolman-Sync
origin: https://github.com/joseto1298/Klipper-Spoolman-Sync.git
virtualenv: /home/pi/Klipper-Spoolman-Sync/venv
requirements: /home/pi/Klipper-Spoolman-Sync/requirements.txt
managed_services: klipper
```

## Uso

### 1. Mostrar la Secuencia de Filamentos

Añádir la macro `_FILAMENT_LIST`en g-code de incio para ver la secuencia de filamentos que se utilizarán en el trabajo de impresión:

```gcode
_FILAMENT_LIST 
```

El script `filamentList.py` analizará el G-code y mostrará en la consola de Klipper la lista de filamentos requeridos, consultando sus nombres y materiales en Spoolman.


### 2. Notificar un Cambio de Filamento

Cuando Klipper necesite cambiar de filamento (por ejemplo, al inicio de la impresión o en un `M600`), debes llamar a la shell_command `FILAMENT_NOTICE` con el ID del filamento:

```gcode
RUN_SHELL_COMMAND CMD=FILAMENT_NOTICE PARAMS="{id}"
```

Esta macro ejecutará `filamentNotice.py`, que:
1.  Consulta Spoolman para obtener el nombre y material del filamento.
2.  Llama a la macro `_FILAMENT_INFO` en Klipper con los datos obtenidos.

**Nota:** Se pueden usar ambos sistemas o uno solo depedendiendo de las necesidades.

## Estructura del Proyecto

| Archivo | Descripción |
| :--- | :--- |
| `config.ini` | Archivo de configuración para las URLs de Spoolman, Klipper y Moonraker. |
| `requirements.txt` | Dependencias de Python (`requests`, `configparser`). |
| `filamentList.py` | Script para analizar un archivo G-code y listar la secuencia de filamentos requeridos. |
| `filamentNotice.py` | Script para consultar Spoolman y enviar la información del filamento a Klipper a través de Moonraker. |
| `klipper_macros-shell_command.cfg` | Macros de Klipper (`_FILAMENT_LIST`, `_FILAMENT_INFO`) y shell_command (`FILAMENT_LIST`, `FILAMENT_NOTICE` ) para la integración. |

## Contribución

Siéntete libre de abrir *issues* o enviar *pull requests* para mejorar la funcionalidad o la documentación.

## Licencia

MIT License
