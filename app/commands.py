import click
from flask.cli import with_appcontext

from .extensions import extensiones
from app.models.userModel import User

from flask import current_app
from sqlalchemy.exc import OperationalError

@click.command(name="create_database")
@with_appcontext
def create_database():
    extensiones.db.create_all()

@click.command(name="test_database")
@with_appcontext
def test_database():
    try:
        # Obtener la conexión de la base de datos
        
        return True
    except OperationalError:
        return False

@click.command(name="create_users")
@with_appcontext
def create_users():
    one = User(username="One",hashed_password=extensiones.guard.hash_password('one'), roles="admin", is_active=True)
    two = User(username="Two",hashed_password=extensiones.guard.hash_password('two'), roles="test", is_active=True)
    three = User(username="Three",hashed_password=extensiones.guard.hash_password('three'), roles="developer", is_active=True)

    extensiones.db.session.add_all([one, two, three])
    extensiones.db.session.commit()