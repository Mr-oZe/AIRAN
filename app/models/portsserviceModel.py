from app.extensions import extensiones
from datetime import datetime
from app.models.subdomainModel import Subdomain
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

class PortsService(extensiones.db.Model):
    id = extensiones.db.Column(extensiones.db.Integer, primary_key=True)
    subdomain_id = extensiones.db.Column(extensiones.db.Integer, extensiones.db.ForeignKey('subdomain.id'), nullable=False)
    services_open = extensiones.db.Column(extensiones.db.String(64), nullable=True)
    services_close = extensiones.db.Column(extensiones.db.String(64), nullable=True)
    services_filtered = extensiones.db.Column(extensiones.db.String(64), nullable=True)
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
    def lookup(cls, subdomain_id):
        """
        *Método requerido*

        flask-praetorian requiere que la clase user implemente un método de clase ``lookup()`` 
        que tome un único argumento ``username`` y devuelva una instancia de usuario si hay alguna que coincida o ``None`` 
        si no la hay.
        """
        return cls.query.filter_by(subdomain_id=subdomain_id).one_or_none()

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
    def serialize(cls, portservices):
        if isinstance(portservices, list):
            serialized_list = []
            for portservice in portservices:
                serialized_list.append(cls._serialize_portservice(portservice))
            return serialized_list
        elif isinstance(portservices, cls):
            return cls._serialize_portservice(portservices)
        else:
            raise TypeError("Instancia de portservice esperada o lista de instancias de portservice")

    @classmethod
    def _serialize_portservice(cls, portservice):
        return {
            'id': portservice.id,
            'subdomain_id': portservice.subdomain_id,
            'services_open': portservice.services_open,
            'services_close': portservice.services_close,
            'services_filtered': portservice.services_filtered,
            'created_at': portservice.created_at.isoformat() if portservice.created_at else None,
            #'update_at': portservice.update_at.isoformat() if portservice.update_at else None,
            #'deleted_at': portservice.deleted_at.isoformat() if portservice.deleted_at else None,
        }