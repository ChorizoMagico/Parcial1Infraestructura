import os
# Evita que cada proceso MPI imprima el saludo de pygame
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import argparse
import pygame
from mpi4py import MPI
from parcial1 import (crearMatriz, siguienteGeneracion, medirSecuencial,
                      medirParalela, esperarOrdenes)

# Uso:
#   python interfaz.py                      -> 1 proceso (el modo paralelo usa 1 solo proceso)
#   mpiexec -n 4 python interfaz.py         -> el modo paralelo usa 4 procesos
#   mpiexec -n 4 python interfaz.py --tam 300 --generaciones 20


# Funciones auxiliares para dibujar texto y botones sin repetir codigo
def dibujarTexto(pantalla, texto, fuente, color, x, y, centrado=False):
    superficie = fuente.render(texto, True, color)
    if centrado:
        x = x - superficie.get_width() // 2
    pantalla.blit(superficie, (x, y))


def dibujarBoton(pantalla, rectangulo, texto, fuente, color_fondo, color_texto):
    pygame.draw.rect(pantalla, color_fondo, rectangulo, border_radius=12)
    superficie = fuente.render(texto, True, color_texto)
    pantalla.blit(superficie, (rectangulo.centerx - superficie.get_width() // 2,
                               rectangulo.centery - superficie.get_height() // 2))


# Muestra el tiempo en ms si es menor a un segundo, y en s si es mayor
def formatearTiempo(segundos):
    if segundos < 1:
        return f"{segundos * 1000:.1f} ms"
    return f"{segundos:.2f} s"


# Solo la ejecuta el proceso 0 (los demas procesos estan en esperarOrdenes)
def interfazGrafica(FILAS, COLUMNAS, matriz_inicial, GENERACIONES):
    comunicador = MPI.COMM_WORLD
    PROCESOS = comunicador.Get_size()

    #Inicialización de la interfaz
    pygame.init()
    pygame.font.init()

    #Configuración de la ventana
    ANCHO_VENTANA = 1280
    ALTO_VENTANA = 720
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Juego de la vida - Parcial 1")
    reloj = pygame.time.Clock()

    # Fuentes (pygame usa la primera que encuentre instalada)
    NOMBRES_FUENTE = "segoeui,helveticaneue,arial,dejavusans"
    fuente_titulo = pygame.font.SysFont(NOMBRES_FUENTE, 34, bold=True)
    fuente_numero = pygame.font.SysFont(NOMBRES_FUENTE, 52, bold=True)
    fuente_boton = pygame.font.SysFont(NOMBRES_FUENTE, 24, bold=True)
    fuente_modo = pygame.font.SysFont(NOMBRES_FUENTE, 22, bold=True)
    fuente = pygame.font.SysFont(NOMBRES_FUENTE, 22)
    fuente_resultado = pygame.font.SysFont(NOMBRES_FUENTE, 20)
    fuente_pequena = pygame.font.SysFont(NOMBRES_FUENTE, 18)

    # Paleta calida / pastel con buen contraste
    COLOR_FONDO_VENTANA = (250, 238, 222)   # Durazno muy claro
    COLOR_SOMBRA = (233, 214, 192)          # Sombra suave de marco y panel
    COLOR_MARCO = (205, 170, 140)           # Marco alrededor de la cuadricula
    COLOR_MUERTA = (255, 251, 245)          # Celula muerta: crema casi blanco
    COLOR_VIVA = (217, 98, 80)              # Celula viva: coral
    COLOR_LINEA = (240, 226, 208)           # Lineas de la cuadricula
    COLOR_PANEL = (255, 252, 247)
    COLOR_PANEL_BORDE = (225, 205, 180)
    COLOR_TEXTO = (78, 52, 46)              # Marron oscuro (alto contraste)
    COLOR_TEXTO_SUAVE = (125, 96, 82)
    COLOR_BOTON = (196, 90, 56)
    COLOR_BOTON_HOVER = (214, 108, 72)
    COLOR_BOTON_TEXTO = (255, 255, 255)
    COLOR_BOTON_OFF = (228, 214, 200)
    COLOR_BOTON_OFF_TEXTO = (140, 118, 102)
    COLOR_BOTON_SEC = (243, 220, 197)
    COLOR_BOTON_SEC_HOVER = (235, 202, 173)
    COLOR_BOTON_SEC_TEXTO = (110, 70, 50)
    COLOR_MEDIR = (166, 108, 30)            # Mostaza oscuro para "Ejecutar todo y medir"
    COLOR_MEDIR_HOVER = (188, 128, 46)
    COLOR_RESULTADOS_FONDO = (250, 241, 228)
    COLOR_OK = (74, 122, 62)
    COLOR_ERROR = (178, 50, 50)

    # Distribucion: cuadricula a la izquierda y panel de control a la derecha
    MARGEN = 30
    ANCHO_PANEL = 420
    ALTO_PANEL = 660
    PAD_MARCO = 10
    HUECO = 40

    AREA_ANCHO = ANCHO_VENTANA - 2 * MARGEN - ANCHO_PANEL - HUECO - 2 * PAD_MARCO
    AREA_ALTO = ALTO_VENTANA - 2 * MARGEN
    # Celdas cuadradas y con tamaño entero
    TAM_CELDA = max(1, min(AREA_ANCHO // COLUMNAS, AREA_ALTO // FILAS))
    SEPARACION = 1 if TAM_CELDA >= 4 else 0   # grosor de las lineas entre celdas
    ANCHO_CUADRICULA = TAM_CELDA * COLUMNAS
    ALTO_CUADRICULA = TAM_CELDA * FILAS

    ANCHO_TOTAL = ANCHO_CUADRICULA + 2 * PAD_MARCO + HUECO + ANCHO_PANEL
    X_MARCO = (ANCHO_VENTANA - ANCHO_TOTAL) // 2
    INICIO_X = X_MARCO + PAD_MARCO
    INICIO_Y = (ALTO_VENTANA - ALTO_CUADRICULA) // 2
    PANEL_X = X_MARCO + ANCHO_CUADRICULA + 2 * PAD_MARCO + HUECO
    PANEL_Y = (ALTO_VENTANA - ALTO_PANEL) // 2
    X_INTERNO = PANEL_X + 30
    ANCHO_INTERNO = ANCHO_PANEL - 60

    rect_marco = pygame.Rect(X_MARCO, INICIO_Y - PAD_MARCO,
                             ANCHO_CUADRICULA + 2 * PAD_MARCO, ALTO_CUADRICULA + 2 * PAD_MARCO)
    rect_panel = pygame.Rect(PANEL_X, PANEL_Y, ANCHO_PANEL, ALTO_PANEL)
    rect_modo_sec = pygame.Rect(X_INTERNO, PANEL_Y + 122, 176, 40)
    rect_modo_par = pygame.Rect(X_INTERNO + 184, PANEL_Y + 122, 176, 40)
    rect_barra = pygame.Rect(X_INTERNO, PANEL_Y + 260, ANCHO_INTERNO, 10)
    rect_siguiente = pygame.Rect(X_INTERNO, PANEL_Y + 318, ANCHO_INTERNO, 48)
    rect_medir = pygame.Rect(X_INTERNO, PANEL_Y + 374, ANCHO_INTERNO, 48)
    rect_reiniciar = pygame.Rect(X_INTERNO, PANEL_Y + 430, ANCHO_INTERNO, 40)
    rect_resultados = pygame.Rect(X_INTERNO, PANEL_Y + 484, ANCHO_INTERNO, 106)

    # Estado de la interfaz
    modo = "secuencial"          # "secuencial" o "paralelo": que version usa el boton "Siguiente"
    matriz_actual = matriz_inicial
    generacion_actual = 0        # el estado inicial es la generacion 0
    celulas_vivas = 0
    hay_cambios = True           # la cuadricula solo se redibuja cuando la matriz cambia
    calculando = False           # True mientras se ejecuta "Ejecutar todo y medir"
    medicion = None              # diccionario con la ultima medicion
    superficie_cuadricula = pygame.Surface((ANCHO_CUADRICULA, ALTO_CUADRICULA))
    ejecutando = True

    # Dibuja toda la pantalla. Es una funcion interna para poder llamarla tambien antes de un
    # calculo largo (y mostrar "Calculando..." mientras la ventana no puede responder).
    def dibujarPantalla():
        mouse_pos = pygame.mouse.get_pos()
        pantalla.fill(COLOR_FONDO_VENTANA)

        # Cuadricula con marco y sombra
        pygame.draw.rect(pantalla, COLOR_SOMBRA, rect_marco.move(5, 6), border_radius=16)
        pygame.draw.rect(pantalla, COLOR_MARCO, rect_marco, border_radius=16)
        pantalla.blit(superficie_cuadricula, (INICIO_X, INICIO_Y))

        # Panel de control con sombra
        pygame.draw.rect(pantalla, COLOR_SOMBRA, rect_panel.move(5, 6), border_radius=16)
        pygame.draw.rect(pantalla, COLOR_PANEL, rect_panel, border_radius=16)
        pygame.draw.rect(pantalla, COLOR_PANEL_BORDE, rect_panel, 2, border_radius=16)

        # Titulo
        dibujarTexto(pantalla, "Juego de la vida", fuente_titulo, COLOR_TEXTO, X_INTERNO, PANEL_Y + 20)
        dibujarTexto(pantalla, f"Tablero {FILAS} x {COLUMNAS}  ·  {GENERACIONES} generaciones",
                     fuente_pequena, COLOR_TEXTO_SUAVE, X_INTERNO, PANEL_Y + 62)
        pygame.draw.line(pantalla, COLOR_PANEL_BORDE, (X_INTERNO, PANEL_Y + 88),
                         (X_INTERNO + ANCHO_INTERNO, PANEL_Y + 88), 2)

        # Selector de modo
        dibujarTexto(pantalla, f"MODO  ·  {PROCESOS} proceso(s) MPI", fuente_pequena,
                     COLOR_TEXTO_SUAVE, X_INTERNO, PANEL_Y + 100)
        for rect, nombre, texto in ((rect_modo_sec, "secuencial", "Secuencial"),
                                    (rect_modo_par, "paralelo", "Paralelo")):
            if modo == nombre:
                dibujarBoton(pantalla, rect, texto, fuente_modo, COLOR_BOTON, COLOR_BOTON_TEXTO)
            elif rect.collidepoint(mouse_pos):
                dibujarBoton(pantalla, rect, texto, fuente_modo, COLOR_BOTON_SEC_HOVER, COLOR_BOTON_SEC_TEXTO)
            else:
                dibujarBoton(pantalla, rect, texto, fuente_modo, COLOR_BOTON_SEC, COLOR_BOTON_SEC_TEXTO)

        # Contador de generaciones grande + barra de progreso
        dibujarTexto(pantalla, "GENERACIÓN", fuente_pequena, COLOR_TEXTO_SUAVE, X_INTERNO, PANEL_Y + 176)
        dibujarTexto(pantalla, f"{generacion_actual} / {GENERACIONES}", fuente_numero, COLOR_TEXTO,
                     X_INTERNO, PANEL_Y + 194)
        pygame.draw.rect(pantalla, COLOR_LINEA, rect_barra, border_radius=5)
        ancho_relleno = int(ANCHO_INTERNO * generacion_actual / GENERACIONES)
        if ancho_relleno > 0:
            pygame.draw.rect(pantalla, COLOR_VIVA, (rect_barra.x, rect_barra.y, ancho_relleno, rect_barra.height),
                             border_radius=5)
        dibujarTexto(pantalla, f"Células vivas: {celulas_vivas:,}", fuente, COLOR_TEXTO, X_INTERNO, PANEL_Y + 278)

        # Boton "Siguiente" (se desactiva al llegar a la ultima generacion)
        if generacion_actual >= GENERACIONES:
            dibujarBoton(pantalla, rect_siguiente, "Simulación completa", fuente_boton, COLOR_BOTON_OFF, COLOR_BOTON_OFF_TEXTO)
        else:
            if rect_siguiente.collidepoint(mouse_pos):
                color_boton = COLOR_BOTON_HOVER
            else:
                color_boton = COLOR_BOTON
            dibujarBoton(pantalla, rect_siguiente, "Siguiente generación", fuente_boton, color_boton, COLOR_BOTON_TEXTO)

        # Boton "Ejecutar todo y medir"
        if rect_medir.collidepoint(mouse_pos):
            color_medir = COLOR_MEDIR_HOVER
        else:
            color_medir = COLOR_MEDIR
        dibujarBoton(pantalla, rect_medir, "Ejecutar todo y medir", fuente_boton, color_medir, COLOR_BOTON_TEXTO)

        # Boton "Reiniciar"
        if rect_reiniciar.collidepoint(mouse_pos):
            color_reiniciar = COLOR_BOTON_SEC_HOVER
        else:
            color_reiniciar = COLOR_BOTON_SEC
        dibujarBoton(pantalla, rect_reiniciar, "Reiniciar", fuente_boton, color_reiniciar, COLOR_BOTON_SEC_TEXTO)

        # Recuadro con el resultado de la ultima medicion
        pygame.draw.rect(pantalla, COLOR_RESULTADOS_FONDO, rect_resultados, border_radius=10)
        pygame.draw.rect(pantalla, COLOR_PANEL_BORDE, rect_resultados, 2, border_radius=10)
        x = rect_resultados.x + 14
        y = rect_resultados.y + 6
        dibujarTexto(pantalla, "ÚLTIMA MEDICIÓN", fuente_pequena, COLOR_TEXTO_SUAVE, x, y)

        if calculando:
            dibujarTexto(pantalla, "Calculando...", fuente_resultado, COLOR_TEXTO, x, y + 26)
            dibujarTexto(pantalla, "La ventana no responde hasta terminar.", fuente_pequena, COLOR_TEXTO_SUAVE, x, y + 52)
        elif medicion is None:
            dibujarTexto(pantalla, "Compara las dos versiones con las", fuente_resultado, COLOR_TEXTO, x, y + 26)
            dibujarTexto(pantalla, f"{GENERACIONES} generaciones desde el inicio.", fuente_resultado, COLOR_TEXTO, x, y + 50)
        else:
            t_sec = medicion["secuencial"]
            t_par = medicion["paralelo"]
            speedup = t_sec / t_par if t_par > 0 else 0
            dibujarTexto(pantalla, f"Secuencial: {formatearTiempo(t_sec)}", fuente_resultado, COLOR_TEXTO, x, y + 26)
            dibujarTexto(pantalla, f"Paralelo ({medicion['procesos']} proc): {formatearTiempo(t_par)}",
                         fuente_resultado, COLOR_TEXTO, x, y + 50)
            dibujarTexto(pantalla, f"Speedup: {speedup:.2f}x", fuente_resultado, COLOR_TEXTO, x, y + 74)
            if medicion["coinciden"]:
                dibujarTexto(pantalla, "Resultados iguales", fuente_pequena, COLOR_OK, x + 170, y + 76)
            else:
                dibujarTexto(pantalla, "Resultados DISTINTOS", fuente_pequena, COLOR_ERROR, x + 170, y + 76)

        # Ayuda de teclado
        dibujarTexto(pantalla, "Espacio: siguiente    Enter: medir todo", fuente_pequena,
                     COLOR_TEXTO_SUAVE, PANEL_X + ANCHO_PANEL // 2, PANEL_Y + 604, centrado=True)
        dibujarTexto(pantalla, "R: reiniciar    M: cambiar de modo", fuente_pequena,
                     COLOR_TEXTO_SUAVE, PANEL_X + ANCHO_PANEL // 2, PANEL_Y + 626, centrado=True)

        pygame.display.flip()

    try:
        while ejecutando:
            # Gestionar eventos: los eventos solo guardan la accion y se ejecuta una sola vez abajo
            accion = None
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:  # Clic izquierdo
                    if rect_siguiente.collidepoint(evento.pos):
                        accion = "siguiente"
                    elif rect_medir.collidepoint(evento.pos):
                        accion = "medir"
                    elif rect_reiniciar.collidepoint(evento.pos):
                        accion = "reiniciar"
                    elif rect_modo_sec.collidepoint(evento.pos):
                        accion = "modo_secuencial"
                    elif rect_modo_par.collidepoint(evento.pos):
                        accion = "modo_paralelo"
                elif evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_SPACE, pygame.K_RIGHT):
                        accion = "siguiente"
                    elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        accion = "medir"
                    elif evento.key == pygame.K_r:
                        accion = "reiniciar"
                    elif evento.key == pygame.K_m:
                        accion = "modo_alternar"

            if accion == "modo_secuencial":
                modo = "secuencial"
            elif accion == "modo_paralelo":
                modo = "paralelo"
            elif accion == "modo_alternar":
                if modo == "secuencial":
                    modo = "paralelo"
                else:
                    modo = "secuencial"

            elif accion == "siguiente" and generacion_actual < GENERACIONES:
                if modo == "secuencial":
                    matriz_actual = siguienteGeneracion(matriz_actual)
                else:
                    # Avisamos a los demas procesos y calculamos UNA generacion en paralelo
                    comunicador.bcast(("paralela", 1), root=0)
                    matriz_actual, _ = medirParalela(matriz_actual, 1)
                generacion_actual += 1
                hay_cambios = True

            elif accion == "medir":
                # Mostramos "Calculando..." antes de bloquear la ventana con el calculo
                calculando = True
                dibujarPantalla()

                resultado_seq, tiempo_seq = medirSecuencial(matriz_inicial, GENERACIONES)

                comunicador.bcast(("paralela", GENERACIONES), root=0)
                resultado_par, tiempo_par = medirParalela(matriz_inicial, GENERACIONES)

                medicion = {
                    "secuencial": tiempo_seq,
                    "paralelo": tiempo_par,
                    "procesos": PROCESOS,
                    "coinciden": resultado_seq == resultado_par,
                }
                matriz_actual = resultado_par
                generacion_actual = GENERACIONES
                hay_cambios = True
                calculando = False

            elif accion == "reiniciar":
                matriz_actual = matriz_inicial   # siguienteGeneracion no modifica la matriz original
                generacion_actual = 0
                hay_cambios = True

            # Redibujar la cuadricula en su propia superficie (solo cuando hubo cambios)
            if hay_cambios:
                superficie_cuadricula.fill(COLOR_LINEA)
                for fila in range(FILAS):
                    for columna in range(COLUMNAS):
                        if matriz_actual[fila][columna] == 1:
                            color = COLOR_VIVA
                        else:
                            color = COLOR_MUERTA
                        rectangulo = pygame.Rect(columna * TAM_CELDA, fila * TAM_CELDA,
                                                 TAM_CELDA - SEPARACION, TAM_CELDA - SEPARACION)
                        pygame.draw.rect(superficie_cuadricula, color, rectangulo)
                celulas_vivas = sum(sum(fila) for fila in matriz_actual)
                hay_cambios = False

            dibujarPantalla()
            reloj.tick(30)

    finally:
        # Avisamos a los demas procesos que terminen (aunque la interfaz falle por algun error)
        comunicador.bcast(("salir", 0), root=0)
        pygame.quit()


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description="Interfaz del Juego de la Vida (secuencial y paralelo con MPI)")
    analizador.add_argument("--tam", type=int, default=200, help="lado del tablero (por defecto 200)")
    analizador.add_argument("--generaciones", type=int, default=10, help="numero de generaciones (por defecto 10)")
    argumentos = analizador.parse_args()

    comunicador = MPI.COMM_WORLD
    rango = comunicador.Get_rank()
    cantidad = comunicador.Get_size()

    FILAS = argumentos.tam
    COLUMNAS = argumentos.tam
    GENERACIONES = argumentos.generaciones

    # Todos los procesos llegan a la misma conclusion, asi que nadie se queda esperando
    if FILAS < cantidad:
        if rango == 0:
            print("Error: usa menos procesos que filas.")

    elif rango == 0:
        # El proceso 0 crea el tablero y maneja la ventana
        matriz_inicial = crearMatriz(FILAS, COLUMNAS)
        print("Iniciando interfaz gráfica... Cierra la ventana de Pygame para salir.")
        interfazGrafica(FILAS, COLUMNAS, matriz_inicial, GENERACIONES)

    else:
        # Los demas procesos esperan las ordenes del proceso 0
        esperarOrdenes()