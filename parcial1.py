from concurrent.futures import ThreadPoolExecutor
import threading
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


def versionParalela():

    return 0






if __name__ == "__main__":

    #creacion matriz
    FILAS = 500
    COLUMNAS = 500

    matriz_inicial = crearMatriz(FILAS, COLUMNAS)
    

    tiempo1S = time.perf_counter()
    resultadoSecuencial = versionSecuencial(matriz_inicial, 10)
    tiempo2S = time.perf_counter()

    tiempoSecuencial = tiempo2S - tiempo1S


    #tiempo1P = time.perf_counter()
    #resultadoParalelo = versionParalela()
    #tiempo2P = time.perf_counter()

    #tiempoParalelo = tiempo2P - tiempo1P

    #aceleracion = tiempoSecuencial / tiempoParalelo

    print(f"Tiempo secuencial: {tiempoSecuencial:.3f} segundos")
    #print(f"Tiempo paralelo: {tiempoParalelo:.3f} segundos")
    #print(f"Aceleracion: {aceleracion:.3f}")

    #if resultadoSecuencial == resultadoParalelo:
        #print("Las dos versiones dan el mismo resultado")
    #else:
        #print("Las versiones no coinciden")
    
    

