import datetime
from typing import Any, List, Literal, Optional

from sqlalchemy import (
    DATE,
    BigInteger,
    Boolean,
    Column,
    False_,
    ForeignKey,
    Integer,
    String,
    Table,
    True_,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base, engine


def to_date_object(date_string: str):
    print(type(date_string))
    return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()


class PrefijoTelefono(Base):
    # id INT AUTO_INCREMENT PRIMARY KEY,
    id: Mapped[int] = mapped_column(primary_key=True)
    # prefijo VARCHAR(8) NOT NULL,
    prefijo: Mapped[str] = mapped_column(String(8))
    # pais VARCHAR(60) NOT NULL
    pais: Mapped[str] = mapped_column(String(60))


class RolProyecto(Base):
    # id INT AUTO_INCREMENT PRIMARY KEY,
    id: Mapped[int] = mapped_column(primary_key=True)
    # nombre VARCHAR(60) UNIQUE NOT NULL
    nombre: Mapped[str] = mapped_column(String(60))


class RolEquipo(Base):
    # id INT AUTO_INCREMENT PRIMARY KEY,
    id: Mapped[int] = mapped_column(primary_key=True)
    # nombre VARCHAR(60) UNIQUE NOT NULL
    nombre: Mapped[str] = mapped_column(String(60))


class Estado(Base):
    # id INT AUTO_INCREMENT PRIMARY KEY,
    id: Mapped[int] = mapped_column(primary_key=True)
    # nombre VARCHAR(60) UNIQUE NOT NULL
    nombre: Mapped[str] = mapped_column(String(60))


class Proyecto(Base):
    # id INT AUTO_INCREMENT PRIMARY KEY,
    id: Mapped[int] = mapped_column(primary_key=True)
    # nombre VARCHAR(60) NOT NULL DEFAULT 'not_named',
    nombre: Mapped[str] = mapped_column(String(60))
    # descripcion TINYTEXT,
    descripcion: Mapped[str] = mapped_column(TINYTEXT)
    # es_publico BOOLEAN NOT NULL DEFAULT false,
    es_publico: Mapped[bool] = mapped_column(Boolean, server_default=False_())
    # activo BOOLEAN NOT NULL DEFAULT true,
    activo: Mapped[bool] = mapped_column(Boolean, server_default=True_())
    # presupuesto BIGINT NOT NULL DEFAULT -1,
    presupuesto: Mapped[int] = mapped_column(BIGINT(unsigned=True))
    # fecha_inicio DATE NOT NULL DEFAULT (CURRENT_DATE()),
    fecha_creacion: Mapped[datetime.date] = mapped_column(
        DATE, server_default=text("(CURRENT_DATE())")
    )
    fecha_inicio: Mapped[datetime.date] = mapped_column(
        DATE, server_default=text("(CURRENT_DATE())")
    )
    # fecha_finalizacion DATE NOT NULL DEFAULT '1000-01-01'
    fecha_finalizacion: Mapped[datetime.date] = mapped_column(DATE)
    integrantes: Mapped[List["Usuario"]] = relationship(
        secondary="integrante_proyecto", back_populates="proyectos", viewonly=True
    )
    equipos: Mapped[List["Equipo"]] = relationship(
        back_populates="proyecto", viewonly=True
    )
    tickets: Mapped[List["TicketTarea"]] = relationship(
        back_populates="proyecto", viewonly=True
    )

    def __init__(
        self,
        nombre: str,
        descripcion: str,
        presupuesto: int,
        fecha_finalizacion: datetime.date,
        es_publico: bool = False,
        activo: bool = True,
        fecha_inicio: datetime.date = datetime.date.today(),
    ):
        self.nombre: str = nombre
        self.descripcion: str = descripcion
        self.es_publico: bool = es_publico
        self.activo: bool = activo
        self.presupuesto: int = presupuesto
        self.fecha_inicio: datetime.date = fecha_inicio
        self.fecha_finalizacion: datetime.date = fecha_finalizacion


# ? TODO: probablemente establecer getters and setter segun necesite, por ejemplo para fechas, nombre, descripcion
# ? con la finalidad de poder establecer validaciones


class Usuario(Base):
    # id INT AUTO_INCREMENT PRIMARY KEY,
    id: Mapped[int] = mapped_column(primary_key=True)
    # username VARCHAR(20) NOT NULL UNIQUE,
    username: Mapped[str] = mapped_column(String(20), unique=True)
    # nombre VARCHAR(60) NOT NULL DEFAULT 'no_name',
    nombre: Mapped[str] = mapped_column(String(60))
    # apellido VARCHAR(60) NOT NULL DEFAULT 'no_surname',
    apellido: Mapped[str] = mapped_column(String(60))
    # email VARCHAR(320) UNIQUE NOT NULL,
    email: Mapped[str] = mapped_column(String(320), unique=True)
    # telefono_prefijo INT NOT NULL,
    id_telefono_prefijo: Mapped[int] = mapped_column(
        ForeignKey(PrefijoTelefono.__tablename__ + ".id")
    )
    telefono_prefijo: Mapped["PrefijoTelefono"] = relationship()
    # telefono_numero VARCHAR(30) NOT NULL,
    telefono_numero: Mapped[str] = mapped_column(String(30))
    # contrasena VARCHAR(72) NOT NULL,
    contrasena: Mapped[str] = mapped_column(String(72))
    # FOREIGN KEY (telefono_prefijo) REFERENCES prefijo_telefono(id) ON DELETE CASCADE
    proyectos: Mapped[List["Proyecto"]] = relationship(
        secondary="integrante_proyecto", back_populates="integrantes", viewonly=True
    )
    equipos: Mapped[List["Equipo"]] = relationship(
        secondary="miembro_equipo", back_populates="miembros", viewonly=True
    )

    def __init__(
        self,
        username: str,
        nombre: str,
        apellido: str,
        email: str,
        # Se utiliza la ID del registro en vez de un objeto row
        # para evitar instanciarlo, dado que solo se necesitaria
        # al crear o editar un usuario y porque el dato
        # se recibirá directamente del frontend
        id_telefono_prefijo: int,
        telefono_numero: str,
        contrasena: str,
    ):
        self.username: str = username
        self.nombre: str = nombre
        self.apellido: str = apellido
        self.email: str = email
        self.id_telefono_prefijo: int = id_telefono_prefijo
        self.telefono_numero: str = telefono_numero
        self.contrasena: str = contrasena


class IntegranteProyecto(Base):
    # ALERT: ASSOCIATION OBJECT
    # id INT AUTO_INCREMENT PRIMARY KEY,
    id: Mapped[int] = mapped_column(primary_key=True)
    # id_proyecto INT NOT NULL, /*FORANEA*/
    # FOREIGN KEY (proyecto) REFERENCES proyecto(id) ON DELETE CASCADE,
    id_proyecto: Mapped[int] = mapped_column(ForeignKey(Proyecto.__tablename__ + ".id"))
    proyecto: Mapped["Proyecto"] = relationship()  # back_populates="integrantes")
    # id_usuario INT NOT NULL, /*FORANEA*/
    # FOREIGN KEY (id_usuario) REFERENCES usuario(id) ON DELETE CASCADE,
    id_usuario: Mapped[int] = mapped_column(ForeignKey(Usuario.__tablename__ + ".id"))
    usuario: Mapped["Usuario"] = relationship()  # back_populates="proyectos")
    # rol INT NOT NULL, /*FORANEA*/
    # FOREIGN KEY (rol) REFERENCES roles_proyecto(id) ON DELETE CASCADE,
    id_rol: Mapped[int] = mapped_column(ForeignKey(RolProyecto.__tablename__ + ".id"))
    rol: Mapped["RolProyecto"] = relationship()
    # fecha_inicio_participacion DATE NOT NULL DEFAULT (CURRENT_DATE()),
    fecha_inicio_participacion: Mapped[datetime.date] = mapped_column(
        DATE, server_default=text("(CURRENT_DATE())")
    )
    # fecha_baja DATE NOT NULL DEFAULT '1000-01-01',
    fecha_baja: Mapped[Optional[datetime.date]] = mapped_column(DATE)
    # suspendido BOOLEAN NOT NULL DEFAULT false,
    suspendido: Mapped[bool] = mapped_column(Boolean, server_default=False_())

    # CONSTRAINT integrante_proyecto UNIQUE (proyecto, id_usuario)
    __table_args__ = (
        UniqueConstraint("id_proyecto", "id_usuario", name="integrante_proyecto"),
    )

    def __init__(
        self,
        proyecto: "Proyecto",
        usuario: "Usuario",
        rol: "RolProyecto",
        fecha_inicio_participacion: datetime.date = datetime.date.today(),
        suspendido: bool = False,
        fecha_baja: Optional[datetime.date] = None,
    ):
        self.proyecto: "Proyecto" = proyecto
        self.usuario: "Usuario" = usuario
        self.rol: "RolProyecto" = rol
        self.suspendido: bool = suspendido
        self.fecha_baja: Optional[datetime.date] = fecha_baja
        # despues mover esta validacion al setter
        if fecha_inicio_participacion is not None:
            self.fecha_inicio_participacion: datetime.date = fecha_inicio_participacion


# ! ALERT:
# * hacer relacion muchos a muchos directa, como en usuario y proyecto,
# * las id foraneas empiezan con 'id_', los objetos igual que la id foranea sin el 'id_'


class Equipo(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    # id_proyecto INT NOT NULL, /*FORANEA*/
    # FOREIGN KEY (id_proyecto) REFERENCES proyecto(id) ON DELETE CASCADE
    id_proyecto: Mapped[int] = mapped_column(ForeignKey(Proyecto.__tablename__ + ".id"))
    proyecto: Mapped["Proyecto"] = relationship(back_populates="equipos")
    # nombre VARCHAR(60) NOT NULL DEFAULT 'not_named',
    nombre: Mapped[str] = mapped_column(String(60))
    # fecha_creacion DATE NOT NULL DEFAULT (CURRENT_DATE())
    fecha_creacion: Mapped[datetime.date] = mapped_column(
        DATE, server_default=text("(CURRENT_DATE())")
    )
    miembros: Mapped[List["Usuario"]] = relationship(
        secondary="miembro_equipo", back_populates="equipos", viewonly=True
    )
    tickets: Mapped[List["TicketTarea"]] = relationship(
        back_populates="equipo", viewonly=True
    )

    def __init__(
        self,
        nombre: str,
        proyecto: "Proyecto",
    ):
        self.nombre: str = nombre
        self.proyecto: "Proyecto" = proyecto


class MiembroEquipo(Base):
    # -- ALERT: ASSOCIATION OBJECT
    # ALERT:
    # ALERT:
    # ! TODO: Me olvide que miembro equipo no se relaciona directo con usuario sino con integrante_proyecto
    # ALERT:
    # ALERT:
    # PK id, id_miembro
    id: Mapped[int] = mapped_column(primary_key=True)
    # id_equipo INT NOT NULL, /*FORANEA*/
    # FOREIGN KEY (id_equipo) REFERENCES equipo(id) ON DELETE CASCADE,
    id_equipo: Mapped[int] = mapped_column(ForeignKey(Equipo.__tablename__ + ".id"))
    equipo: Mapped["Equipo"] = relationship()
    # id_usuario INT NOT NULL, /*FORANEA*/
    # FOREIGN KEY (id_usuario) REFERENCES integrantes_proyecto(id) ON DELETE CASCADE,
    id_usuario: Mapped[int] = mapped_column(ForeignKey(Usuario.__tablename__ + ".id"))
    usuario: Mapped["Usuario"] = relationship()
    # id_rol INT NOT NULL,
    # FOREIGN KEY (id_rol) REFERENCES roles_equipo(id) ON DELETE CASCADE,
    id_rol: Mapped[int] = mapped_column(ForeignKey(RolEquipo.__tablename__ + ".id"))
    rol: Mapped["RolEquipo"] = relationship()
    # fecha_inicio_participacion DATE NOT NULL DEFAULT (CURRENT_DATE()),
    fecha_inicio_participacion: Mapped[datetime.date] = mapped_column(
        DATE, server_default=text("(CURRENT_DATE())")
    )
    # fecha_baja DATE NOT NULL DEFAULT '1000-01-01',
    fecha_baja: Mapped[Optional[datetime.date]] = mapped_column(DATE)
    # suspendido BOOLEAN NOT NULL DEFAULT false,
    suspendido: Mapped[bool] = mapped_column(Boolean, server_default=False_())
    # CONSTRAINT miembro_equipo UNIQUE (id_equipo, id_usuario)
    __table_args__ = (
        UniqueConstraint("id_equipo", "id_usuario", name="miembro_equipo"),
    )

    def __init__(
        self,
        proyecto: "Proyecto",
        usuario: "Usuario",
        rol: "RolProyecto",
        fecha_inicio_participacion: Optional[datetime.date] = datetime.date.today(),
        suspendido: bool = False,
        fecha_baja: Optional[datetime.date] = None,
    ):
        self.proyecto: "Proyecto" = proyecto
        self.usuario: "Usuario" = usuario
        self.rol: "RolProyecto" = rol
        self.suspendido: bool = suspendido
        self.fecha_baja: Optional[datetime.date] = fecha_baja
        # despues mover esta validacion al setter
        if fecha_inicio_participacion is not None:
            self.fecha_inicio_participacion: datetime.date = fecha_inicio_participacion


class TicketTarea(Base):
    # id INT AUTO_INCREMENT PRIMARY KEY,
    id: Mapped[int] = mapped_column(primary_key=True)
    # id_proyecto INT NOT NULL, /*FORANEA*/
    # FOREIGN KEY (id_proyecto) REFERENCES proyecto(id) ON DELETE CASCADE,
    id_proyecto: Mapped[int] = mapped_column(ForeignKey(Proyecto.__tablename__ + ".id"))
    proyecto: Mapped["Proyecto"] = relationship(back_populates="tickets")
    # id_equipo INT NOT NULL, /*FORANEA*/
    # FOREIGN KEY (id_equipo) REFERENCES equipo(id) ON DELETE CASCADE,
    id_equipo: Mapped[int] = mapped_column(ForeignKey(Equipo.__tablename__ + ".id"))
    equipo: Mapped["Equipo"] = relationship(back_populates="tickets")
    # nombre VARCHAR(60) NOT NULL DEFAULT 'not_named',
    nombre: Mapped[str] = mapped_column(String(60))
    # id_estado INT NOT NULL,
    # FOREIGN KEY (id_estado) REFERENCES estado(id) ON DELETE CASCADE
    id_estado: Mapped[int] = mapped_column(ForeignKey(Estado.__tablename__ + ".id"))
    estado: Mapped["Estado"] = relationship()
    # descripcion TINYTEXT,
    descripcion: Mapped[str] = mapped_column(TINYTEXT)
    # fecha_creacion DATE NOT NULL DEFAULT (CURRENT_DATE()),
    fecha_creacion: Mapped[datetime.date] = mapped_column(
        DATE, server_default=text("(CURRENT_DATE())")
    )
    # fecha_limite DATE NOT NULL DEFAULT '1000-01-01',
    fecha_limite: Mapped[Optional[datetime.date]] = mapped_column(DATE)
    # fecha_finalizacion DATE NOT NULL DEFAULT '1000-01-01',
    fecha_finalizacion: Mapped[Optional[datetime.date]] = mapped_column(DATE)

    def __init__(
        self,
        id_proyecto: int,
        proyecto: "Proyecto",
        id_equipo: int,
        equipo: "Equipo",
        nombre: str,
        # se utiliza la id en vez del objeto al igual que prefijo_telefono de Usuario
        id_estado: int,
        descripcion: str,
        fecha_creacion: datetime.date,
        fecha_asignacion: Optional[datetime.date] = None,
        fecha_limite: Optional[datetime.date] = None,
        fecha_finalizacion: Optional[datetime.date] = None,
        asignado: bool = False,
    ) -> None:
        self.id_proyecto: int = id_proyecto
        self.proyecto: "Proyecto" = proyecto
        self.id_equipo: int = id_equipo
        self.equipo: "Equipo" = equipo
        self.nombre: str = nombre
        self.id_estado: int = id_estado
        self.descripcion: str = descripcion
        self.fecha_creacion: datetime.date = fecha_creacion
        self.asignado: bool = asignado

        if fecha_asignacion is not None:
            self.fecha_asignacion: datetime.date = fecha_asignacion
        if fecha_limite is not None:
            self.fecha_limite: datetime.date = fecha_limite
        if fecha_finalizacion is not None:
            self.fecha_finalizacion: datetime.date = fecha_finalizacion


class AsignacionTarea(Base):
    # -- ALERT: ASSOCIATION OBJECT
    # id INT AUTO_INCREMENT PRIMARY KEY,
    id: Mapped[int] = mapped_column(primary_key=True)
    # id_ticket_tarea INT NOT NULL, /*FORANEA*/
    # FOREIGN KEY (id_ticket_tarea) REFERENCES ticket_tarea(id) ON DELETE CASCADE,
    id_ticket: Mapped[int] = mapped_column(
        ForeignKey(TicketTarea.__tablename__ + ".id")
    )
    ticket: Mapped["TicketTarea"] = relationship()
    # id_miembro INT NOT NULL, /*FORANEA*/
    # FOREIGN KEY (id_miembro) REFERENCES miembros_equipo(id) ON DELETE CASCADE,
    id_miembro: Mapped[int] = mapped_column(
        ForeignKey(
            MiembroEquipo.__tablename__ + ".id"
        )  # TODO: el campo aca no es .id si no .id_miembro
    )
    miembro: Mapped["MiembroEquipo"] = relationship()
    # fecha_asignacion DATE NOT NULL DEFAULT (CURRENT_DATE()),
    fecha_asignacion: Mapped[datetime.date] = mapped_column(
        DATE, server_default=text("(CURRENT_DATE())")
    )

    def __init__(
        self,
        ticket: "TicketTarea",
        miembro: "MiembroEquipo",
        fecha_asignacion: Optional[datetime.date] = None,
    ) -> None:
        self.ticket: "TicketTarea" = ticket
        self.miembro: "MiembroEquipo" = miembro

        if fecha_asignacion is not None:
            self.fecha_asignacion: datetime.date = fecha_asignacion
        if self.ticket.fecha_limite is not None:
            self.fecha_limite: datetime.date = self.ticket.fecha_limite
        if self.ticket.fecha_finalizacion is not None:
            self.fecha_finalizacion: datetime.date = self.ticket.fecha_finalizacion


if __name__ == "__main__":
    Base.metadata.create_all(engine)
