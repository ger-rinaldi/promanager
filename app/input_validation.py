import datetime
import re
from typing import Union


class validate_user:
    password_required_length: int = 12
    character_complexity: int = 3
    name_max_length: int = 60
    name_min_length: int = 2
    phone_max_length: int = 15
    username_max_length: int = 20

    @classmethod
    def validate_all(
        cls,
        password: str,
        email: str,
        name: str,
        surname: str,
        phonenumber: str,
        username: str,
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
        if not cls.username_not_registered(username):
            errors.append(Errors.non_unique_username)
        if not cls.username_length(username):
            errors.append(Errors.username_bad_length)

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

    @classmethod
    def username_not_registered(cls, username: str) -> bool:
        from db import get_connection

        cnx = get_connection()
        cursor = cnx.cursor()

        sql = "SELECT 1 FROM usuario WHERE username = %s;"

        cursor.execute(sql, (username,))

        username_exists = cursor.fetchone()

        cnx.close()
        cursor.close()

        if not username_exists:
            return True
        else:
            return False

    @classmethod
    def username_length(cls, username: str) -> bool:
        if (
            len(username) > cls.username_max_length
            or len(username) < cls.name_min_length
        ):
            return False
        return True


class validate_proyect:
    name_max_len = 60
    name_min_len = 2

    @classmethod
    def validate_all(cls, name, budget, start_date, end_date) -> list[str]:
        errors = []

        if not cls.valid_name_lenght(name):
            errors.append(Errors.proy_bad_name)

        if not cls.valid_budget_value(budget):
            errors.append(Errors.bad_budget)

        if not cls.end_after_today(end_date):
            errors.append(Errors.end_after_today)

        if not cls.start_before(start_date, end_date):
            errors.append(Errors.start_before)

        return errors

    @classmethod
    def valid_name_lenght(cls, name: str) -> bool:
        if cls.name_min_len < len(name) < cls.name_max_len:
            return True

        return False

    @classmethod
    def valid_budget_value(cls, budget: str):
        rgx_numbers: re.Pattern = re.compile(r"[0-9]")

        total_numbers = len(re.findall(rgx_numbers, budget))
        total_dots = len(re.findall(re.compile("\."), budget))

        if not total_numbers >= len(budget) - 1:
            return False

        if not total_dots <= 1:
            return False

        return True

    @classmethod
    def start_before(cls, start_date: str, end_date: str) -> bool:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

        if start_date >= end_date:
            return False

        return True

    @classmethod
    def end_after_today(cls, end_date: str) -> bool:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        today = datetime.date.today()

        if end_date <= today:
            return False

        return True


class Errors:
    non_unique_username: str = "El nombre de usuario ingresado ya está registrado"

    username_bad_length: str = f"El nombre de usuario no puede exceder los {validate_user.username_max_length} y debe superar los {validate_user.name_min_length}"

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

    proy_bad_name: str = f"Nombre de proyecto inválido. Debe contener entre \
    {validate_proyect.name_min_len} y {validate_proyect.name_max_len} caracteres."

    bad_budget: str = "Valor de presupuesto inválido. Solo puede contener numeros y un punto para decimales"

    start_before: str = f"Fechas ingresadas inválidas. La fecha de inicio debe ser anterior a la de finalización."

    end_after_today: str = f"Fecha de finalización inválida. El proyecto debe terminar después de la fecha corriente."
