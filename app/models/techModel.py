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

class Tech(extensiones.db.Model):
    id = extensiones.db.Column(extensiones.db.Integer, primary_key=True)
    subdomain_id = extensiones.db.Column(extensiones.db.Integer, extensiones.db.ForeignKey('subdomain.id'), nullable=False)
    tech_data = extensiones.db.Column(extensiones.db.String(64), nullable=True)
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
    def serialize(cls, techs):
        if isinstance(techs, list):
            serialized_list = []
            for tech in techs:
                serialized_list.append(cls._serialize_tech(tech))
            return serialized_list
        elif isinstance(techs, cls):
            return cls._serialize_tech(techs)
        else:
            raise TypeError("Instancia de tech esperada o lista de instancias de tech")

    @classmethod
    def _serialize_tech(cls, tech):
        return {
            'id': tech.id,
            'subdomain_id': tech.subdomain_id,
            'tech_data': tech.tech_data,
            'created_at': tech.created_at.isoformat() if tech.created_at else None,
            #'update_at': tech.update_at.isoformat() if tech.update_at else None,
            #'deleted_at': tech.deleted_at.isoformat() if tech.deleted_at else None,
        }