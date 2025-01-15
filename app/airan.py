from extensions import extensiones
from utils.core import Core
import json

class Airan:
    def __init__(self, dominio, dominio_id):
        self.dominio = dominio
        self.whois_headers = [
                'Domain Name', 'Sponsoring Registrar', 'Registry Domain ID',
                'Registrar WHOIS Server', 'Registrar URL', 'Updated Date',
                'Creation Date', 'Registry Expiry Date', 'Registrar',
                'Registrar IANA ID', 'Registrar Abuse Contact Email',
                'Registrar Abuse Contact Phone', 'Domain Status',
                'Registrant Name', 'Admin Name', 'Admin Email',
                'Name Server', 'DNSSEC', 
                'URL of the ICANN Whois Inaccuracy Complaint Form'
            ]
        self.dominio_id = dominio_id
        self.commands = {
            'whois': [f"whois {dominio}"],
            'waf': [f"wafw00f {dominio}"],
            'subdomains': [
                f"sublist3r -d {dominio}", f"knockpy -d {dominio}",
                f"nmap --script dns-brute {dominio}", f"fierce --domain {dominio}",
                f"dnsmap {dominio}", f"dnsenum --enum --threads 10 --dnsserver 1.1.1.1 --fqdns --noreverse {dominio}",
                f"subfinder -d {dominio}"
            ]
        }
        self.name_servers = []

    def _execute_command(self, command_key):
        return Core.ejecutar(self.commands[command_key])

    def get_whois(self):
        return Core.parsearWhois(self._execute_command('whois').split("\n"))

    def get_waf(self):
        return Core.parsearWaf(self._execute_command('waf'))

    def get_name_servers(self):
        ns_list = self.get_whois().get('Name Server').split(", ")
        self.name_queries = [f"dig @{ns} axfr {self.dominio}" for ns in ns_list]
        return Core.parsearNS(ns_list, Core.escaneoConcurrente(self.name_queries))

    def get_subdomains(self):
        subdomains = Core.parsearSubDomain(self.dominio, Core.escaneoConcurrente(self.commands['subdomains']))
        subdomains_waf = Core.parsearWaf(Core.escaneoConcurrente([f"wafw00f {sf}" for sf in subdomains]))
        return Core.parsearWaf(Core.escaneoConcurrente([f"wafw00f {sf}" for sf in subdomains]))

    def get_json(self):
        whois_data = self.get_whois()
        waf_data = self.get_waf()

        whois_dic = {
            'domain_id': self.dominio_id,
            'domain': self.dominio,
            **{key: whois_data.get(key) for key in self.whois_headers},
            'created_at': extensiones.datetime.now()
        }

        waf_dict = {
            'domain_id': self.dominio_id,
            'name': waf_data.get(self.dominio),
            'created_at': extensiones.datetime.now()
        }

        name_servers_info = [
            {
                'domain_id': self.dominio_id,
                'name': ns,
                #zone_transfer = parsed_nameservers[ns],
                'zone_transfer_id': self.get_name_servers().get(ns),
                'created_at': extensiones.datetime.now()
            } for ns in self.get_name_servers()
        ]
        #subdomains_info = [
        #    {
        #        'domain_id': self.dominio_id,
        #        'name': subdomain,
        #        'waf': waf,
        #        'created_at': extensiones.datetime.now()
        #    } for subdomain,waf in self.get_subdomains().items()]
        

        return {'whois': whois_dic, 'waf': waf_dict, 'name_server': name_servers_info, 'subdomains':subdomains_info}

if __name__ == '__main__':
    airan = Airan('jpardo.edu.pe', 1)
    #json_result = json.dumps(airan.get_json(), indent=4)
    subdomains_info = airan.get_subdomains()
    print(subdomains_info)
    #print(json_result)