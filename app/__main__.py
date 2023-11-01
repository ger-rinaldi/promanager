import locale

from __init__ import create_app
from config import APP_CONFIG

locale.setlocale(locale.LC_ALL, "es_AR.UTF-8")

if __name__ == "__main__":
    app = create_app()
    app.run(**APP_CONFIG)
