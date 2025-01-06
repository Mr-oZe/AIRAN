from os import environ
import tempfile

class Config():
    # Configuración de api
    SECRET_KEY = environ.get("SECRET_KEY")
    JWT_ACCESS_LIFESPAN = {"hours": 12}
    JWT_REFRESH_LIFESPAN = {"days": 30}
    # Configuración de base de datos
    #local_database = tempfile.NamedTemporaryFile(prefix="local", suffix=".db")
    local_database = "airan.db"
    SQLALCHEMY_DATABASE_URI= "sqlite:///{}".format(local_database)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Configuración de correo electrónico
    MAIL_SERVER = environ.get("MAIL_SERVER")
    MAIL_PORT = environ.get("MAIL_PORT")
    MAIL_USERNAME = environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = environ.get("MAIL_PASSWORD")
    MAIL_USE_TLS = environ.get("MAIL_USE_TLS")
    MAIL_USE_SSL = environ.get("MAIL_USE_SSL")
    
