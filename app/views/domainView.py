from app.controllers.domainController import DomainController
#from app.controllers.userController import UserController
from flask import Blueprint
from app.extensions import extensiones

domain_blueprint = Blueprint("domain",__name__)

@domain_blueprint.route("/insert", methods=["POST"])
@extensiones.praetorian.auth_required
def insert():
    return DomainController.insert()

# Ver un solo usuario
@domain_blueprint.route("/<int:domain_id>", methods=["GET"])
@extensiones.praetorian.auth_required
def listOneDomain(domain_id):
    return DomainController.readOne(domain_id)

# Ver todos los usuarios
@domain_blueprint.route("/", methods=["GET"])
@extensiones.praetorian.auth_required
def listAllDomain():
    return DomainController.readAll()

@domain_blueprint.route('/<int:domain_id>', methods=['PUT'])
@extensiones.praetorian.auth_required
def update_single_domain(domain_id):
    return DomainController.update(domain_id)

@domain_blueprint.route('/<int:domain_id>', methods=['DELETE'])
@extensiones.praetorian.auth_required
def delete_single_domain(domain_id):
    return DomainController.delete(domain_id)
