#!/bin/bash
# run_flake8.sh

# Activar el entorno virtual
source phishbusters/bin/activate

# Ejecutar flake8 en todos los archivos .py
flake8 *.py

# Desactivar el entorno virtual
deactivate