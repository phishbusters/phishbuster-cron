# run_flake8.ps1

# Activar el entorno virtual
. .\phishbusters\Scripts\activate

# Ejecutar flake8 en todos los archivos .py
flake8 *.py

# Desactivar el entorno virtual
deactivate