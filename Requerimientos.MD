# WatchPub - Red Social en Consola

WatchPub es una aplicación de red social en consola desarrollada en Python, que permite a los usuarios registrarse, iniciar sesión, publicar mensajes, dar likes, comentar publicaciones y visitar perfiles de otros usuarios. Utiliza una interfaz basada en texto con la librería `textual` y Firebase Realtime Database para almacenar datos.

## Requerimientos

A continuación, se detallan los requerimientos necesarios para ejecutar el archivo `main.py` y poner en marcha la aplicación.

### 1. Entorno de Ejecución
- **Sistema Operativo**: Compatible con Windows, macOS o Linux.
- **Python**: Versión 3.8 o superior. Puedes descargar Python desde [python.org](https://www.python.org/downloads/).

### 2. Librerías de Python
El proyecto depende de las siguientes librerías de Python. Asegúrate de instalarlas antes de ejecutar el programa.

#### Librerías Requeridas
- **`textual`**: Para la interfaz de usuario en consola.
  - Versión recomendada: `>=0.47.1`
- **`firebase_admin`**: Para interactuar con Firebase Realtime Database.
  - Versión recomendada: `>=6.5.0`

#### Instalación de Librerías
1. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate