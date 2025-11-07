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

Clona este repositorio en tu máquina Klipper (por ejemplo, en `/home/pi/klipper_config/`):

```bash
git clone https://github.com/joseto1298/Klipper-Spoolman-Sync.git
cd Klipper-Spoolman-Sync
```

### 2. Configuración (`config.ini`)

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

### 3. Macros de Klipper (`klipper_macros.cfg`)

Copia el contenido del archivo `klipper_macros.cfg` y añádelo a tu archivo de configuración de Klipper (por ejemplo, `printer.cfg`).

Este archivo contiene las siguientes macros:

| Macro | Descripción |
| :--- | :--- |
| `FILAMENT_INFO` | Macro que recibe la información del filamento (ID, Nombre, Material) desde `filamentNotice.py`. **Aquí es donde puedes añadir lógica personalizada**, como enviar notificaciones a Telegram o Discord, o actualizar una pantalla. |
| `CHECK_FILAMENT_LIST` | Macro que ejecuta `filamentList.py` para analizar el G-code y obtener la secuencia de filamentos. |
| `FILAMENT_CHANGE_NOTICE` | Macro que ejecuta `filamentNotice.py` para consultar Spoolman y notificar a Klipper. |

### 4. Integración con el Slicer

Para que el sistema funcione, debes añadir un comando de cambio de filamento en tu *slicer* (por ejemplo, PrusaSlicer o Cura) que incluya el ID del filamento de Spoolman.

El comando debe tener el formato:

```gcode
ASSERT_ACTIVE_FILAMENT ID=<ID_DE_SPOOLMAN>
```

**Ejemplo:** Si el filamento que vas a usar tiene el ID `123` en Spoolman, el comando en el G-code debe ser:

```gcode
ASSERT_ACTIVE_FILAMENT ID=123
```

## Uso

### 1. Analizar la Secuencia de Filamentos

Antes de imprimir, puedes usar la macro `CHECK_FILAMENT_LIST` para ver la secuencia de filamentos que se utilizarán en el trabajo de impresión:

```gcode
CHECK_FILAMENT_LIST FILENAME=<nombre_del_archivo.gcode>
```

El script `filamentList.py` analizará el G-code y mostrará en la consola de Klipper la lista de filamentos requeridos, consultando sus nombres y materiales en Spoolman.

### 2. Notificar un Cambio de Filamento

Cuando Klipper necesite cambiar de filamento (por ejemplo, al inicio de la impresión o en un `M600`), debes llamar a la macro `FILAMENT_CHANGE_NOTICE` con el ID del filamento:

```gcode
FILAMENT_CHANGE_NOTICE ID=<ID_DE_SPOOLMAN>
```

Esta macro ejecutará `filamentNotice.py`, que:
1.  Consulta Spoolman para obtener el nombre y material del filamento.
2.  Llama a la macro `FILAMENT_INFO` en Klipper con los datos obtenidos.

**Nota:** La macro `FILAMENT_INFO` es el punto de entrada para tus acciones personalizadas.

## Estructura del Proyecto

| Archivo | Descripción |
| :--- | :--- |
| `config.ini` | Archivo de configuración para las URLs de Spoolman, Klipper y Moonraker. |
| `requirements.txt` | Dependencias de Python (`requests`, `configparser`). |
| `filamentList.py` | Script para analizar un archivo G-code y listar la secuencia de filamentos requeridos. |
| `filamentNotice.py` | Script para consultar Spoolman y enviar la información del filamento a Klipper a través de Moonraker. |
| `klipper_macros.cfg` | Macros de Klipper (`FILAMENT_INFO`, `CHECK_FILAMENT_LIST`, `FILAMENT_CHANGE_NOTICE`) para la integración. |

## Contribución

Siéntete libre de abrir *issues* o enviar *pull requests* para mejorar la funcionalidad o la documentación.

## Licencia

MIT License
