# Backend de la API de Procesamiento de Facturas

Este repositorio contiene el código del backend para una API que procesa facturas en formato PDF, extrayendo información relevante y convirtiéndola a formato JSON. Utiliza Tesseract OCR para la extracción de texto y OpenAI para el análisis y estructuración de los datos.

## Estructura del Proyecto

El backend está organizado de la siguiente manera:

*   `/backend`: Directorio raíz del backend.
*   `/backend/databases/db.py`: Configuración y exportación de la sesión de la base de datos utilizando SQLAlchemy.
*   `/backend/databases/models/{model}.py`: Definición de los modelos de la base de datos. En este caso, se incluyen los modelos `log` e `invoice`.
*   `/backend/modules/{function}.py`: Funciones reutilizables que se utilizan en la API para la lógica de negocio, como la interacción con Tesseract y OpenAI.
*   `/backend/routes/api_v2.py`: Definición de las rutas de la API (endpoints).
*   `/backend/app.py`: Archivo principal que ejecuta la aplicación Flask.
*   `/backend/requirements.txt`: Lista de dependencias del proyecto.
*   `alembic.ini`: Archivo de configuración de Alembic.
*   `alembic`: Directorio que contiene los scripts de migración de la base de datos.

## Prerrequisitos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

*   Python 3.x
*   Tesseract OCR (y los paquetes de idioma necesarios, como `tesseract-ocr-spa` para español). Puedes instalarlo siguiendo las instrucciones para tu sistema operativo: [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)
*   Una cuenta y clave de API de OpenAI.

## Configuración

1.  **Clonar el repositorio:**

    ```bash
    git clone <URL_del_repositorio>
    cd backend
    ```

2.  **Crear un entorno virtual (recomendado):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En Linux/macOS
    venv\Scripts\activate      # En Windows
    ```

3.  **Instalar las dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar las variables de entorno:**

    Crea un archivo `.env` en el directorio `/backend` y añade las siguientes variables:

    ```
    OPENAI_API_KEY=<Tu_clave_de_API_de_OpenAI>
    DATABASE_URL=<URL_de_tu_base_de_datos> #ej: postgresql://user:password@host:port/database_name
    ```
    Reemplaza `<Tu_clave_de_API_de_OpenAI>` con tu clave real y `<URL_de_tu_base_de_datos>` con la URL de tu base de datos.

## Migraciones de la Base de Datos con Alembic

Este proyecto utiliza Alembic para el manejo de migraciones de la base de datos.

### Inicializar Alembic (solo la primera vez):

```bash
alembic init alembic
```

## Crear una nueva migración:

Después de realizar cambios en los modelos de la base de datos, ejecuta el siguiente comando para generar un script de migración:

```bash
alembic revision -m "Descripción de los cambios"
```

Revisa el script generado en alembic/versions y asegúrate de que los cambios sean correctos.

## Aplicar las migraciones:

Para aplicar las migraciones a la base de datos, ejecuta:

```bash
alembic upgrade head
```

Esto aplicará todas las migraciones pendientes.

## Revertir una migración:

Si necesitas revertir a una versión anterior de la base de datos:

```bash
alembic downgrade <ID_de_la_revisión>
```

Puedes obtener el ID de la revisión con alembic history. Para revertir a la versión base:

```bash
alembic downgrade base
```

## ¿Cuándo usar las migraciones?

Debes crear una nueva migración cada vez que realices cambios en la estructura de la base de datos, como:

- Agregar o eliminar tablas.
- Agregar, eliminar o modificar columnas.
- Cambiar tipos de datos.

Es crucial utilizar migraciones para mantener un control de versiones de tu esquema de base de datos y facilitar la colaboración en equipo.

### Ejecución

Para ejecutar el backend:

```bash
python backend/app.py
```

El servidor se iniciará localmente.