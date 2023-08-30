import re


def password_complexity_validator(password: str = None) -> bool:
    def _correct_match_times(
        password: str, *patterns: re, times: int = 3
    ) -> list[bool]:
        match_amount_per_pattern = []

        for pattern in patterns:
            found_matches = re.findall(pattern, password)
            total_matches = len(found_matches)

            if total_matches >= times:
                match_amount_per_pattern.append(True)
            else:
                match_amount_per_pattern.append(False)

        return match_amount_per_pattern

    minuscula = re.compile(r"[a-z]")
    mayuscula = re.compile(r"[A-Z]")
    numeros = re.compile(r"[0-9]")
    especiales = re.compile(r"[!-\.:-@\[-_]")

    match_result = _correct_match_times(
        password, minuscula, mayuscula, numeros, especiales
    )

    return all(match_result)


def password_length_validator(password: str = None) -> bool:
    if password is None:
        return

    required_length: int = 12

    if len(password) < required_length:
        return False
    else:
        return True


def email_address_validator(mail_address: str = None) -> bool:
    if mail_address is None:
        return

    regex = re.compile(
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
            ((\.|\-)\w+)+       # 1:N grupos que empiecen por '.' o '-' terminen con 1:N caracteres
            |                                # O
            (\[(\d{3}\.){3}\d{1,3}\]){1}     # una IP como [123.123.123.123]
        )                       # el grupo despues de la arroba es obligatorio
        $                       # y debe encontrarse al final del string
        """,
        re.VERBOSE,
    )
    is_valid_mail = regex.fullmatch(mail_address)

    if is_valid_mail is None:
        return False
    else:
        return True
