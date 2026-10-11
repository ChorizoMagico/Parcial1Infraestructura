from concurrent.futures import ThreadPoolExecutor
import threading
import time
import random


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



def versionSecuencial():

    return 0


def versionParalela():

    return 0


def interfazGrafica():


    return 0



if __name__ == "__main__":

    #creacion matriz
    FILAS = 500
    COLUMNAS = 500

    matriz_inicial = crearMatriz(FILAS, COLUMNAS)

    tiempo1S = time.perf_counter()
    versionSecuencial()
    tiempo2S = time.perf_counter()

    tiempoSecuencial = tiempo2S - tiempo1S


    tiempo1P = time.perf_counter()
    versionParalela()
    tiempo2P = time.perf_counter()

    tiempoParalelo = tiempo2P - tiempo1P