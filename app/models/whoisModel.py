from app.extensions import extensiones
from datetime import datetime
from app.models.domainModel import Domain
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

class Whois(extensiones.db.Model):
    id = extensiones.db.Column(extensiones.db.Integer, primary_key=True)
    domain_id = extensiones.db.Column(extensiones.db.Integer, extensiones.db.ForeignKey('domain.id'), nullable=False)
    domain = extensiones.db.Column(extensiones.db.String(64), unique=True, nullable=False)
    domain_name = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    sponsoring_registrar = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    registry_domain_id = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    registrar_whois_server = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    registrar_url = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    updated_date = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    creation_date = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    registry_expiry_date = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    registrar = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    registrar_iana_id = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    registrar_abuse_contact_email = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    registrar_abuse_contact_phone = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    domain_status = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    registrant_name = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    admin_name = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    admin_email = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    name_server = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    dnssec = extensiones.db.Column(extensiones.db.String(256), nullable=True)
    url_ofthe_icann_whois_inaccuracy_complaint_form = extensiones.db.Column(extensiones.db.String(256), nullable=True)
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
    def lookup(cls, domain):
        """
        *Método requerido*

        flask-praetorian requiere que la clase user implemente un método de clase ``lookup()`` 
        que tome un único argumento ``username`` y devuelva una instancia de usuario si hay alguna que coincida o ``None`` 
        si no la hay.
        """
        return cls.query.filter_by(domain=domain).one_or_none()

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
    def serialize(cls, whois):
        if isinstance(whois, list):
            serialized_list = []
            for w in whois:
                serialized_list.append(cls._serialize_whois(w))
            return serialized_list
        elif isinstance(whois, cls):
            return cls._serialize_whois(whois)
        else:
            raise TypeError("Instancia de whois esperada o lista de instancias de whois")

    @classmethod
    def _serialize_whois(cls, whois):
        return {
            'id': whois.id,
            'domain_id': whois.domain_id,
            'domain': whois.domain,
            'domain_name': whois.domain_name,
            'sponsoring_registrar': whois.sponsoring_registrar,
            'registry_domain_id': whois.registry_domain_id,
            'registrar_whois_server': whois.registrar_whois_server,
            'registrar_url': whois.registrar_url,
            'updated_date': whois.updated_date,
            'creation_date': whois.creation_date,
            'registry_expiry_date': whois.registry_expiry_date,
            'registrar': whois.registrar,
            'registrar_iana_id': whois.registrar_iana_id,
            'registrar_abuse_contact_email': whois.registrar_abuse_contact_email,
            'registrar_abuse_contact_phone': whois.registrar_abuse_contact_phone,
            'domain_status': whois.domain_status,
            'registrant_name': whois.registrant_name,
            'admin_name': whois.admin_name,
            'admin_email': whois.admin_email,
            'name_server': whois.name_server,
            'dnssec': whois.dnssec,
            'url_ofthe_icann_whois_inaccuracy_complaint_form': whois.admin_name,
            'created_at': whois.created_at.isoformat() if whois.created_at else None,
            #'update_at': whois.update_at.isoformat() if whois.update_at else None,
            #'deleted_at': whois.deleted_at.isoformat() if whois.deleted_at else None,
        }