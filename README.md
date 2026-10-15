Usamos pygame, por lo que hay que instalar dependencias.

Por favor, ejecute estos comandos en la terminal ubicándose en la carpeta raíz del repositorio.

1. Para Windows, primero se debe instalar Microsoft MPI (runtime y SDK) de la página oficial de Microsoft

2. Crear entorno virtual:
python -m venv .venv

3. Activar el entorno virtual:
.venv\Scripts\Activate.ps1

4. Instalar dependencias:
python -m pip install -r requirements.txt

5. Si la instalación con requirements falla, instalar las dependencias manualmente 
python -m pip install mpi4py
python -m pip install pygame-ce
python -m pip install matplotlib



Para ejecutar el programa (sin interfaz gráfica):



1. El programa se ejecuta en la consola indicando la cantidad de procesos. Por ejemplo, para 4 procesos, se ejecuta:
mpiexec -n 4 python parcial1.py

2. Para probar con distintas cantidades de procesos:
mpiexec -n 2 python parcial1.py
mpiexec -n 4 python parcial1.py
mpiexec -n 8 python parcial1.py

Para ejecutar la interfaz gráfica y el archivo de pruebas:
1. Ejecutar la interfaz gráfica:
mpiexec -n 4 python interfazGrafica.py --tam 300 --generaciones 20
Siendo n el número de procesos, tam el tamaño de la matriz y generaciones la cantidad de generaciones a recorrer (o matrices)

2. Ejecutar el benchmark:
python benchmark.py --tam 500 --procesos 4 --generaciones 20

Por ejemplo, para varias pruebas:
python benchmark.py --tam 100  --procesos 4 --generaciones 20
python benchmark.py --tam 500  --procesos 4 --generaciones 20
python benchmark.py --tam 1000 --procesos 4 --generaciones 20
python benchmark.py --tam 500  --procesos 2 --generaciones 20
python benchmark.py --tam 500  --procesos 8 --generaciones 20

python benchmark.py --graficar #Genera las tres gráficas (aceleración por número de procesos, tiempo por número de procesos
y tiempo por tamaño de la matriz)
python interfazGrafica.py


