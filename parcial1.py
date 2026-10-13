from mpi4py import MPI
import time
import random


#Crea una matriz, con una probabilidad para cada celda de que sean celdas vivas
def crearMatriz(filas, columnas, vivo_porcentaje=0.2):
    matriz=[]

    for i in range(filas):
        fila = []
        for j in range(columnas):
            #Se genera un valor aleatorio entre 0 y 1
            numero_aleatorio = random.random()
            if numero_aleatorio < vivo_porcentaje:
                fila.append(1)
            else:
                fila.append(0)
        matriz.append(fila)

    return matriz

#Suma el contenido de las celdas adyacentes a una celda dada
def vecinosVivos(matriz, fila, columna):
    filas = len(matriz)
    columnas = len(matriz[0])
    contador = 0

    # range incluye el valor inicial y excluye el final, por eso se suma 2, si pusieramos fila + 1 solo contaria la fila de arriba y de en medio, pero no la de abajo
    for i in range(fila - 1, fila + 2):
        for j in range(columna - 1, columna + 2):
            if 0 <= i < filas and 0 <= j < columnas:  # verifica que no se salga de los limites de la matriz
                # si la posicion es diferente a la posicion de la celula que estamos evaluando
                if (i, j) != (fila, columna):
                    contador = contador + matriz[i][j]

    return contador

#Inicializa una matriz con solo ceros, y luego por cada celda mira si está viva y cuántos vecinos tiene
#Aplica las condiciones descritas en el juego luego
def siguienteGeneracion(matriz):
    filas = len(matriz)
    columnas = len(matriz[0])
    
    estado_siguiente = []
    
    for i in range(filas):
        fila = []
        for j in range(columnas):
            fila.append(0)
        estado_siguiente.append(fila)

    for i in range(filas):
        for j in range(columnas):
            vecinos = vecinosVivos(matriz, i, j)
            if matriz[i][j] == 1:  # si la celula esta viva
                if vecinos < 2 or vecinos > 3:
                    estado_siguiente[i][j] = 0  # muere por soledad o sobrepoblacion
                else:
                    estado_siguiente[i][j] = 1  # sigue viva
            else:  # si la celula esta muerta
                if vecinos == 3:
                    estado_siguiente[i][j] = 1  # nace
                else:
                    estado_siguiente[i][j] = 0  # sigue muerta

    return estado_siguiente

#Avanza tantas veces como generaciones haya (Llamando a la función siguienteGeneracion)
def versionSecuencial(matriz, generaciones):
    for i in range(generaciones):
        matriz = siguienteGeneracion(matriz)

    return matriz



def calcularBloque(bloque, fila_superior, fila_inferior):
    # Agregamos temporalmente las filas vecinas.
    ampliado = [fila_superior] + bloque + [fila_inferior]

    filas_locales = len(bloque)
    columnas = len(bloque[0])
    siguiente = [[0] * columnas for _ in range(filas_locales)]

    for i in range(filas_locales):
        for j in range(columnas):
            fila = i + 1
            vecinos = 0

            for fi in range(fila - 1, fila + 2):
                for co in range(max(0, j - 1), min(columnas, j + 2)):
                    if (fi, co) != (fila, j):
                        vecinos += ampliado[fi][co]

            if bloque[i][j] == 1:
                siguiente[i][j] = int(vecinos in (2, 3))
            else:
                siguiente[i][j] = int(vecinos == 3)

    return siguiente


def versionParalela(matriz_inicial, generaciones):
    comunicador = MPI.COMM_WORLD
    rango = comunicador.Get_rank()
    cantidad = comunicador.Get_size()

    # Solo el proceso 0 divide la matriz inicial.
    if rango == 0:
        total_filas = len(matriz_inicial)
        base, sobrantes = divmod(total_filas, cantidad)

        bloques = []
        inicio = 0

        for p in range(cantidad):
            numero_filas = base + (1 if p < sobrantes else 0)
            fin = inicio + numero_filas
            bloques.append(matriz_inicial[inicio:fin])
            inicio = fin
    else:
        bloques = None

    bloque = comunicador.scatter(bloques, root=0)

    if not bloque:
        raise ValueError(
            "Cada proceso debe recibir al menos una fila."
        )

    columnas = len(bloque[0])
    fila_ceros = [0] * columnas

    for _ in range(generaciones):
        anterior = rango - 1 if rango > 0 else MPI.PROC_NULL
        siguiente = rango + 1 if rango < cantidad - 1 else MPI.PROC_NULL

        # Intercambio de la fila superior.
        fila_superior = comunicador.sendrecv(
            sendobj=bloque[0],
            dest=anterior,
            sendtag=10,
            source=anterior,
            recvtag=11
        )

        # Intercambio de la fila inferior.
        fila_inferior = comunicador.sendrecv(
            sendobj=bloque[-1],
            dest=siguiente,
            sendtag=11,
            source=siguiente,
            recvtag=10
        )

        if anterior == MPI.PROC_NULL:
            fila_superior = fila_ceros

        if siguiente == MPI.PROC_NULL:
            fila_inferior = fila_ceros

        bloque = calcularBloque(
            bloque, fila_superior, fila_inferior
        )

    # Reunimos los bloques en el proceso principal.
    bloques_finales = comunicador.gather(bloque, root=0)

    if rango == 0:
        resultado = []
        for parte in bloques_finales:
            resultado.extend(parte)
        return resultado

    return None






if __name__ == "__main__":
    comunicador = MPI.COMM_WORLD
    rango = comunicador.Get_rank()
    cantidad = comunicador.Get_size()

    FILAS = 100
    COLUMNAS = 100
    GENERACIONES = 10

    if FILAS < cantidad:
        if rango == 0:
            print("Error: usa menos procesos que filas.")
    else:
        # Solo el proceso 0 crea la matriz.
        if rango == 0:
            random.seed(42)
            matriz_inicial = crearMatriz(FILAS, COLUMNAS)
        else:
            matriz_inicial = None

        # Medimos la versión paralela.
        comunicador.Barrier()
        inicio_paralelo = time.perf_counter()

        resultado_paralelo = versionParalela(
            matriz_inicial, GENERACIONES
        )

        comunicador.Barrier()
        tiempo_paralelo = time.perf_counter() - inicio_paralelo

        # Solo el proceso 0 compara e imprime.
        if rango == 0:
            inicio_secuencial = time.perf_counter()

            resultado_secuencial = versionSecuencial(
                [fila[:] for fila in matriz_inicial],
                GENERACIONES
            )

            tiempo_secuencial = (
                time.perf_counter() - inicio_secuencial
            )

            print(f"Procesos MPI: {cantidad}")
            print(f"Tablero: {FILAS} x {COLUMNAS}")
            print(f"Generaciones: {GENERACIONES}")
            print(f"Tiempo secuencial: {tiempo_secuencial:.6f} s")
            print(f"Tiempo paralelo: {tiempo_paralelo:.6f} s")

            coinciden = resultado_secuencial == resultado_paralelo
            print(f"¿Los resultados coinciden?: {coinciden}")

            if tiempo_paralelo > 0:
                aceleracion = tiempo_secuencial / tiempo_paralelo
                print(f"Speedup: {aceleracion:.3f}")

