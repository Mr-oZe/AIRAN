from flask import session, jsonify, request
from sqlalchemy.exc import IntegrityError
from app.models.userModel import User
from app.extensions import extensiones
from app.utils.core import Core

class UserController():
    """
    Controlador para la creación de usuarios.

    Este controlador maneja la creación, lectura, actualización y eliminación de usuarios.
    """
    @staticmethod
    def create():
        """
        Registra un nuevo usuario.

        Este método espera recibir un JSON en el cuerpo de la solicitud con la información del nuevo usuario.
        El formato esperado es el siguiente:

        {
            "name": "Nombre",
            "surname": "Apellido",
            "phone": "1234567890",
            "birthdate": "YYYY-MM-DD",
            "email": "usuario@ejemplo.com",
            "username": "nombredeusuario",
            "profile_picture": "http://ejemplo.com/imagen.jpg",
            "password": "contraseña_secreta",
            "roles": "rol1, rol2"
        }

        Si el registro es exitoso, se devuelve un mensaje de éxito y un código de estado 201.
        Si el usuario ya existe, se devuelve un mensaje de error con un código de estado 409.

        Returns:
            Response: Un objeto JSON que contiene el mensaje de éxito o error y el código de estado correspondiente.

        Raises:
            Exception: Si ocurre un error inesperado durante la creación del usuario.
        """
        
        data = request.get_json()
    
        user_data = dict(
            name = Core.validar(data.get('name', None)),
            surname = Core.validar(data.get('surname', None)),
            phone = data.get('phone', None),
            birthdate = Core.convertir_fecha(data.get('birthdate', None)),
            email = data.get('email', None) if extensiones.validators.email(data.get('email', None)) else None,
            username = data.get('username', None),
            profile_picture = data.get('profile_picture', None) if extensiones.validators.url(data.get('profile_picture', None)) else None,
            hashed_password = extensiones.guard.hash_password(data.get('hashed_password', None)),
            roles = data.get('roles', None),
            created_at = extensiones.datetime.now()
        )

        try:    
            new_user = User(**user_data)
            extensiones.db.session.add(new_user)
            extensiones.db.session.commit()
            #extensiones.guard.send_registration_email(email, user=new_user)
            return (jsonify({'message': f'Correo electrónico de registro enviado exitosamente al usuario {new_user.username}'}), 201)
        except IntegrityError:
            extensiones.db.session.rollback()
            return jsonify({'error': f'El usuario {new_user.username} ya existe.'}), 409
        except Exception as e:
            extensiones.db.session.rollback()
            return jsonify({'error': 'Error inesperado al crear el usuario.'}), 500
        
    @staticmethod
    def readOne(user_id):
        """
        Obtiene un usuario por ID.

        Args:
            user_id (int): El ID del usuario a buscar.

        Returns:
            Response: Un objeto JSON que contiene los datos del usuario o un mensaje de error con el código de estado correspondiente.
        """
        try:
            user = User.identify(user_id)
            return jsonify(User.serialize(user)), 200 if user else jsonify({'error':f'Usuario {user.username}no encontrado'}), 404
        except Exception as e:
            return jsonify({'error': 'Error inesperado al obtener el usuario.'}), 500

    @staticmethod
    def readAll():
        """
        Obtiene todos los usuarios.

        Returns:
            Response: Un objeto JSON que contiene la lista de usuarios o un mensaje de error si no hay usuarios.
        """
        try:
            users = User.readAll()
            return jsonify(User.serialize(users)), 200 if user else jsonify({'error':f'Usuario {users.username}no encontrado'}), 404
        except Exception as e:
            return jsonify({'error': 'Error inesperado al obtener usuarios.'}), 500

    @staticmethod
    def update(user_id):
        """
        Actualiza un usuario existente.

        Este método busca un usuario por su ID y actualiza sus datos con la información proporcionada en el cuerpo de la solicitud.
        El formato esperado es el siguiente:

        {
            "name": "Nuevo Nombre",
            "surname": "Nuevo Apellido",
            "phone": "0987654321",
            "email": "nuevo_usuario@ejemplo.com",
            "username": "nuevo_nombredeusuario",
            "profile_picture": "http://ejemplo.com/nueva_imagen.jpg",
            "roles": ["nuevo_rol1", "nuevo_rol2"]
        }

        Si se encuentra y actualiza correctamente, devuelve un mensaje de éxito con un código de estado 200.
        Si no se encuentra, devuelve un mensaje de error con un código de estado 404.

        Args:
            user_id (int): El ID del usuario a actualizar.

        Returns:
            Response: Un objeto JSON que contiene el mensaje de éxito o error y el código de estado correspondiente.

        Raises:
            Exception: Si ocurre un error inesperado durante la actualización del usuario.
        """
        user = User.identify(user_id)
        if not user:
            return jsonify({'error': f'Usuario {user.username} no encontrado'}), 404

        data = request.get_json()
        # Crear un diccionario con los nuevos valores
        update_user = dict(
            name = Core.validar(data.get('name', user.name)),
            surname = Core.validar(data.get('surname', user.surname)),
            phone = data.get('phone', user.phone),
            email = data.get('email', user.email) if extensiones.validators.email(data.get('email', user.email)) else None,  # Validación de email
            username = data.get('username', user.username),
            profile_picture = data.get('profile_picture', user.profile_picture) if extensiones.validators.url(data.get('profile_picture', user.profile_picture)) else None,  # Validación de URL
            roles = data.get('roles', user.roles),
            update_at = extensiones.datetime.now()
        )

        # Actualizar los atributos del usuario utilizando el diccionario
        for key, value in update_user.items():
            setattr(user, key, value)

        try:
            extensiones.db.session.commit()
            return (jsonify({'message': f'Usuario {user.username} actualizado exitosamente'}), 200)
        except Exception as e:
            extensiones.db.session.rollback()
            return jsonify({'error': 'Error al actualizar el usuario.'}), 500

    @staticmethod
    def delete(user_id):
        """
        Elimina un usuario por ID.

        Args:
            user_id (int): El ID del usuario a eliminar.

        Returns:
             Response: Un objeto JSON que contiene el mensaje de éxito o error y el código de estado correspondiente.
         """
        
        user = User.identify(user_id)
        if not user:
            return jsonify({'error':'Usuario no encontrado'}), 404
        try:
            extensiones.db.session.delete(user)
            extensiones.db.session.commit()
            return jsonify({'msg': f'Usuario {user.username} ha sido eliminado'}), 200
        except Exception:
            extensiones.db.session.rollback()
            return jsonify({'error': 'Error al eliminar el usuario.'}), 500

    @staticmethod
    def forgotPassword():
        """Implementación pendiente para restablecer la contraseña."""
        pass

    @staticmethod
    def disableUser(user_id):
        """
        Deshabilita un usuario por ID.

        Args:
            user_id (int): El ID del usuario a deshabilitar.

        Returns:
            Response: Un objeto JSON que contiene el mensaje de éxito o error y el código de estado correspondiente.
        """
        user = User.identify(user_id)
        if not user:
            return (jsonify({'error':'Usuario no encontrado'}), 404)
        user.is_active = False

        try:
            extensiones.db.session.commit()
            return jsonify({'msg': f'Usuario {user.username} ha sido deshabilitado'}), 200
        except Exception:
            extensiones.db.session.rollback()
            return jsonify({'error': 'Error al deshabilitar el usuario.'}), 500
