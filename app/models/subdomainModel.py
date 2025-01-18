from app.extensions import extensiones
from datetime import datetime
from app.models.domainModel import Domain
from app.models.wafModel import Waf
"""
Requisitos de la user_class
El argumento user_class suministrado durante la inicialización representa la clase que debe utilizarse para comprobar la autorización de las rutas decoradas. 
La clase en sí puede implementarse de la forma que se considere oportuna. No obstante, debe cumplir los siguientes requisitos:
- Proporcionar un método de clase lookup que:
    - debe tomar como único argumento el nombre del usuario
    - devuelva una instancia de user_class o None
- Proporcionar un método de clase identify:
    - tome como único argumento el identificador único del usuario
    - debe devolver una instancia de user_class o None
- Proporcionar un atributo de instancia rolenames:
    - debe devolver una lista de roles de cadena asignados al usuario
- Proporcionar un atributo de instancia password:
    - debe devolver la contraseña hash asignada al usuario
- Proporcionar un atributo de instancia identity:
    - debe devolver el id único del usuario
"""

class Subdomain(extensiones.db.Model):
    id = extensiones.db.Column(extensiones.db.Integer, primary_key=True)
    domain_id = extensiones.db.Column(extensiones.db.Integer, extensiones.db.ForeignKey('domain.id'), nullable=False)
    subdomain = extensiones.db.Column(extensiones.db.String(64), unique=True, nullable=False)
    waf = extensiones.db.Column(extensiones.db.String(64), nullable=False)
    created_at = extensiones.db.Column(extensiones.db.DateTime, nullable=False, default=extensiones.datetime.utcnow)
    update_at = extensiones.db.Column(extensiones.db.DateTime)
    deleted_at = extensiones.db.Column(extensiones.db.DateTime)
    

    @property
    def identity(self):
        """
        *Atributo o propiedad requerida*
        flask-praetorian requiere que la clase user tenga un atributo o propiedad de instancia ``identity`` 
        que proporcione el id único de la instancia user
        """
        return self.id

    @property
    def rolenames(self):
        """
        *Atributo o propiedad requerida*

        flask-praetorian requiere que la clase user tenga un atributo o propiedad de instancia ``rolenames`` 
        que proporcione una lista de cadenas que describan los roles asociados a la instancia user
        """
        try:
            return self.roles.split(",")
        except Exception:
            return []

    @property
    def password(self):
        """
        *Atributo o propiedad requerida*

        flask-praetorian requiere que la clase user tenga un atributo o propiedad de instancia ``password`` 
        que proporcione la contraseña hash asignada a la instancia user
        """
        return "self.hashed_password"

    @classmethod
    def lookup(cls, domain_id):
        """
        *Método requerido*

        flask-praetorian requiere que la clase user implemente un método de clase ``lookup()`` 
        que tome un único argumento ``username`` y devuelva una instancia de usuario si hay alguna que coincida o ``None`` 
        si no la hay.
        """
        return cls.query.filter_by(domain_id=domain_id).all()

    @classmethod
    def identify(cls, id):
        """
        *Método requerido*

        flask-praetorian requiere que la clase user implemente un método de clase ``identify()`` 
        que tome un único argumento ``id`` y devuelva la instancia de usuario si hay una que coincida o ``None`` 
        si no la hay.
        """
        return cls.query.get(id)

    def is_valid(self):
        return self.is_active

    @classmethod
    def readAll(cls):
        return cls.query.all()

    @classmethod
    def serialize(cls, subdomains):
        if isinstance(subdomains, list):
            serialized_list = []
            for subdomain in subdomains:
                serialized_list.append(cls._serialize_subdomain(subdomain))
            return serialized_list
        elif isinstance(subdomains, cls):
            return cls._serialize_subdomain(subdomains)
        else:
            raise TypeError("Instancia de subdomain esperada o lista de instancias de subdomain")

    @classmethod
    def _serialize_subdomain(cls, subdomain):
        return {
            'id': subdomain.id,
            'domain_id': subdomain.domain_id,
            'subdomain': subdomain.subdomain,
            'waf': subdomain.waf,
            'created_at': subdomain.created_at.isoformat() if subdomain.created_at else None,
            #'update_at': subdomain.update_at.isoformat() if subdomain.update_at else None,
            #'deleted_at': subdomain.deleted_at.isoformat() if subdomain.deleted_at else None,
        }