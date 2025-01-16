from flask import session, jsonify, request
from sqlalchemy.exc import IntegrityError
from app.models.domainModel import Domain
from app.models.whoisModel import Whois
from app.models.wafModel import Waf
from app.models.nameserverModel import Nameserver
from app.models.subdomainModel import Subdomain
from app.models.techModel import Tech
from app.models.portsserviceModel import PortsService
from app.models.userModel import User
from app.extensions import extensiones
from app.utils.core import Core

import os
#from app.utils import 

from typing import Optional, List, Dict

class ReconController:
    """
    Controlador para realizar tareas de reconocimiento sobre dominios.

    Este controlador maneja la obtención de información sobre dominios, 
    incluyendo WHOIS, WAF, y subdominios.
    """

    @staticmethod
    def set_data():
        """
        Establece los datos del dominio a partir del JSON recibido.

        Este método espera recibir un JSON en el cuerpo de la solicitud con la información del dominio.
        Si se establece correctamente, devuelve los datos del dominio.
        El formato esperado es el siguiente:
        {
            "domain": "dominio.com"
        }

        Returns:
            Response: Un objeto JSON que contiene los datos del dominio o un mensaje de error con el código de estado correspondiente.

        Raises:
            Exception: Si ocurre un error inesperado al obtener los datos.
        """
        try:
            data = request.get_json(force=True)
            domain_name = data.get('domain')
            if not extensiones.validators.domain(domain_name):
                return jsonify({'error': 'Dominio inválido.'}), 400
            
            dominio = Domain.lookup(domain_name)
            if not dominio:
                return jsonify({'error': 'Dominio no encontrado.'}), 404

            whois_info = Core.parsearWhois(Core.ejecutar(f"whois {dominio.domain}").split("\n"))
            waf_info = Core.parsearWaf(dominio.domain, Core.parsear(Core.ejecutar(f"wafw00f {dominio.domain}")))
            nameservers = Core.parsearNS(whois_info.get('Name Server').split(", "), Core.escaneoConcurrente([f"dig @{ns} axfr {dominio.domain}" for ns in whois_info.get('Name Server').split(", ")]))

            return jsonify({'whois': whois_info, 'waf': waf_info, 'nameservers': nameservers}), 200

        except Exception as e:
            return jsonify({'error': f'Error al obtener datos: {str(e)}'}), 500
    
    @staticmethod
    def search():
        """
        Busca información sobre un dominio específico.

        Este método espera recibir un JSON en el cuerpo de la solicitud con el nombre del dominio.
        Devuelve información WHOIS y WAF si el dominio es válido.
        El formato esperado es el siguiente:
        {
            "domain": "dominio.com"
        }
        Returns:
            Response: Un objeto JSON que contiene la información del dominio o un mensaje de error con el código de estado correspondiente.

        Raises:
            Exception: Si ocurre un error inesperado durante la búsqueda.
        """
        
        try:
            data = request.get_json(force=True)
            domain_name = data.get('domain')
            if not extensiones.validators.domain(domain_name):
                return jsonify({'error': 'Dominio inválido.'}), 400

            whois = Whois.lookup(domain_name)
            if whois:
                return jsonify({'error': f'Dominio {domain_name} ya existe'}), 404

            dominio = Domain.lookup(domain_name)
            if not dominio:
                return jsonify({'error': 'Dominio no encontrado.'}), 404

            whois = Core.parsearWhois(Core.ejecutar(f"whois {dominio.domain}").split("\n"))
            waf = Core.parsearWaf(Core.ejecutar(f"wafw00f {dominio.domain}"))
            name_queries = [f"dig @{ns} axfr {dominio.domain}" for ns in whois.get('Name Server').split(", ")]
            parsed_nameservers = Core.parsearNS(whois.get('Name Server').split(", "), Core.escaneoConcurrente(name_queries))

            whois_dic = dict(
                domain_id=dominio.id, 
                domain=dominio.domain,
                domain_name = whois['Domain Name'],
                sponsoring_registrar = whois['Sponsoring Registrar'],
                registry_domain_id = whois['Registry Domain ID'],
                registrar_whois_server = whois['Registrar WHOIS Server'],
                registrar_url = whois['Registrar URL'],
                updated_date = whois['Updated Date'],
                creation_date = whois['Creation Date'],
                registry_expiry_date = whois['Registry Expiry Date'],
                registrar = whois['Registrar'],
                registrar_iana_id = whois['Registrar IANA ID'],
                registrar_abuse_contact_email = whois['Registrar Abuse Contact Email'],
                registrar_abuse_contact_phone = whois['Registrar Abuse Contact Phone'],
                domain_status = whois['Domain Status'],
                registrant_name = whois['Registrant Name'],
                admin_name = whois['Admin Name'],
                admin_email = whois['Admin Email'],
                name_server = whois['Name Server'],
                dnssec = whois['DNSSEC'],
                url_ofthe_icann_whois_inaccuracy_complaint_form = whois['URL of the ICANN Whois Inaccuracy Complaint Form'],
                created_at = extensiones.datetime.now()
                )
            extensiones.db.session.add(Whois(**whois_dic))
            
            waf_dict = dict(
                domain_id = dominio.id,
                name = waf[dominio.domain],
                created_at = extensiones.datetime.now()
            )
            extensiones.db.session.add(Waf(**waf_dict))

            for ns in parsed_nameservers:
                nameserver_dict = dict(
                    domain_id = dominio.id,
                    name = ns,
                    zone_transfer = parsed_nameservers[ns],
                    created_at = extensiones.datetime.now()
                )
                extensiones.db.session.add(Nameserver(**nameserver_dict))

            extensiones.db.session.commit()
            return jsonify({'message': f'Datos de {dominio.domain} guardados correctamente.'}), 201
            #return jsonify({'whois': whois_dic, 'waf': waf_dict,'name_server':nameserver_dict}), 200
        except IntegrityError:
            extensiones.db.session.rollback()
            return jsonify({'error': f'Los datos de {dominio.domain} ya existe.'}), 409
        except Exception as e:
            extensiones.db.session.rollback()
            return jsonify({'error': f'Error inesperado al crear el buscar.{e}'}), 500

    @staticmethod
    def searchSubdomains():
        """
        Busca subdominios asociados a un dominio específico.

        Este método espera recibir un JSON en el cuerpo de la solicitud con el nombre del dominio.
        Devuelve una lista de subdominios encontrados.

        El formato esperado es el siguiente:
        {
            "domain": "dominio.com"
        }

        Returns:
            Response: Un objeto JSON que contiene los subdominios o un mensaje de error con el código de estado correspondiente.

        Raises:
            Exception: Si ocurre un error inesperado durante la búsqueda.
        """
        try:
            data = request.get_json(force=True)
            domain_name = data.get('domain')
            
            # Validar el dominio
            if not extensiones.validators.domain(domain_name):
                return jsonify({'error': 'Dominio inválido.'}), 400

            dominio = Domain.lookup(domain_name)
            subdomains = Subdomain.lookup(dominio.id)
            if subdomains:
                return jsonify({'error': f'Los subdominios de {domain_name} ya existe'}), 404
            
            waf_id = Waf.identify(dominio.id)
            if not dominio:
                return jsonify({'error': 'Dominio no encontrado.'}), 404

            comandos_subdominios  = [
                    f"sublist3r -d {dominio.domain}", 
                    f"knockpy -d {dominio.domain}",
                    f"nmap --script dns-brute {dominio.domain}",
                    f"fierce --domain {dominio.domain}",
                    f"dnsmap {dominio.domain}",
                    f"dnsenum --enum --threads 10 --dnsserver 1.1.1.1 --fqdns --noreverse {dominio.domain}",
                    f"subfinder -d {dominio.domain}"
                ]
            # Obtener subdominios)
            subdomains = Core.parsearSubDomain(dominio.domain, Core.escaneoConcurrente(comandos_subdominios))
            subdomains_waf = Core.parsearWaf(Core.escaneoConcurrente([f"wafw00f {sf}" for sf in subdomains]))

            for subdomain, waf in subdomains_waf.items():
                subdomains_data = dict(
                    domain_id = dominio.id,
                    subdomain = subdomain,
                    #waf_id = waf_id.id,
                    waf = waf,
                    created_at = extensiones.datetime.now()
                )
                extensiones.db.session.add(Subdomain(**subdomains_data))

            extensiones.db.session.commit()
            return jsonify({'message': f'Subdominios de {dominio.domain} guardados correctamente.'}), 201
            #return jsonify({'whois': whois_dic, 'waf': waf_dict,'name_server':nameserver_dict}), 200    
        except IntegrityError:
            extensiones.db.session.rollback()
            return jsonify({'error': f'Los subdominios de {dominio.domain} ya existe.'}), 409
        except Exception as e:
            extensiones.db.session.rollback()
            return jsonify({'error': f'Error inesperado al ingresar subdominios.{e}'}), 500
    
    @staticmethod
    def tech():
        data = request.get_json(force=True)
        domain_name = data.get('domain')
        ruta = os.getcwd()
        wappalyzer = os.chdir(f"{ruta}/app/tools/wappalyzer-cli/src")
        print(os.getcwd())
        # Validar el dominio
        if not extensiones.validators.domain(domain_name):
            return jsonify({'error': 'Dominio inválido.'}), 400

        dominio = Domain.lookup(domain_name)
        subdomains = Subdomain.lookup(dominio.id)
        wappy = [f"./wappy -u {s.subdomain}" for s in subdomains]
        whatweb = [f"whatweb {s.subdomain}" for s in subdomains]
        print(wappy)
        result = Core.escaneoConcurrente(wappy)
        return result

    @staticmethod
    def services():
        xml_output_path = f"{os.getcwd()}/result"
    
        # Validar el directorio
        validacion = Core.validarEscaneos(xml_output_path)
        print(validacion)
        if "El directorio no existe" in validacion:
            return jsonify({'error': 'Directorio no encontrado.'}), 400
        if not "El directorio está vacío" in validacion:
            return jsonify({'services': Core.manipularXML(xml_output_path)}), 200

        # Obtener el nombre de dominio y subdominios
        domain_name = request.get_json(force=True).get('domain')
        subdomains = Subdomain.lookup(Domain.lookup(domain_name).id)

        # Generar comandos de escaneo
        services = [
            f"sudo nmap -Pn -f -A -O -sVC -p- {script} {s.subdomain} -oX {os.path.join(xml_output_path, f'scan_{script.split()[-1] if script.split() else 'default'}_{s.subdomain.replace('/', '_')}.xml')} 2>/dev/null"
            for s in subdomains for script in [' ', '--script vuln']
        ]

        print(services)
        #return services
        return Core.escaneoConcurrente(services)

    @staticmethod
    def certificate():
        pass
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