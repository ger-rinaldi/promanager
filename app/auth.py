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


    return all(match_result)
