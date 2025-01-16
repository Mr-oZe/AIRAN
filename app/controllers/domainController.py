from flask import session, jsonify, request
from app.models.domainModel import Domain
from app.models.userModel import User
from app.extensions import extensiones
from app.utils.core import Core

class DomainController():

    @staticmethod
    def insert():
        """
        Registra un nuevo dominio asociado a un usuario.

        Este método espera recibir un JSON en el cuerpo de la solicitud con la información del dominio.
        El formato esperado es el siguiente:
        {
            "user_id": "123",
            "domain": "ejemplo.com",
            "logo": "url_del_logo"
        }

        Returns:
            Response: Un objeto JSON que contiene un mensaje de éxito o error con el código de estado correspondiente.
        """
        data = request.get_json()
        user = User.identify(data.get('user_id'))

        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        domain_dict = dict(
            user_id = Core.validar(data.get('user_id', None)),
            domain = data.get('domain', None) if extensiones.validators.domain(data.get('domain', None)) else None,
            logo = Core.validar(data.get('logo', None)),
            
            #waf_id = Core.validar(data.get('waf_id', None)),
            created_at = extensiones.datetime.now()
        )

        try:
            extensiones.db.session.add(Domain(**domain_dict))
            extensiones.db.session.commit()
            #extensiones.guard.send_registration_email(email, user=new_user)
            return (jsonify({'message': f'Dominio {domain_dict["domain"]} guardado exitosamente'}), 200)
        except Exception as e:
            extensiones.db.session.rollback()
            return (jsonify({'error':f'Dominio {domain_dict["domain"]} ya está registrado'}), 409)
        
    @staticmethod
    def readOne(domain_id):
        """
        Obtiene la información de un dominio por su ID.

        Args:
            domain_id (int): El ID del dominio a buscar.

        Returns:
            Response: Un objeto JSON que contiene la información del dominio o un mensaje de error con el código de estado correspondiente.
        """
        domain = Domain.identify(domain_id)
        return (jsonify(Domain.serialize(domain)), 200) if domain else (jsonify({'error': 'Dominio no encontrado'}), 404)
    
    @staticmethod
    def readAll():
        """
        Obtiene la lista de todos los dominios registrados.

        Returns:
            Response: Un objeto JSON que contiene la lista de dominios o un mensaje de error con el código de estado correspondiente.
        """
        domains = Domain.readAll()
        return (jsonify(Domain.serialize(domains)), 200) if domains else (jsonify({'error': 'Dominios no encontrados'}), 404)

    @staticmethod
    def update(domain_id):
        """
        Actualiza la información de un dominio existente.
        El formato esperado es el siguiente:
        {
            "user_id": "123",
            "domain": "ejemplo.com",
            "logo": "url_del_logo"
        }

        Args:
            domain_id (int): El ID del dominio a actualizar.

        Returns:
            Response: Un objeto JSON que contiene un mensaje de éxito o error con el código de estado correspondiente.
        """
        domains = Domain.identify(domain_id)
        if not domain:
            return jsonify({'error': 'Dominio no encontrado'}), 404

        data = request.get_json()            
        update_domain = dict(
            domain = data.get('domain', None) if extensiones.validators.domain(data.get('domain', None)) else None,
            logo = Core.validar(data.get('logo', None)),
            update_at = extensiones.datetime.now()  # Actualiza la fecha de actualización en la base de datos.  
        )
        for key, value in update_domain.items():
                setattr(user, key, value)

        try:
            extensiones.db.session.commit()
            return (jsonify({'message': f'Dominio {domains.domain} actualizado exitosamente'}), 200)
        except Exception as e:
            extensiones.db.session.rollback()
            return jsonify({'error': 'Error al actualizar el usuario.'}), 500

    @staticmethod
    def delete(domain_id):
        """
        Elimina un dominio por su ID.

        Args:
            domain_id (int): El ID del dominio a eliminar.

        Returns:
            Response: Un objeto JSON que contiene un mensaje de éxito o error con el código de estado correspondiente.
        """
        domain = Domain.identify(domain_id)
        if not domain:
            return (jsonify({'error':'Dominio no encontrado'}), 404)

        try:
            extensiones.db.session.delete(domain)
            extensiones.db.session.commit()
            return jsonify({'msg': f'Dominio {domain.domain} ha sido eliminado'}), 200
        except Exception as e:
            extensiones.db.session.rollback()
            return jsonify({'error': 'Error al eliminar el dominio: ' + str(e)}), 500

