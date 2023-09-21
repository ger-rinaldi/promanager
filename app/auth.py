import re
from typing import Union


class validate_user:
    password_required_length: int = 12
    character_complexity: int = 3
    name_max_length: int = 60
    name_min_length: int = 2
    phone_max_length: int = 15

    @classmethod
    def validate_all(
        cls, password: str, email: str, name: str, surname: str, phonenumber: str
    ) -> list[str]:
        errors = []

        if not cls.email_address_validator(email):
            errors.append(Errors.invalid_email)

        if not cls.check_email_not_registered(email):
            errors.append(Errors.email_alreay_registered)

        if not cls.password_length_validator(password):
            errors.append(Errors.pass_too_short)

        if not cls.password_complexity_validator(password):
            errors.append(Errors.pass_too_simple)

        if not cls.valid_name_length(name) or not cls.valid_name_length(surname):
            errors.append(Errors.username_too_long_short)

        if not cls.valid_phonenumber(phonenumber):
            errors.append(Errors.phonetoolong)

        return errors

    @classmethod
    def password_complexity_validator(cls, password: str) -> bool:
        def _correct_match_times(
            password: str,
            *patterns: re.Pattern,
            times: int = cls.character_complexity,
        ) -> list[bool]:
            match_amount_per_pattern: list[bool] = []

            for pattern in patterns:
                found_matches: list[str] = re.findall(pattern, password)
                total_matches: int = len(found_matches)

                if total_matches >= times:
                    match_amount_per_pattern.append(True)
                else:
                    match_amount_per_pattern.append(False)

            return match_amount_per_pattern

        minuscula: re.Pattern = re.compile(r"[a-z]")
        mayuscula: re.Pattern = re.compile(r"[A-Z]")
        numeros: re.Pattern = re.compile(r"[0-9]")
        especiales: re.Pattern = re.compile(r"[!-\.:-@\[-_]")

        match_result = _correct_match_times(
            password, minuscula, mayuscula, numeros, especiales
        )

        return all(match_result)

    @classmethod
    def password_length_validator(cls, password: str) -> bool:
        required_length: int = cls.password_required_length

        if len(password) < required_length:
            return False
        else:
            return True

    @classmethod
    def email_address_validator(cls, mail_address: str) -> bool:
        regex: re.Pattern = re.compile(
            r"""
            ^                       # el string debe comenzar con
            [a-zA-Z_0-9\\"“”]+      # 1:N caracteres que se hallen dentro de este rango
            (                       # luego de eso, el mail PUEDE contener el siguiente grupo:
                (\.|-|\+)               # un simbolo de 'punto', 'guion' o 'más'  previo a
                [a-zA-Z_0-9\\"“”\s]+    # 1:N caracteres de esta lista
            )*                      # el grupo previamente descripto puede estar entre 0 y N veces
            @                       # el mail debe contener una arroba
            (                       # el mail DEBE contener el siguiente grupo:
                \w+                 # 1:N caracteres palabra, seguidos de
                ((\.|\-)\w+)+       # 1:N grupos empezando por '.' o '-' terminen con 1:N caracteres
                |                                # O
                (\[(\d{3}\.){3}\d{1,3}\]){1}     # una IP como [123.123.123.123]
            )                       # el grupo despues de la arroba es obligatorio
            $                       # y debe encontrarse al final del string
            """,
            re.VERBOSE,
        )
        is_valid_mail: re.Match[str] | None = regex.fullmatch(mail_address)

        if is_valid_mail is None:
            return False
        else:
            return True

    @classmethod
    def check_email_not_registered(cls, email: str) -> bool:
        from db import get_connection

        cnx = get_connection()
        cursor = cnx.cursor()

        sql = "SELECT 1 FROM usuario WHERE email = %s;"

        cursor.execute(sql, (email,))

        email_exists = cursor.fetchone()

        cnx.close()
        cursor.close()

        if not email_exists:
            return True
        else:
            return False

    @classmethod
    def valid_name_length(cls, name: str) -> bool:
        if cls.name_max_length < len(name) or len(name) < cls.name_min_length:
            return False
        return True

    @classmethod
    def valid_phonenumber(cls, phonenumber: str) -> bool:
        return phonenumber.isnumeric() and len(phonenumber) <= 15


class Errors:
    pass_too_short: str = f"La contraseña debe tener un mínimo de\
                        {validate_user.password_required_length} caractéres"

    pass_too_simple: str = f"La contraseña debe contener {validate_user.character_complexity}\
    de los siguientes tipos de caracteres \
    minúscula, mayúscula, numéricos y especiales."

    invalid_email: str = "La dirección de email ingresada no es válida"

    email_alreay_registered: str = (
        "La dirección de email ingresada ya está sido registrada."
    )

    username_too_long_short: str = f"Tanto nombre como apellido deben tener entre\
        {validate_user.name_min_length} y {validate_user.name_max_length} caracteres."

    phonetoolong: str = f"El número de teléfono no puede ser mayor a\
        {validate_user.phone_max_length} caracteres"
