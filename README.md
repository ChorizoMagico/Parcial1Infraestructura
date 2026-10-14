Usamos pygame, por lo que hay que instalar dependencias.

Por favor, ejecute estos comandos en la terminal ubicándose en la carpeta raíz del repositorio.



1. Crear entorno virtual:
python -m venv .venv

2. Activar el entorno virtual:
.venv\Scripts\Activate.ps1

3. Instalar dependencias:
python -m pip install -r requirements.txt

4. Ejecutar el archivo:
mpiexec -n 4 python interfazGrafica.py --tam 300 --generaciones 20
Siendo n el número de procesos, tam el tamaño de la matriz y generaciones la cantidad de generaciones a recorrer (o matrices)

O para ejecutar el benchmark:
python benchmark.py --tam 500 --procesos 4 --generaciones 20

Por ejemplo, para varias pruebas:
python benchmark.py --tam 100  --procesos 4 --generaciones 20
python benchmark.py --tam 500  --procesos 4 --generaciones 20
python benchmark.py --tam 1000 --procesos 4 --generaciones 20
python benchmark.py --tam 500  --procesos 2 --generaciones 20
python benchmark.py --tam 500  --procesos 8 --generaciones 20

python benchmark.py --graficar #Genera las tres gráficas (aceleración por número de procesos, tiempo por número de procesos
y tiempo por tamaño de la matriz)