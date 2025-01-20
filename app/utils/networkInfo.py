import requests
import json

class NetworkInfo():
    def __init__(self):
        self._ip_publica = None
        self.ip_privada = None

    @property
    def ip_publica(self):
        if not self._ip_publica:
            self._ip_publica = self.obtener_ip_publica()
        return self._ip_publica

    def obtener_ip_publica(self):
        try:
            response = requests.get("https://httpbin.org/ip")
            response.raise_for_status()  # Lanza una excepción si hay un error en la respuesta HTTP
            ip_info = response.json()
            return ip_info['origin']
        except requests.exceptions.RequestException as e:
            print(f"No se pudo obtener la IP pública: {e}")
        except json.JSONDecodeError as e:
            print(f"No se pudo decodificar el JSON de la respuesta: {e}")
        return None

# Uso de la clase optimizada
network_info = NetworkInfo()
