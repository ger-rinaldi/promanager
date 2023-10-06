-- los comentarios 'table' permiten a db.crear_schemas separar cada CREATE statement
-- para manejar individualmente cada creacion y sus posibles errores
-- table
CREATE TABLE IF NOT EXISTS prefijo_telefono (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prefijo VARCHAR(8) NOT NULL,
    pais VARCHAR(60) NOT NULL
);
-- table
CREATE TABLE IF NOT EXISTS proyecto(
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL DEFAULT 'not_named',
    descripcion TINYTEXT,
    es_publico BOOLEAN NOT NULL DEFAULT false,
    activo BOOLEAN NOT NULL DEFAULT true,
    presupuesto INT NOT NULL DEFAULT -1,
    fecha_inicio DATE NOT NULL DEFAULT (CURRENT_DATE()),
    fecha_finalizacion DATE NOT NULL DEFAULT '1000-01-01'
);
-- table
CREATE TABLE IF NOT EXISTS usuario(
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL DEFAULT 'no_name',
    apellido VARCHAR(60) NOT NULL DEFAULT 'no_surname',
    email VARCHAR(320) UNIQUE NOT NULL,
    telefono_prefijo INT NOT NULL,
    telefono_numero VARCHAR(30) NOT NULL,
    contrasena VARCHAR(72) NOT NULL,
    llave_sesion VARCHAR(80) NOT NULL DEFAULT 'not_logged',
    FOREIGN KEY (telefono_prefijo) REFERENCES prefijo_telefono(id)

);
-- table
CREATE TABLE IF NOT EXISTS roles_proyecto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) UNIQUE NOT NULL
);
-- table
CREATE TABLE IF NOT EXISTS integrantes_proyecto(
    id INT AUTO_INCREMENT PRIMARY KEY,
    proyecto INT NOT NULL,    /*FORANEA*/
    integrante INT NOT NULL, /*FORANEA*/
    rol INT NOT NULL, /*FORANEA*/
    fecha_inicio_participacion DATE NOT NULL DEFAULT (CURRENT_DATE()),
    fecha_baja DATE NOT NULL DEFAULT '1000-01-01', 
    suspendido BOOLEAN NOT NULL DEFAULT false,
    FOREIGN KEY (proyecto) REFERENCES proyecto(id),
    FOREIGN KEY (integrante) REFERENCES usuario(id),
    FOREIGN KEY (rol) REFERENCES roles_proyecto(id),
    CONSTRAINT integrante_proyecto UNIQUE (proyecto, integrante)
);
-- table
CREATE TABLE IF NOT EXISTS equipo(
    id INT AUTO_INCREMENT PRIMARY KEY,
    proyecto INT NOT NULL,    /*FORANEA*/
    nombre VARCHAR(60) NOT NULL DEFAULT 'not_named',
    fecha_creacion DATE NOT NULL DEFAULT (CURRENT_DATE()),
    FOREIGN KEY (proyecto) REFERENCES proyecto(id)
);
-- table
CREATE TABLE IF NOT EXISTS roles_equipo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) UNIQUE NOT NULL
);
-- table
CREATE TABLE IF NOT EXISTS miembros_equipo(
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipo INT NOT NULL,  /*FORANEA*/
    miembro INT NOT NULL, /*FORANEA*/
    rol INT NOT NULL,
    fecha_inicio_participacion DATE NOT NULL DEFAULT (CURRENT_DATE()),
    fecha_baja DATE NOT NULL DEFAULT '1000-01-01',
    suspendido BOOLEAN NOT NULL DEFAULT false,
    FOREIGN KEY (equipo) REFERENCES equipo(id),
    FOREIGN KEY (miembro) REFERENCES usuario(id),
    FOREIGN KEY (rol) REFERENCES roles_equipo(id),
    CONSTRAINT miembro_equipo UNIQUE (equipo, miembro)
);
-- table
CREATE TABLE IF NOT EXISTS estado(
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(25) UNIQUE NOT NULL
);
-- table
CREATE TABLE IF NOT EXISTS ticket_tarea(
    id INT AUTO_INCREMENT PRIMARY KEY,
    proyecto INT NOT NULL,    /*FORANEA*/
    equipo INT NOT NULL, /*FORANEA*/
    nombre VARCHAR(60) NOT NULL DEFAULT 'not_named',
    estado INT NOT NULL,
    descripcion TINYTEXT,
    fecha_creacion DATE NOT NULL DEFAULT (CURRENT_DATE()),
    fecha_asignacion DATE NOT NULL DEFAULT '1000-01-01',
    fecha_limite DATE NOT NULL DEFAULT '1000-01-01',
    fecha_finalizacion DATE NOT NULL DEFAULT '1000-01-01',
    FOREIGN KEY (proyecto) REFERENCES proyecto(id),
    FOREIGN KEY (equipo) REFERENCES equipo(id),
    FOREIGN KEY (estado) REFERENCES estado(id)
);
-- table
CREATE TABLE IF NOT EXISTS asignacion_tarea(
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_tarea INT NOT NULL, /*FORANEA*/
    miembro INT NOT NULL,  /*FORANEA*/
    fecha_asignacion DATE NOT NULL DEFAULT (CURRENT_DATE()),
    fecha_limite DATE NOT NULL DEFAULT '1000-01-01',
    fecha_finalizacion DATE NOT NULL DEFAULT '1000-01-01',
    FOREIGN KEY (ticket_tarea) REFERENCES ticket_tarea(id),
    FOREIGN KEY (miembro) REFERENCES miembros_equipo(id),
    CONSTRAINT asignacion UNIQUE (ticket_tarea, miembro)
);