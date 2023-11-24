# Lista de que-haceres

Rastrear requisitos a cumplir.
Fecha de inicio: 1/9/23

## Requisitos macro: backlog

1. Boton volver universal (a ultima vista)
1. Boton subir (en el path del sitio)
1. Creación, configuración/modificación,  consulta, baja y validación de datos de **equipos**
1. Creación, configuración/modificación,  consulta, baja y validación de datos **tareas**
1. Asignación de tareas a equipos y miembros de equipo, validación de asignación
1. Alta, configuración/modificación, consultas, baja y validación de datos de miembros de equipo
1. Desarrollar api para separar front de back
1. Pensar e incluir métricas de proyecto mejores y más interesantes, posibles:
     - diagrama Gantt
     - tablero kanban
     - representaciones graficas de un recurso deben redirigir al mismo
     - Lead time (tiempo hasta compleción de tarea) estimado/deseado y concreto
     - WIP (work in progress): cuanto tiempo una tarea ha estado siendo trabajada y cuantas se hayan en ese estado, permitir establecer WIP estimado/deseado
     - Tiempo que una tarea ha estado en cada estado

## Requisitos macro: en proceso

1. Configuración/modificación, consultas, baja y validación de datos de integrantes de proyecto

## Requisitos macro: completados

- Manejo de sesión de usuario (registro, login, logout, cookies)
- Configuración/modificación, baja y validación de datos de **proyectos**
- Validación de solicitudes de informacion por usuario en sesion (Proyecto, Equipo, Tarea)
- Desarrollar y agregar jsonify

### Requisitos micro de macro actual

- verificar que usuario a agregar existe
- verificar que usuario a agregar no ha sido incluido previamente
- modificación de rol de integrante
- eliminación de integrante actual
- suspención de integrante
- agregar información de fechas de acciones sobre integrante
  - cuando fue incluido al proyecto actual
  - cuando se le asigno el rol actual
  - cuando fue suspendido
  - cuando se quito la suspención

### Requisitos micro completados
