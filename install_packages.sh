#!/bin/bash

# Ruta al archivo que contiene la lista de paquetes
archivo="requerimientos.txt"

# Verifica si el archivo existe
if [ ! -f "$archivo" ]; then
    echo "  [X] El archivo no existe."
    exit 1
fi

# Lee cada línea del archivo y verifica el estado del paquete
while IFS= read -r paquete; do
    echo "  [?] Verificando $paquete..."

    # Verifica si el paquete existe en los repositorios
    if apt-cache show "$paquete" >/dev/null 2>&1; then
        # Verifica si el paquete ya está instalado
        if dpkg -l | grep -q "^ii  $paquete"; then
            echo "      [✓] El paquete $paquete ya está instalado."
        else
            echo "      Instalando $paquete..."
            sudo apt install -y "$paquete"
        fi
    else
        echo "      [X] El paquete $paquete no existe en los repositorios."
    fi
done < "$archivo"
