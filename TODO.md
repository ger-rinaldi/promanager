# Lista de que-haceres

Rastrear requisitos a cumplir.
Fecha de inicio: 1/9/23

## Requisitos macro: backlog

1. Validación de solicitudes de informacion por usuario en sesion (Proyecto, Equipo, Tarea)
1. Creación, configuración/modificación,  consulta, baja y validación de datos de **equipos**
1. Creación, configuración/modificación,  consulta, baja y validación de datos **tareas**
1. Asignación de tareas a equipos y miembros de equipo, validación de asignación
1. Configuración/modificación, consultas, baja y validación de datos de integrantes de proyecto
1. Alta, configuración/modificación, consultas, baja y validación de datos de miembros de equipo
1. Desarrollar api para separar front de back
1. Desarrollar y agregar jsonify

## Requisitos macro: en proceso

1. Configuración/modificación, baja y validación de datos de **proyectos**

## Requisitos macro: completados

- Manejo de sesión de usuario (registro, login, logout, cookies)

### Requisitos micro de macro actual

- Vista de información de proyecto (sin permitir modificar)
  - boton modificar dentro de esta vista
  - boton ver equipos de proyecto
    - tabla de equipos de proyecto
      - acciones de equipo: ver detalles, ver integrantes, ver tareas
  - boton ver tareas de proyecto
  - boton ver integrantes dentro de esta vista
- Acciones en lista: ver detalles (ojito), ver integrantes (icono con personitas)
- Baja y confirmación de baja de proyecto
  - borrado de registros relacionados

### Requisitos micro completados

- creación de proyecto
- validación de datos de creacion
- mostrar errores de creación de proyectos
- Modificacion de proyecto ya creado
- Validacion de valores modificados
- Mostrar errores
- Vista de modificación
