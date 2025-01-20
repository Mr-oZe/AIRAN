import re
import os
import bleach
import subprocess
import concurrent.futures
from html import unescape
from dateutil import parser
from datetime import datetime
from bs4 import BeautifulSoup

class Core():

    @staticmethod
    def convertir_fecha(fecha_str):
        try:
            fecha_obj = parser.parse(fecha_str, dayfirst=True)  # dayfirst=True para manejar formatos con día primero
            return datetime.strptime(fecha_obj.strftime('%d-%m-%Y'), '%d-%m-%Y').date()
        except ValueError as e:
            raise ValueError("Formato de fecha no válido") from e

    @staticmethod
    def validar(data):
        """
        Valida y limpia el texto de entrada eliminando caracteres no deseados y etiquetas HTML.

        Este método utiliza expresiones regulares para eliminar caracteres específicos,
        decodifica entidades HTML y elimina etiquetas HTML utilizando la biblioteca bleach.

        Args:
            data (str): El texto a validar y limpiar.

        Returns:
            str: El texto limpio y validado.

        Raises:
            ValueError: Si el dato de entrada es None o no es una cadena.
        """
        if not isinstance(data, str) or data is None:
            raise ValueError("El dato de entrada debe ser una cadena no vacía.")

        try:
            cleaned_text = bleach.clean(unescape(re.sub(r'[.,:;!?—_\'"`~+*/=%<>&|^√π∞$€£¥¢@#{}\[\]()°©®™§¶†‡¡¿ªº\\]', '', data)), tags=[], attributes={})
            return cleaned_text
        except Exception as e:
            raise RuntimeError(f"Error al validar el texto: {str(e)}")
    
    @staticmethod
    def parsear(data):
        """
        Elimina códigos de escape ANSI de un texto o de cada elemento en una lista.

        Este método procesa el texto o la lista de textos proporcionados, eliminando 
        cualquier código de escape ANSI presente.

        Args:
            data (str | list): El texto o la lista de textos a procesar.

        Returns:
            str | list | None: El texto limpio si se proporciona una cadena, 
                            una lista de textos limpios si se proporciona una lista,
                            o None si el tipo de dato no es válido.

        Raises:
            ValueError: Si el dato de entrada es None.
        """
        if data is None:
            raise ValueError("El dato de entrada no puede ser None.")
        eliminar_codigos_escape = lambda texto: re.sub(r'\x1b\[[0-?9;]*[mK]', '', texto)
        return eliminar_codigos_escape(data.strip()) if isinstance(data, str) else [eliminar_codigos_escape(item) for item in data if isinstance(item, str)]

    @staticmethod
    def ejecutar(command):
        """
        Ejecuta un comando en el sistema operativo y devuelve su salida.

        Args:
            command (str): El comando a ejecutar en el sistema.

        Returns:
            str: La salida estándar del comando sin códigos de escape ANSI.
            str: La salida de error del comando, si ocurre algún error.
        """
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            return Core.parsear(stdout.decode('utf-8'))
        except Exception as e:
            return "", f"Error al ejecutar el comando: {str(e)}"

    @staticmethod
    def escaneoConcurrente(commands):
        """
        Ejecuta una lista de comandos en paralelo.

        Args:
            commands (list): Una lista de comandos a ejecutar.

        Returns:
            list: Una lista con los resultados de cada comando o mensajes de error.
        """
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(Core.ejecutar, cmd): cmd for cmd in commands}
            for future in concurrent.futures.as_completed(futures):
                command = futures[future]
                try:
                    output = future.result()
                    results.append(output if output else f"{command} failed with error: {error}")
                except Exception as exc:
                    results.append(f"{command} generated an exception: {exc}")        
        return results

    @staticmethod
    def parsearWhois(data):
        """
        Parsea la información WHOIS de un conjunto de datos.

        Este método toma una lista de líneas de texto que representan la salida del comando WHOIS
        y extrae información relevante según las etiquetas predefinidas.

        Args:
            data (list): Una lista de cadenas que representan la salida del comando WHOIS.

        Returns:
            dict: Un diccionario con las etiquetas y sus valores correspondientes.

        Raises:
            ValueError: Si el dato de entrada no es una lista.
        """
        if not isinstance(data, list):
            raise ValueError("El dato de entrada debe ser una lista.")

        etiquetas = [
                    "Domain Name",
                    "Sponsoring Registrar",
                    "Registry Domain ID",
                    "Registrar WHOIS Server",
                    "Registrar URL",
                    "Updated Date",
                    "Creation Date",
                    "Registry Expiry Date",
                    "Registrar",
                    "Registrar IANA ID",
                    "Registrar Abuse Contact Email",
                    "Registrar Abuse Contact Phone",
                    "Domain Status",
                    "Registrant Name",
                    "Admin Name",
                    "Admin Email",
                    "Name Server",
                    "DNSSEC",
                    "URL of the ICANN Whois Inaccuracy Complaint Form"
                ]
        # Inicializar diccionarios y listas
        r = {etiqueta: None for etiqueta in etiquetas}
        name_servers = []
        for texto in data:
            partes = texto.split(":", 1)
            if len(partes) == 2:
                llave, valor = partes[0].strip(), partes[1].strip()
                if llave in etiquetas:
                    r[llave] = valor
                    if llave == "Name Server":
                        name_servers.append(valor)

        # Asignar la lista de name_servers al diccionario r si existen elementos
        if name_servers:
            # Filtrar valores no vacíos y eliminar duplicados
            r["Name Server"] = ', '.join(set(filter(None, name_servers)))

        return r
    
    @staticmethod
    def parsearWaf(data):
        """
        Parsea la información de detección de WAF a partir de una cadena o lista de cadenas.

        Este método busca frases específicas en el texto proporcionado y determina si hay un WAF presente.

        Args:
            data (str | list): Una cadena con la salida del escaneo WAF o una lista de cadenas.

        Returns:
            dict: Un diccionario con el subdominio y el mensaje correspondiente sobre la detección del WAF.

        Raises:
            ValueError: Si el dato de entrada no es una cadena ni una lista.
        """
        if not isinstance(data, (str, list)):
            return {"WAF": "Formato de datos no válido"}

        # Frases a buscar
        frases_a_buscar = {
            "No WAF detected by the generic detection": "No contiene WAF",
            "is behind": " "  # Placeholder para la expresión regular
        }

        def procesar_texto(texto):
            """Función interna para procesar el texto y buscar subdominios."""
            patron = r'\[\*] Checking https://([^/\n]+)'  # Captura hasta un salto de línea
            subdominio_match = re.search(patron, texto)
            
            if subdominio_match:
                subdominio = subdominio_match.group(1)
                for frase, mensaje in frases_a_buscar.items():
                    if frase in texto:
                        coincidencia = re.search(r'behind (.+?) WAF', texto)
                        return {subdominio: coincidencia.group(1) if coincidencia else mensaje}
                return {subdominio: "Falló al conectar"}
            
            return {}

        # Procesar según el tipo de datos
        if isinstance(data, str):
            return procesar_texto(data)
        
        resultados = {}
        for item in data:
            resultado = procesar_texto(item)
            resultados.update(resultado)  # Actualiza el diccionario con el resultado                            

        return resultados

    @staticmethod
    def parsearNS(ns, data):
        """
        Parsea la información de los servidores de nombres y verifica mensajes específicos en los datos proporcionados.

        Este método toma una lista de servidores de nombres y un conjunto de datos, 
        buscando frases específicas para determinar el estado de cada servidor.

        Args:
            ns (list): Una lista de servidores de nombres.
            data (list): Una lista de cadenas que representan la salida del escaneo.

        Returns:
            dict: Un diccionario donde las claves son los servidores de nombres y los valores son mensajes sobre su estado.

        Raises:
            ValueError: Si los argumentos no son del tipo esperado.
        """
        if not isinstance(ns, list) or not isinstance(data, list):
            raise ValueError("Ambos argumentos deben ser listas.")

        name_servers_dict = {}        
        # Definir las frases a buscar y sus mensajes
        frases_a_buscar = {
            "Transfer failed": "Falló la transferencia de zona",
            "no servers could be reached": "Sin acceso"
        }
        # Convertir data a un conjunto para búsquedas más rápidas
        data_set = set(data)
        # Iterar sobre los servidores de nombres
        for index, nameserver in enumerate(ns, start=1):
            key = f"Name Server {index}"            
            # Verificar las frases en el conjunto de data
            for frase, mensaje in frases_a_buscar.items():
                if any(frase in entry for entry in data_set):
                    name_servers_dict[nameserver] = mensaje  # Asignar solo el mensaje si se encuentra una frase
                    continue
        return name_servers_dict

    @staticmethod
    def parsearSubDomain(dominio, data):
        """
        Parsea subdominios a partir de una lista de cadenas de texto.

        Este método busca subdominios que pertenecen al dominio especificado en los datos proporcionados.

        Args:
            dominio (str): El dominio principal para el cual se buscan subdominios.
            data (list): Una lista de cadenas que representan la salida del escaneo.

        Returns:
            list: Una lista de subdominios únicos encontrados.

        Raises:
            ValueError: Si el dominio no es una cadena o si los datos no son una lista.
        """
        if not isinstance(dominio, str) or not isinstance(data, list):
            raise ValueError("El dominio debe ser una cadena y los datos deben ser una lista.")

        subdominios_set = set()  # Usar un conjunto para almacenar subdominios únicos

        for d in data:            
            # Expresión regular para encontrar subdominios con el dominio especificado
            pattern = rf'([a-zA-Z0-9-]+)\.{re.escape(dominio)}'            
            subdominios_set.update(f'{sub}.{dominio}' for sub in re.findall(pattern, d))

        return list(subdominios_set)  # Convertir el conjunto a lista antes de devolver
    
    @staticmethod
    def manipularXML(directorio_xml):
        """
        archivos = os.listdir(ruta)
        #Filtrar archivos que coincidan con el formato específico
        archivos_xml = [archivo for archivo in archivos if archivo.endswith('.xml') and archivo.startswith('scan_')]
        if archivos_xml:
            print("Se encontraron archivos con el formato 'scan_dominio.com.xml':")
            for archivo in archivos_xml:
                return (archivo)
        else:
            print("No se encontraron archivos con el formato 'scan_dominio.com.xml'.")
        """
        # Inicializar listas para almacenar resultados
        resultados = []

        # Iterar sobre todos los archivos en el directorio
        for nombre_archivo in os.listdir(directorio_xml):
            if nombre_archivo.endswith('.xml') and nombre_archivo.startswith('scan_'):
                ruta_archivo = os.path.join(directorio_xml, nombre_archivo)

                # Abrir y leer el archivo XML
                with open(ruta_archivo, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file.read(), 'xml')

                # Extraer información de puertos
                puertos = soup.find_all('port')
                dominio = nombre_archivo[5:-4]  # Quitar 'scan_' y '.xml'

                print(f"Contenido de {nombre_archivo}: {dominio}\n")

                # Inicializar listas para cada archivo
                portid = [puerto['portid'] for puerto in puertos]
                protocol = [puerto['protocol'] for puerto in puertos]
                estado = [puerto.find('state')['state'] for puerto in puertos]
                servicio = [puerto.find('service')['name'] if puerto.find('service') else 'Desconocido' for puerto in puertos]

                # Agregar resultados a la lista
                resultados.append({
                    'dominio': dominio,
                    'portid': portid,
                    'protocol': protocol,
                    'estado': estado,
                    'servicio': servicio
                })
        return resultados

    @staticmethod
    def validarEscaneos(ruta):
        if not os.path.isdir(ruta):
            #print("El directorio no existe.")
            return "El directorio no existe"

        # Listar los archivos en el directorio
        archivos = os.listdir(ruta)

        if not archivos:
            #print("El directorio está vacío.")
            return "El directorio está vacío"
            #return False
        

        
        
