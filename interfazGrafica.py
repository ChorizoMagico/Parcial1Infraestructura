import pygame
from parcial1 import crearMatriz, siguienteGeneracion

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

# CAMBIO: la funcion recibe GENERACIONES como parametro (antes usaba la variable global del main)
def interfazGrafica(FILAS, COLUMNAS, matriz_inicial, GENERACIONES):
    #Inicialización de la interfaz
    pygame.init()
    pygame.font.init()
 
    #Configuración de la ventana
    ANCHO_VENTANA = 1280
    ALTO_VENTANA = 720
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption ("Juego de la vida - Parcial 1")
    reloj = pygame.time.Clock()
 
    # CAMBIO: varias fuentes (pygame usa la primera que encuentre instalada)
    NOMBRES_FUENTE = "segoeui,helveticaneue,arial,dejavusans"
    fuente_titulo = pygame.font.SysFont(NOMBRES_FUENTE, 34, bold=True)
    fuente_numero = pygame.font.SysFont(NOMBRES_FUENTE, 64, bold=True)
    fuente_boton = pygame.font.SysFont(NOMBRES_FUENTE, 24, bold=True)
    fuente = pygame.font.SysFont(NOMBRES_FUENTE, 22)
    fuente_pequena = pygame.font.SysFont(NOMBRES_FUENTE, 18)
 
    # CAMBIO: paleta calida / pastel con buen contraste
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
 
    # CAMBIO: nuevo diseño -> cuadricula a la izquierda y panel de control a la derecha
    MARGEN = 30
    ANCHO_PANEL = 420
    ALTO_PANEL = 620
    PAD_MARCO = 10
    HUECO = 40
 
    AREA_ANCHO = ANCHO_VENTANA - 2 * MARGEN - ANCHO_PANEL - HUECO - 2 * PAD_MARCO
    AREA_ALTO = ALTO_VENTANA - 2 * MARGEN
    # CAMBIO: celdas cuadradas y con tamaño entero (antes eran 9 x 7.8 px)
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
    rect_barra = pygame.Rect(X_INTERNO, PANEL_Y + 236, ANCHO_INTERNO, 12)
    # CAMBIO: boton "Siguiente" dentro del panel, grande y facil de encontrar + boton "Reiniciar"
    rect_siguiente = pygame.Rect(X_INTERNO, PANEL_Y + 320, ANCHO_INTERNO, 56)
    rect_reiniciar = pygame.Rect(X_INTERNO, PANEL_Y + 390, ANCHO_INTERNO, 46)
 
    matriz_actual = matriz_inicial
    # CAMBIO: empieza en 0 (el estado inicial es la generacion 0, no la 1)
    generacion_actual = 0
    celulas_vivas = 0
    hay_cambios = True   # CAMBIO: la cuadricula solo se redibuja cuando la matriz cambia
    superficie_cuadricula = pygame.Surface((ANCHO_CUADRICULA, ALTO_CUADRICULA))
    ejecutando = True
 
    while ejecutando:
        # Gestionar eventos (Cerrar ventana, Clic en botones, Espacio o R)
        # CAMBIO: los eventos solo guardan la accion y se ejecuta una sola vez abajo
        accion = None
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:  # Clic izquierdo
                if rect_siguiente.collidepoint(evento.pos):
                    accion = "siguiente"
                elif rect_reiniciar.collidepoint(evento.pos):
                    accion = "reiniciar"
            elif evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_SPACE, pygame.K_RIGHT):
                    accion = "siguiente"
                elif evento.key == pygame.K_r:
                    accion = "reiniciar"
 
        if accion == "siguiente" and generacion_actual < GENERACIONES:
            matriz_actual = siguienteGeneracion(matriz_actual)
            generacion_actual += 1
            hay_cambios = True
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
 
        # ---------------- DIBUJO ----------------
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
        dibujarTexto(pantalla, "Juego de la vida", fuente_titulo, COLOR_TEXTO, X_INTERNO, PANEL_Y + 28)
        dibujarTexto(pantalla, "Autómata celular de Conway", fuente_pequena, COLOR_TEXTO_SUAVE, X_INTERNO, PANEL_Y + 74)
        pygame.draw.line(pantalla, COLOR_PANEL_BORDE, (X_INTERNO, PANEL_Y + 108),
                         (X_INTERNO + ANCHO_INTERNO, PANEL_Y + 108), 2)
 
        # Contador de generaciones grande + barra de progreso
        dibujarTexto(pantalla, "GENERACIÓN", fuente_pequena, COLOR_TEXTO_SUAVE, X_INTERNO, PANEL_Y + 128)
        dibujarTexto(pantalla, f"{generacion_actual} / {GENERACIONES}", fuente_numero, COLOR_TEXTO, X_INTERNO, PANEL_Y + 152)
        pygame.draw.rect(pantalla, COLOR_LINEA, rect_barra, border_radius=6)
        ancho_relleno = int(ANCHO_INTERNO * generacion_actual / GENERACIONES)
        if ancho_relleno > 0:
            pygame.draw.rect(pantalla, COLOR_VIVA, (rect_barra.x, rect_barra.y, ancho_relleno, rect_barra.height), border_radius=6)
        dibujarTexto(pantalla, f"Células vivas: {celulas_vivas:,}", fuente, COLOR_TEXTO, X_INTERNO, PANEL_Y + 262)
 
        # Botones (el de siguiente se desactiva al llegar a la ultima generacion)
        mouse_pos = pygame.mouse.get_pos()
        if generacion_actual >= GENERACIONES:
            dibujarBoton(pantalla, rect_siguiente, "Simulación completa", fuente_boton, COLOR_BOTON_OFF, COLOR_BOTON_OFF_TEXTO)
        else:
            if rect_siguiente.collidepoint(mouse_pos):
                color_boton = COLOR_BOTON_HOVER
            else:
                color_boton = COLOR_BOTON
            dibujarBoton(pantalla, rect_siguiente, "Siguiente generación", fuente_boton, color_boton, COLOR_BOTON_TEXTO)
 
        if rect_reiniciar.collidepoint(mouse_pos):
            color_reiniciar = COLOR_BOTON_SEC_HOVER
        else:
            color_reiniciar = COLOR_BOTON_SEC
        dibujarBoton(pantalla, rect_reiniciar, "Reiniciar", fuente_boton, color_reiniciar, COLOR_BOTON_SEC_TEXTO)
 
        # Leyenda de colores
        y_leyenda = PANEL_Y + 470
        pygame.draw.rect(pantalla, COLOR_VIVA, (X_INTERNO, y_leyenda, 20, 20), border_radius=4)
        dibujarTexto(pantalla, "Célula viva", fuente_pequena, COLOR_TEXTO, X_INTERNO + 30, y_leyenda + 1)
        pygame.draw.rect(pantalla, COLOR_MUERTA, (X_INTERNO + 180, y_leyenda, 20, 20), border_radius=4)
        pygame.draw.rect(pantalla, COLOR_PANEL_BORDE, (X_INTERNO + 180, y_leyenda, 20, 20), 2, border_radius=4)
        dibujarTexto(pantalla, "Célula muerta", fuente_pequena, COLOR_TEXTO, X_INTERNO + 210, y_leyenda + 1)
 
        # Ayuda de teclado
        dibujarTexto(pantalla, "Espacio: siguiente   |   R: reiniciar", fuente_pequena, COLOR_TEXTO_SUAVE,
                     PANEL_X + ANCHO_PANEL // 2, PANEL_Y + 575, centrado=True)
 
        pygame.display.flip()
        reloj.tick(30)   # CAMBIO: antes era reloj.tick(GENERACIONES), que limitaba la ventana a 10 FPS
 
    pygame.quit()

if __name__ == "__main__":

    #creacion matriz
    FILAS = 100
    COLUMNAS = 100

    #Generaciones
    GENERACIONES = 10
    
    matriz_inicial = crearMatriz(FILAS, COLUMNAS)


    print("Iniciando interfaz gráfica... Cierra la ventana de Pygame para salir.")
 
    interfazGrafica(FILAS, COLUMNAS, matriz_inicial, GENERACIONES)