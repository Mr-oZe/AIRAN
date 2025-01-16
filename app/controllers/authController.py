from flask import session, jsonify, request
from app.models.userModel import User
from app.extensions import extensiones

MAX_LOGIN_ATTEMPTS = 3

class AuthController():
    """
    Controlador para la autenticación de usuarios.

    Este controlador maneja el inicio de sesión y la gestión de tokens JWT.
    """

    @staticmethod
    def login():
        """
        Inicia sesión de un usuario.

        Este método espera recibir un JSON en el cuerpo de la solicitud con las credenciales del usuario.
        El formato esperado es el siguiente:

        {
            "username": "NombreDeUsuario",
            "password": "Contraseña"
        }

        Returns:
            Response: Un objeto JSON que contiene el token de acceso o un mensaje de error con el código de estado correspondiente.

        Raises:
            Exception: Si ocurre un error inesperado durante el proceso de inicio de sesión.
        """
        try:
            req = request.get_json(force=True)
            username, password = req.get("username"), req.get("password")
            user = User.lookup(username)

            if not user:
                return jsonify({'error': 'Usuario no encontrado.'}), 404

            if extensiones.guard.authenticate(username, password):
                user.last_login = extensiones.datetime.now()
                extensiones.db.session.commit()
                access_token = extensiones.guard.encode_jwt_token(user)
                return jsonify({"access_token": access_token}), 200
            
            return jsonify({'error': 'Credenciales inválidas.'}), 401
            
        except extensiones.praetorian.exceptions.PraetorianError:
            return jsonify({'error': 'Nombre de usuario o contraseña inválidos.'}), 401        
        except Exception as e:
            return jsonify({'error': 'Ocurrió un error inesperado.'}), 500

    @staticmethod
    def logout():
        """
        Cierra la sesión del usuario.

        Este método invalida el token del usuario. La implementación específica depende del mecanismo de gestión de sesiones o tokens.

        Returns:
            Response: Un objeto JSON que indica que la sesión ha sido cerrada exitosamente.
        """
        # Implementación pendiente
        return jsonify({'message': 'Sesión cerrada exitosamente.'}), 200
    
    @staticmethod
    def refresh():
        """
        Refresca el token JWT del usuario.

        Este método genera un nuevo token JWT utilizando el token actual. 
        Se espera que el token actual sea válido.

        Returns:
            Response: Un objeto JSON que contiene el nuevo token de acceso o un mensaje de error con el código de estado correspondiente.
        """
        # Implementación pendiente
        return jsonify({'message': 'Token refrescado exitosamente.'}), 200