from app.extensions import extensiones
from datetime import datetime
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

class User(extensiones.db.Model):
    id = extensiones.db.Column(extensiones.db.Integer, primary_key=True, autoincrement=True)
    name = extensiones.db.Column(extensiones.db.String(64), nullable=False)
    surname = extensiones.db.Column(extensiones.db.String(64), nullable=False)
    phone = extensiones.db.Column(extensiones.db.String(64), nullable=False)
    birthdate = extensiones.db.Column(extensiones.db.DateTime, nullable=False)
    email = extensiones.db.Column(extensiones.db.String(120), unique=True, nullable=False)
    username = extensiones.db.Column(extensiones.db.String(64), unique=True, nullable=False)
    profile_picture = extensiones.db.Column(extensiones.db.String(256), nullable=False)
    hashed_password = extensiones.db.Column(extensiones.db.Text)
    roles = extensiones.db.Column(extensiones.db.Text)
    is_active = extensiones.db.Column(extensiones.db.Boolean, default=True, server_default="true")
    created_at = extensiones.db.Column(extensiones.db.DateTime, nullable=False, default=extensiones.datetime.utcnow)
    update_at = extensiones.db.Column(extensiones.db.DateTime, onupdate=datetime.utcnow)
    deleted_at = extensiones.db.Column(extensiones.db.DateTime)
    last_login = extensiones.db.Column(extensiones.db.DateTime)
    

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
        return self.hashed_password

    @classmethod
    def lookup(cls, username):
        """
        *Método requerido*

        flask-praetorian requiere que la clase user implemente un método de clase ``lookup()`` 
        que tome un único argumento ``username`` y devuelva una instancia de usuario si hay alguna que coincida o ``None`` 
        si no la hay.
        """
        return cls.query.filter_by(username=username).one_or_none()

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
    def serialize(cls, users):
        if isinstance(users, list):
            serialized_list = []
            for user in users:
                serialized_list.append(cls._serialize_user(user))
            return serialized_list
        elif isinstance(users, cls):
            return cls._serialize_user(users)
        else:
            raise TypeError("Expected User instance or list of User instances")

    @classmethod
    def _serialize_user(cls, user):
        return {
            'id': user.id,
            'name': user.name,
            'surname': user.surname,
            #'phone': user.phone,
            #'birthdate': user.birthdate.isoformat() if user.birthdate else None,
            'email': user.email,
            'username': user.username,
            'profile_picture': user.profile_picture,
            #'roles': user.rolenames,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            #'update_at': user.update_at.isoformat() if user.update_at else None,
            #'deleted_at': user.deleted_at.isoformat() if user.deleted_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
        }