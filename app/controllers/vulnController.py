from flask import session, jsonify, request
from app.models.subdomainModel import Subdomain
from app.models.domainModel import Domain
from app.models.vulnModel import Vuln
from app.extensions import extensiones
from app.utils.core import Core
import os 

#from app.utils import 

class VulnController():

    @staticmethod
    def search():
        xml_output_path = f"{os.getcwd()}/result"
        #xml_output_file = os.path.join(xml_output_path, f"scan_vuln_{target.replace('/', '_')}.xml")
        data = request.get_json(force=True)
        domain_name = data.get('domain')
        dominio = Domain.lookup(domain_name)
        subdomains = Subdomain.lookup(dominio.id)
        vuln = ['--script auth','--script brute','--script default','--script exploit','--script fuzzer','--script intrusive','--script vuln']
        #services = [f"sudo nmap -Pn -f --mtu 24 -D RND:10 --min-rate 2000 --max-rate 5000 --max-retries 2 --defeat-rst-ratelimit --randomize-hosts -sV -p- {vuln} {s.subdomain}" for s in subdomains ]
        services = [
            f"sudo nmap -Pn -f --mtu 24 -D RND:10 --min-rate 2000 --max-rate 5000 "
            f"--max-retries 2 --defeat-rst-ratelimit --randomize-hosts -sV -p- {script} {s.subdomain} -oX {os.path.join(xml_output_path, f"scan_{script.split(" ")[-1]}_{s.subdomain.replace('/', '_')}.xml")} 2>/dev/null"
            for s in subdomains for script in vuln
        ]
        print(len(services))
        return services
    
    '''
    def create():
        """
        Registers a new user by parsing a POST request containing new user info and
        dispatching an email with a registration token

        .. example::
        $ curl http://localhost:5000/register -X POST \
            -d '{
            "username":"Brandt", \
            "password":"herlifewasinyourhands" \
            "email":"brandt@biglebowski.com"
            }'
        """
        # new_user = User(
        #    username=username,
        #    password=guard.hash_password(password),
        #    roles='operator',
        # )
        # birthdate = extensiones.convertir_fecha(req.get('birthdate', None)),
        # birthdate = extensiones.datetime.strptime(req.get('birthdate', None), '%d-%m-%Y').date(),
        data = request.get_json()
        #core.validar(data)
        # return ""
        
        new_user = User(
            name = core.validar(data.get('name', None)),
            surname = core.validar(data.get('surname', None)),
            phone = data.get('phone', None),
            birthdate = core.convertir_fecha(data.get('birthdate', None)),
            email = data.get('email', None) if extensiones.validators.email(data.get('email', None)) else None,
            username = data.get('username', None),
            profile_picture = data.get('profile_picture', None) if extensiones.validators.url(data.get('profile_picture', None)) else None,
            hashed_password = extensiones.guard.hash_password(data.get('hashed_password', None)),
            created_at = extensiones.datetime.now()
        )
        
        try:
            extensiones.db.session.add(new_user)
            extensiones.db.session.commit()
            #extensiones.guard.send_registration_email(email, user=new_user)
            ret = {'message': 'Correo electrónico de registro enviado exitosamente al usuario {}'.format(
                new_user.username
            )}
            return (jsonify(ret), 201)
        except Exception as e:
            extensiones.db.session.rollback()
            ret = {'error': str(e)}
            return (jsonify(ret), 500)
        

    def readOne(user_id):
        user = User.identify(user_id)
        if user:
            return (jsonify(User.serialize(user)), 201)
        else:
            return (jsonify({'error':'Usuario no encontrado'}), 404)
    

    def readAll():
        users = User.readAll()
        if users:
            return (jsonify(User.serialize(users)), 201)
        else:
            return (jsonify({'error':'Usuario no encontrado'}), 404)

    def update(user_id):
        user = User.identify(user_id)
        if user:
            data = request.get_json()
            #user.name = data.get('name', user.name)
            
            data = request.get_json()

            user.name = core.validar(data.get('name', user.name))
            user.surname = core.validar(data.get('surname', user.surname))
            user.phone = data.get('phone', user.phone)
            user.email = data.get('email', user.email) if extensiones.validators.email(data.get('email', user.email)) else None  # Validación de email
            user.username = data.get('username', user.username)
            user.profile_picture = data.get('profile_picture', user.profile_picture) if extensiones.validators.url(data.get('profile_picture', user.profile_picture)) else None  # Validación de URL
            user.update_at = extensiones.datetime.now()

            """
            user.name = extensiones.validar(data.get('name')),
            user.surname = extensiones.validar(data.get('surname', user.surname)),
            user.phone = data.get('phone', user.phone),
            user.email = data.get('email', user.email) if extensiones.validators.email(data.get('email', user.email)) else None,
            user.username = data.get('username', user.username),
            user.profile_picture = data.get('profile_picture', user.profile_picture) if extensiones.validators.url(data.get('profile_picture', user.profile_picture)) else None,
            user.update_at = extensiones.datetime.now()
            """

            try:
                extensiones.db.session.commit()
                return (jsonify({'message': f'Usuario {user.username} actualizado exitosamente'}), 200)
            except Exception as e:
                print(e)
                extensiones.db.session.rollback()
                return (jsonify({'error':'Usuario no encontrado'}), 404)


    def delete(user_id):
        user = User.identify(user_id)
        if not user:
            return (jsonify({'error':'Usuario no encontrado'}), 404)
        extensiones.db.session.delete(user)
        extensiones.db.session.commit()
        return (jsonify({'msg':f'Usuario {user.username} ha sido eliminado'}), 201)

    def forgotPassword():
        data = request.get_json()

    def disableUser(user_id):
        user = User.identify(user_id)
        if not user:
            return (jsonify({'error':'Usuario no encontrado'}), 404)

        data = request.get_json()
        user.is_active = False
        extensiones.db.session.commit()
        return (jsonify({'msg':f'Usuario {user.username} ha deshabilitado'}), 201)
    '''