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

#Inicializa una matriz con solo ceros, y luego por cada celda mira si esta viva y cuántos vecinos tiene
#luego aplica las condiciones descritas en el juego
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

#Avanza tantas veces como generaciones haya (Llamando a la funcion siguienteGeneracion)
def versionSecuencial(matriz, generaciones):
    for i in range(generaciones):
        matriz = siguienteGeneracion(matriz)

    return matriz


# Calcula la siguiente generacion de las filas asignadas a un proceso
def calcularBloque(bloque, fila_superior, fila_inferior):
    # Agregamos las filas vecinas al bloque
    ampliado = []

    ampliado.append(fila_superior)
    for fila in bloque:
        ampliado.append(fila)
    ampliado.append(fila_inferior)

    filas_locales = len(bloque)
    columnas = len(bloque[0])

    # Creamos una matriz vacia para guardar la siguiente generacion
    siguiente = []

    for i in range(filas_locales):
        fila_vacia = []

        for j in range(columnas):
            fila_vacia.append(0)

        siguiente.append(fila_vacia)

    # Recorremos cada celda del bloque
    for i in range(filas_locales):
        for j in range(columnas):

            # La fila real esta desplazada una posicion
            # porque agregamos una fila superior al bloque
            fila_actual = i + 1

            vecinos = 0

            # Revisamos las filas cercanas
            for fi in range(fila_actual - 1, fila_actual + 2):

                # Revisamos las columnas cercanas
                for co in range(j - 1, j + 2):

                    # Ignoramos las columnas que estan fuera del tablero
                    if co < 0 or co >= columnas:
                        continue

                    # No contamos la celda que estamos evaluando
                    if fi == fila_actual and co == j:
                        continue

                    # Sumamos el estado de la celda vecina
                    vecinos += ampliado[fi][co]

            # Aplicamos las reglas del Juego de la Vida
            if bloque[i][j] == 1:

                # Una célula viva muere si tiene menos de 2
                # o más de 3 vecinos vivos
                if vecinos < 2 or vecinos > 3:
                    siguiente[i][j] = 0
                else:
                    siguiente[i][j] = 1

            else:

                # Una celula muerta revive si tiene exactamente
                # 3 vecinos vivos
                if vecinos == 3:
                    siguiente[i][j] = 1
                else:
                    siguiente[i][j] = 0

    return siguiente


# Divide la matriz, calcula generaciones y reúne el resultado
def versionParalela(matriz_inicial, generaciones):
    comunicador = MPI.COMM_WORLD
    rango = comunicador.Get_rank()
    cantidad = comunicador.Get_size()

    # Solo el proceso 0 divide la matriz inicial
    if rango == 0:
        total_filas = len(matriz_inicial)

        # Calculamos cuántas filas recibe cada proceso
        base = total_filas // cantidad
        sobrantes = total_filas % cantidad

        bloques = []
        inicio = 0

        for p in range(cantidad):
            numero_filas = base

            # Repartimos las filas sobrantes entre los primeros procesos
            if p < sobrantes:
                numero_filas = numero_filas + 1

            fin = inicio + numero_filas

            # Guardamos las filas que le corresponden al proceso
            bloques.append(matriz_inicial[inicio:fin])

            inicio = fin

    else:
        bloques = None

    # Cada proceso recibe su bloque de filas
    bloque = comunicador.scatter(bloques, root=0)

    if not bloque:
        raise ValueError("Cada proceso debe recibir al menos una fila.")

    columnas = len(bloque[0])

    # Fila de ceros para los bordes del tablero
    fila_ceros = []
    for i in range(columnas):
        fila_ceros.append(0)

    # Calculamos cada generación
    for i in range(generaciones):

        # Identificamos el proceso anterior
        if rango > 0:
            anterior = rango - 1
        else:
            anterior = MPI.PROC_NULL

        # Identificamos el proceso siguiente
        if rango < cantidad - 1:
            siguiente = rango + 1
        else:
            siguiente = MPI.PROC_NULL

        # Enviamos nuestra primera fila al proceso anterior
        # y recibimos la fila superior que necesitamos
        fila_superior = comunicador.sendrecv(
            sendobj=bloque[0],
            dest=anterior,
            sendtag=10,
            source=anterior,
            recvtag=11
        )

        # Enviamos nuestra ultima fila al proceso siguiente
        # y recibimos la fila inferior que necesitamos
        fila_inferior = comunicador.sendrecv(
            sendobj=bloque[-1],
            dest=siguiente,
            sendtag=11,
            source=siguiente,
            recvtag=10
        )

        # Si no existe un proceso anterior, usamos una fila de ceros
        if anterior == MPI.PROC_NULL:
            fila_superior = fila_ceros

        # Si no existe un proceso siguiente, usamos una fila de ceros
        if siguiente == MPI.PROC_NULL:
            fila_inferior = fila_ceros

        # Calculamos la siguiente generación de nuestro bloque
        bloque = calcularBloque(bloque, fila_superior, fila_inferior)

    # Reunimos los bloques calculados en el proceso 0
    bloques_finales = comunicador.gather(bloque, root=0)

    if rango == 0:
        resultado = []

        for parte in bloques_finales:
            for fila in parte:
                resultado.append(fila)

        return resultado

    # Los demás procesos no reconstruyen la matriz completa
    return None


if __name__ == "__main__":
    comunicador = MPI.COMM_WORLD
    rango = comunicador.Get_rank()
    cantidad = comunicador.Get_size()

    FILAS = 100
    COLUMNAS = 100
    GENERACIONES = 10

    # Verificamos que cada proceso pueda recibir al menos una fila
    if FILAS < cantidad:

        if rango == 0:
            print("Error: usa menos procesos que filas.")

    else:

        # Solo el proceso 0 crea el tablero inicial
        if rango == 0:
            random.seed(42)
            matriz_inicial = crearMatriz(FILAS, COLUMNAS)
        else:
            matriz_inicial = None

        # Medimos el tiempo de la versión paralela
        comunicador.Barrier()
        inicio_paralelo = time.perf_counter()

        resultado_paralelo = versionParalela(matriz_inicial, GENERACIONES)

        comunicador.Barrier()
        final_paralelo = time.perf_counter()
        tiempo_paralelo = final_paralelo - inicio_paralelo

        # Solo el proceso 0 calcula la versión secuencial y compara
        if rango == 0:
            inicio_secuencial = time.perf_counter()

            resultado_secuencial = versionSecuencial(matriz_inicial, GENERACIONES)

            final_secuencial = time.perf_counter()
            tiempo_secuencial = final_secuencial - inicio_secuencial

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
