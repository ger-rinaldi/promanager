from app.validation.requirements import (
    character_complexity,
    name_max_length,
    name_min_length,
    password_required_length,
    phone_max_length,
    username_max_length,
)

non_unique_username: str = "El nombre de usuario ingresado ya está registrado"

username_bad_length: str = f"El nombre de usuario no puede exceder los \
{username_max_length} y debe superar los {name_min_length}"

pass_too_short: str = f"La contraseña debe tener un mínimo de\
{password_required_length} caractéres"

pass_too_simple: str = f"La contraseña debe contener {character_complexity}\
de los siguientes tipos de caracteres \
minúscula, mayúscula, numéricos y especiales."

invalid_email: str = "La dirección de email ingresada no es válida"

email_alreay_registered: str = "La dirección de email ingresada \
ya está registrada."


name_too_long_short: str = f"Tanto nombre como apellido deben tener entre\
{name_min_length} y {name_max_length} caracteres."

phonetoolong: str = f"El número de teléfono no puede ser mayor a\
{phone_max_length} caracteres"

proy_bad_name: str = f"Nombre de proyecto inválido. Debe contener entre \
{name_min_length} y {name_max_length} caracteres."

bad_budget_type: str = "Tipo de presupuesto inválido. Solo puede contener \
numeros y un punto para decimales"

start_before: str = "Fechas ingresadas inválidas. La fecha de inicio debe ser \
anterior a la de finalización."

end_after_today: str = "Fecha de finalización inválida. El proyecto debe terminar \
después de la fecha corriente."

bad_budget_amount: str = "La cantidad de presupuesto no es válida. debe \
encontrarse entre -2<sup>63</sup> y 2<sup>63</sup>"
