from application import create_app
from config import APP_CONFIG

if __name__ == "__main__":
    app = create_app(APP_CONFIG)
    app.run(**APP_CONFIG)
