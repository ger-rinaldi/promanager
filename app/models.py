from bcrypt import gensalt, hashpw
from db import get_connection


class usuario:
    tablename = "usuario"
    fields = (
        "ID_usuario",
        "nombre",
        "apellido",
        "mail",
        "prefijo_tel",
        "telefono_num",
        "contraseña",
    )
    all_fields: str = ", ".join(fields)
    no_id_fields: str = ", ".join(fields[1:])

    @classmethod
    def create(
        cls,
        nombre: str = None,
        apellido: str = None,
        mail: str = None,
        prefijo_tel: int = None,
        telefono: str = None,
        contraseña: str = None,
    ):
        "Crear nuevo registro de usuario en la base de datos"

        cnx = get_connection()
        cursor_create = cnx.cursor()

        sql = f"INSERT INTO {cls.tablename}({cls.no_id_fields})\
                VALUES  (%s, %s, %s, %s, %s, %s)"

        values = (
            nombre,
            apellido,
            mail,
            prefijo_tel,
            telefono,
            hashpw(password=contraseña.encode("utf8"), salt=gensalt()),
        )

        cursor_create.execute(sql, values)

        cnx.commit()
        cursor_create.close()
        cnx.close()

    def __init__(
        self,
        id: int = None,
        nombre: str = None,
        apellido: str = None,
        mail: str = None,
        telef_prefix: str = None,
        telef_num: str = None,
        contraseña: str = None,
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.mail = mail
        self._contraseña = contraseña
        self.prefijo_telefono = telef_prefix
        self.numero_telefono = telef_num

    def __tuple__(self) -> tuple:
        """Retornar atributos de usuario como tupla


        Returns:
            tuple: (id, nombre, apellido, mail)
        """
        return (self.id, self.nombre, self.apellido, self.mail)


class prefijos_telefonicos:
    """Clase encargada de obtener los prefijos telefonicos"""

    tablename = "prefijo_telefono"

    @classmethod
    def read_all(cls):
        """Obtener todos los paises y sus codigos sin ID"""

        cnx = get_connection()
        cursor_getall = cnx.cursor(dictionary=True)
        cursor_getall.execute(
            f"SELECT ID_prefijo, prefijo, pais FROM {prefijos_telefonicos.tablename}"
        )

        return cursor_getall.fetchall()
