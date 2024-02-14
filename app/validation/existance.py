from app.db import get_connection


def username_exists(username: str) -> bool:
    cnx = get_connection()
    cursor = cnx.cursor()

    sql = "SELECT 1 FROM usuario WHERE username = %s;"

    cursor.execute(sql, (username,))

    username_exists = cursor.fetchone()

    cnx.close()
    cursor.close()

    if username_exists is not None:
        return True

    return False


def email_exists(email: str) -> bool:
    cnx = get_connection()
    cursor = cnx.cursor()

    sql = "SELECT 1 FROM usuario WHERE email = %s;"

    cursor.execute(sql, (email,))

    email_exists = cursor.fetchone()

    cnx.close()
    cursor.close()

    if email_exists is not None:
        return True

    return False


def duplicate_username(username: str) -> bool:
    if username_exists(username):
        return True

    return False


def duplicate_email(email: str) -> bool:
    if email_exists(email):
        return True

    return False
