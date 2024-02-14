from app.validation import dates, errors, existance, numbers, text


def validate_project(name, budget, start_date, end_date) -> list[str]:
    validation_errors = []

    if not text.name_length(name):
        validation_errors.append(errors.proy_bad_name)

    if not text.budget_type(budget):
        validation_errors.append(errors.bad_budget_type)

    if not dates.end_after_today(end_date):
        validation_errors.append(errors.end_after_today)

    if not dates.start_before_end(start_date, end_date):
        validation_errors.append(errors.start_before)

    elif not numbers.budget_amount(budget):
        validation_errors.append(errors.bad_budget_amount)

    return validation_errors


def validate_user(
    password: str,
    email: str,
    name: str,
    surname: str,
    phonenumber: str,
    username: str,
) -> list[str]:
    validation_errors = []

    if not text.email_address(email):
        validation_errors.append(errors.invalid_email)

    if existance.duplicate_email(email):
        validation_errors.append(errors.email_alreay_registered)

    if not text.password_length(password):
        validation_errors.append(errors.pass_too_short)

    if not text.password_complexity(password):
        validation_errors.append(errors.pass_too_simple)

    if not text.name_length(name) or not text.name_length(surname):
        validation_errors.append(errors.name_too_long_short)

    if not text.phonenumber(phonenumber):
        validation_errors.append(errors.phonetoolong)
    if existance.duplicate_username(username):
        validation_errors.append(errors.non_unique_username)
    if not text.username_length(username):
        validation_errors.append(errors.username_bad_length)

    return validation_errors


def validate_user_update(
    email: str,
    name: str,
    surname: str,
    phonenumber: str,
    username: str,
):
    validation_errors = []

    if not text.email_address(email):
        validation_errors.append(errors.invalid_email)

    if not text.name_length(name) or not text.name_length(surname):
        validation_errors.append(errors.name_too_long_short)

    if not text.phonenumber(phonenumber):
        validation_errors.append(errors.phonetoolong)
    if existance.duplicate_username(username):
        validation_errors.append(errors.non_unique_username)

    if not text.username_length(username):
        validation_errors.append(errors.username_bad_length)

    return validation_errors
