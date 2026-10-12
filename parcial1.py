from concurrent.futures import ThreadPoolExecutor
import threading
import time
import random
import pygame


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


def versionSecuencial(matriz, generaciones):
    for i in range(generaciones):
        matriz = siguienteGeneracion(matriz)

    return matriz


def versionParalela():

    return 0


def interfazGrafica(FILAS, COLUMNAS, matriz_inicial):
    #Inicialización de la interfaz
    pygame.init()
    pygame.font.init()

    #Configuración de la ventana
    ANCHO_VENTANA = 1280
    ALTO_VENTANA = 720
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption ("Juego de la vida - Parcial 1")
    reloj = pygame.time.Clock()

    fuente = pygame.font.SysFont(None, 24)


    # Dimensiones y posición del recuadro de la cuadrícula en la pantalla
    ANCHO_CUADRICULA = 900
    ALTO_CUADRICULA = 780
    INICIO_X = (ANCHO_VENTANA - ANCHO_CUADRICULA) // 2
    INICIO_Y = 80

    ANCHO_CELDA = ANCHO_CUADRICULA / COLUMNAS
    ALTO_CELDA = ALTO_CUADRICULA / FILAS

    # Colores
    COLOR_FONDO_VENTANA = (135, 206, 235)  # Azul claro
    COLOR_MUERTA = (20, 20, 20)           # Gris oscuro (Célula muerta)
    COLOR_VIVA = (255, 255, 255)          # Blanco (Célula viva)
    COLOR_BORDE = (0, 180, 0)             # Verde para los bordes de la cuadrícula
    COLOR_BOTON = (40, 120, 220)          # Azul botón
    COLOR_BOTON_HOVER = (60, 150, 250)    # Azul botón al pasar el mouse
    COLOR_TEXTO = (255, 255, 255)

    

    matriz_actual = matriz_inicial
    generacion_actual = 1
    ejecutando = True

    # Rectángulo para el botón "Siguiente"
    rectangulo_boton = pygame.Rect(ANCHO_VENTANA // 2 - 110, 670, 220, 45)

    while ejecutando: 
        pantalla.fill(COLOR_FONDO_VENTANA)

        #Gestionar eventos (Cerrar ventana, Clic en botón o Barra Espaciadora)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: # Clic izquierdo
                    if rectangulo_boton.collidepoint(evento.pos) and generacion_actual < GENERACIONES:
                        matriz_actual = siguienteGeneracion(matriz_actual)
                        generacion_actual += 1
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and generacion_actual < GENERACIONES:
                    matriz_actual = siguienteGeneracion(matriz_actual)
                    generacion_actual += 1

        # Dibujar el recuadro de fondo de la cuadrícula
        pygame.draw.rect(pantalla, COLOR_MUERTA, (INICIO_X, INICIO_Y, ANCHO_CUADRICULA, ALTO_CUADRICULA))

        # Dibujar células y bordes de la cuadrícula
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                x = INICIO_X + columna * ANCHO_CELDA
                y = INICIO_Y + fila * ALTO_CELDA
                rectangulo = pygame.Rect(x, y, ANCHO_CELDA, ALTO_CELDA)

                if matriz_actual[fila][columna] == 1:
                    pygame.draw.rect(pantalla, COLOR_VIVA, rectangulo)
                
                # Dibujar borde de cada celda en color verde
                pygame.draw.rect(pantalla, COLOR_BORDE, rectangulo, 1)

        # Dibujar Botón interactivo "Siguiente Generación"
        mouse_pos = pygame.mouse.get_pos()
        if rectangulo_boton.collidepoint(mouse_pos):
            color_boton_actual = COLOR_BOTON_HOVER
        else:
            color_boton_actual = COLOR_BOTON
        pygame.draw.rect(pantalla, color_boton_actual, rectangulo_boton, border_radius=8)
        
        texto_btn = fuente.render("Siguiente Generación", True, COLOR_TEXTO)
        pantalla.blit(texto_btn, (rectangulo_boton.centerx - texto_btn.get_width() // 2, rectangulo_boton.centery - texto_btn.get_height() // 2))

        # Dibujar el contador de generaciones (i/n) arriba
        texto_contador = fuente.render(f"Generación: {generacion_actual} / {GENERACIONES}", True, (20, 40, 60))
        pantalla.blit(texto_contador, (ANCHO_VENTANA // 2 - texto_contador.get_width() // 2, 30))

        pygame.display.flip()
        reloj.tick(GENERACIONES)

    pygame.quit()



if __name__ == "__main__":

    #creacion matriz
    FILAS = 500
    COLUMNAS = 500

    #Generaciones
    GENERACIONES = 10

    matriz_inicial = crearMatriz(FILAS, COLUMNAS)
    

    tiempo1S = time.perf_counter()
    resultadoSecuencial = versionSecuencial(matriz_inicial, GENERACIONES)
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
    
    print("Iniciando interfaz gráfica... Cierra la ventana de Pygame para salir.")
    interfazGrafica(100, 100, matriz_inicial)

