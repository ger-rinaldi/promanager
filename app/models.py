from db import get_connection


class usuario:
    tablename = "usuario"
    fields = ("ID_usuario", "nombre", "apellido", "mail", "contraseña")

    def __init__(
        self,
        id: int = None,
        nombre: str = None,
        apellido: str = None,
        mail: str = None,
        contraseña: str = None,
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.mail = mail
        self._contraseña = contraseña

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
            f"SELECT prefijo, pais FROM {prefijos_telefonicos.tablename}"
        )

        return cursor_getall.fetchall()
