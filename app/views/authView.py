from app.controllers.authController import AuthController
from flask import Blueprint

auth_blueprint = Blueprint("auth",__name__)

@auth_blueprint.route("/login", methods=["POST"])
def login():
    return AuthController.login()

@auth_blueprint.route("/logout", methods=["POST"])
def logout():
    return AuthController.login()

@auth_blueprint.route("/refresh", methods=["POST"])
def refresh():
    return AuthController.login()