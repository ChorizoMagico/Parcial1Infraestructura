Usamos pygame, por lo que hay que instalar dependencias.

Por favor, ejecute estos comandos en la terminal ubicándose en la carpeta raíz del repositorio.

1. Crear entorno virtual:
python -m venv .venv

2. Activar el entorno virtual:
.venv\Scripts\Activate.ps1

3. Instalar dependencias:
pip install -r requirements.txt

4. Ejecutar el archivo:
python interfazGrafica.py

Para ejecutar el programa (sin interfaz gráfica):

1. Para Windows, primero se debe instalar Microsoft MPI (runtime y SDK) de la página oficial de Microsoft, y luego instalar la librería con:
pip install mpi4py

2. Luego, el programa se ejecuta en la consola indicando la cantidad de procesos. Por ejemplo, para 4 procesos, se ejecuta:
mpiexec -n 4 python parcial1.py

3. Para probar con distintas cantidades de procesos:
mpiexec -n 2 python parcial1.py
mpiexec -n 4 python parcial1.py
mpiexec -n 8 python parcial1.py
