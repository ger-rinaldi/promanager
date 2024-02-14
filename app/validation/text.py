import re

from app.validation.requirements import (
    character_complexity,
    name_max_length,
    name_min_length,
    password_required_length,
    username_max_length,
)


def password_complexity(password: str) -> bool:
    def _correct_match_times(
        password: str,
        *patterns: re.Pattern,
        times: int = character_complexity,
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


def password_length(password: str) -> bool:
    required_length: int = password_required_length

    if len(password) < required_length:
        return False
    else:
        return True


def email_address(mail_address: str) -> bool:
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


def phonenumber(phonenumber: str) -> bool:
    return phonenumber.isnumeric() and len(phonenumber) <= 15


def username_length(username: str) -> bool:
    if len(username) > username_max_length or len(username) < name_min_length:
        return False
    return True


def name_length(name: str) -> bool:
    if name_min_length < len(name) < name_max_length:
        return True

    return False


def budget_type(budget: str):
    rgx_numbers: re.Pattern = re.compile(r"[0-9]")

    total_numbers = len(re.findall(rgx_numbers, budget))
    total_dots = len(re.findall(re.compile("\\."), budget))

    if not total_numbers >= len(budget) - 1:
        return False

    if not total_dots <= 1:
        return False

    return True
