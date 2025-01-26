# Blog Application

Este proyecto es una aplicación de blog desarrollada con **FastAPI** y **MongoDB**. Permite a los usuarios registrarse, iniciar sesión, crear publicaciones, y gestionar su perfil personal.

---

## Características

- **Registro e inicio de sesión**:
  - Los usuarios pueden registrarse proporcionando su nombre, correo electrónico, contraseña y una imagen de perfil.
  - Autenticación con cookies y tokens JWT.

- **Gestión de publicaciones**:
  - Crear, actualizar y eliminar publicaciones.
  - Listar publicaciones en la página principal.

- **Gestión de perfiles**:
  - Ver las publicaciones asociadas a un usuario en su perfil.

- **Diseño Frontend**:
  - Integración con plantillas HTML utilizando **Jinja2**.
  - Archivos estáticos (CSS/JavaScript/Imágenes) servidos desde el directorio `/static`.

---

## Tecnologías utilizadas

- **Backend**:
  - [FastAPI](https://fastapi.tiangolo.com/): Framework para desarrollar APIs rápidas y robustas.
  - [MongoDB](https://www.mongodb.com/): Base de datos NoSQL.
  - [PyMongo](https://pymongo.readthedocs.io/): Cliente de MongoDB para Python.

- **Autenticación**:
  - [passlib](https://passlib.readthedocs.io/): Hashing seguro para contraseñas.
  - [python-jose](https://python-jose.readthedocs.io/): Generación y verificación de tokens JWT.

- **Frontend**:
  - [Jinja2](https://jinja.palletsprojects.com/): Motor de plantillas HTML.

- **Entorno**:
  - [dotenv](https://pypi.org/project/python-dotenv/): Gestión de variables de entorno.

---

## Requisitos previos

Asegúrate de tener instalados los siguientes programas:

- [Python 3.9+](https://www.python.org/downloads/)
- [MongoDB](https://www.mongodb.com/try/download/community)

---

## Instalación y configuración

1. Clona este repositorio:

   ```bash
   git@github.com:Jyepes18/blog.git
   ```
2. Instalar dependencias
    ```
    pip install -r requirements.txt
    ```
3. Crear entono virtual
    - Windows

        ```
        python -m venv venv
        venv\Scripts\activate
        ```
    - Mac/Linux

        ```
        python3 -m venv venv
        source venv/bin/activate
        ```
4. Crear un archivo **.env** para variables de entorno y colocar estas varibles 
    ```
    SECRET_KEY=tu_clave_secreta
    TOKEN_SECONDS_EXPIRATE=3600
    ```
5. Iniciar servidor de mongoDB
6. Correr aplicacion
    ```
    fastapi dev main.py
    ```