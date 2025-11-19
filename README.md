# Refugio Andino -- Sistema de Gestión Hotelera

## Descripción general

Refugio Andino es un sistema web para la gestión integral de un hotel.
Permite administrar reservas, disponibilidad de habitaciones, clientes y
usuarios mediante una interfaz simple y eficiente. El sistema está
construido con Flask y utiliza SQLite como motor de base de datos.
Incluye control de acceso basado en roles y garantiza la integridad de
los datos a través de validaciones y restricciones lógicas.

## Características principales

### Autenticación y roles

-   Inicio y cierre de sesión.
-   Registro de usuarios con rol de cliente.
-   Usuario administrador preconfigurado.
-   Roles disponibles:
    -   **Administrador**: acceso completo al sistema.
    -   **Usuario**: acceso limitado a la gestión de sus propias
        reservas.

### Gestión de reservas

-   Crear reservas con validación de disponibilidad y choques de fechas.
-   Confirmar, cancelar y reprogramar reservas.
-   Eliminar reservas únicamente cuando se encuentran en estado
    "Cancelada".
-   El administrador puede gestionar todas las reservas; los usuarios
    solo las suyas.

### Gestión de disponibilidad

-   Consulta de habitaciones disponibles en un rango de fechas.
-   Exclusión automática de habitaciones con reservas activas o en
    mantenimiento.

### Gestión de clientes

-   Creación, listado y búsqueda de clientes.
-   Eliminación restringida a clientes sin reservas activas.
-   Asociación automática entre usuario registrado y cliente
    correspondiente.

### Habitaciones y tipos

-   Habitaciones clasificadas por tipo, precio y estado.
-   Habitaciones en mantenimiento excluidas de reservas y consultas de
    disponibilidad.

## Tecnologías utilizadas

-   Python 3
-   Flask
-   SQLite3
-   HTML, CSS, Jinja2
-   JavaScript (mínimo)

## Estructura del proyecto

    Proyecto/
    │── app.py
    │── reserva_hotel.db
    │── /templates
    │     ├── base.html
    │     ├── login.html
    │     ├── register.html
    │     ├── home.html
    │     ├── clientes.html
    │     ├── reservas.html
    │     └── disponibilidad.html
    │── /static
    │     ├── style.css
    │     └── img/

## Instalación y ejecución

### 1. Crear entorno virtual (opcional)

    python -m venv venv

### 2. Activar el entorno

    venv\Scripts\activate       (Windows)
    source venv/bin/activate      (Linux/Mac)

### 3. Instalar dependencias

    pip install flask

### 4. Ejecutar el servidor

    python app.py

### 5. Acceder al sistema

    http://127.0.0.1:5000

## Credenciales por defecto

  Rol             Usuario   Contraseña
  --------------- --------- ------------
  Administrador   admin     admin123

## Reglas de negocio relevantes

-   Las reservas solo pueden eliminarse si están en estado "Cancelada".
-   Los usuarios solo pueden ver, crear y gestionar reservas asociadas a
    su propio cliente.
-   Los pagos asociados a una reserva deben eliminarse antes de borrar
    la reserva para cumplir las restricciones de clave foránea.
-   La creación de clientes por parte de usuarios se realiza
    automáticamente al momento del registro.

## Estado del proyecto

El sistema se encuentra completamente funcional y permite gestionar de
manera eficiente las operaciones básicas de un hotel. Está diseñado para
ser mantenible, extensible y fácilmente desplegable en entornos pequeños
o académicos.
