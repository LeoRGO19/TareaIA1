import pygame

from Interfaz.vista_grilla import VistaGrilla
from Logica.a_estrella import BusquedaEstrella
from Logica.algoritmo_genetico import AlgoritmoGenetico
from Logica.bfs import BusquedaBFS
from Logica.dfs import BusquedaDFS
from Logica.gestor_de_eventos import GestorDeEventos
from Logica.ida import AlgoritmoBusquedaIDAEstrella
from Logica.lector_de_mapas import LectorDeMapas


MAPAS = (
    "mapa_cuello_botella50x50.txt",
    "mapa_corporativo50x50.txt",
    "mapa_abierto50x50.txt",
)
ALGORITMOS = [
    (BusquedaBFS, False, "BFS"),
    (BusquedaDFS, False, "DFS"),
    (BusquedaEstrella, True, "A*"),
    (AlgoritmoBusquedaIDAEstrella, True, "IDA*"),
    (AlgoritmoGenetico, True, "Genetico"),
]
ITERACIONES_DISPONIBLES = (1, 5, 10, 25, 50, 100)
K_TURNOS_DISPONIBLES = (1, 2, 3, 4, 5, 10)


def obtener_maximo_agentes(mapa_archivo):
    _, _, posiciones_agentes = LectorDeMapas.cargar_mapa(mapa_archivo)
    return len(posiciones_agentes)


def crear_gestor(mapa_archivo, algoritmo, es_informado, numero_agentes, k_turnos_fuego):
    return GestorDeEventos(
        mapa_archivo,
        algoritmo,
        es_informado=es_informado,
        k_turnos_fuego=k_turnos_fuego,
        numero_agentes=numero_agentes,
    )


def dibujar_boton(superficie, fuente, rect, texto, activo=False):
    color = (40, 110, 150) if activo else (55, 65, 75)
    pygame.draw.rect(superficie, color, rect, border_radius=6)
    pygame.draw.rect(superficie, (150, 165, 175), rect, 1, border_radius=6)
    texto_renderizado = fuente.render(texto, True, (245, 245, 245))
    superficie.blit(texto_renderizado, texto_renderizado.get_rect(center=rect.center))


def elegir_configuracion():
    pygame.init()
    pantalla = pygame.display.set_mode((760, 600))
    pygame.display.set_caption("Configuracion de evacuacion")
    fuente_titulo = pygame.font.SysFont("Arial", 28, bold=True)
    fuente = pygame.font.SysFont("Arial", 20)
    fuente_pequena = pygame.font.SysFont("Arial", 16)
    reloj = pygame.time.Clock()

    mapa_idx = 0
    algoritmo_idx = 4
    iteraciones_idx = 0
    k_turnos_idx = 4
    max_agentes = obtener_maximo_agentes(MAPAS[mapa_idx])
    numero_agentes = min(80, max_agentes)

    boton_mapa = pygame.Rect(300, 105, 300, 42)
    boton_algoritmo = pygame.Rect(300, 165, 300, 42)
    boton_agentes_menos = pygame.Rect(300, 225, 42, 42)
    boton_agentes_mas = pygame.Rect(558, 225, 42, 42)
    boton_iteraciones_menos = pygame.Rect(300, 295, 42, 42)
    boton_iteraciones_mas = pygame.Rect(558, 295, 42, 42)
    boton_k_turnos = pygame.Rect(300, 365, 300, 42)
    boton_iniciar = pygame.Rect(280, 450, 200, 52)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (
                evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                return None

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_a:
                    algoritmo_idx = (algoritmo_idx + 1) % len(ALGORITMOS)
                elif evento.key == pygame.K_m:
                    mapa_idx = (mapa_idx + 1) % len(MAPAS)
                    max_agentes = obtener_maximo_agentes(MAPAS[mapa_idx])
                    numero_agentes = min(numero_agentes, max_agentes)
                elif evento.key == pygame.K_k:
                    k_turnos_idx = (k_turnos_idx + 1) % len(K_TURNOS_DISPONIBLES)
                elif evento.key == pygame.K_LEFT:
                    iteraciones_idx = max(0, iteraciones_idx - 1)
                elif evento.key == pygame.K_RIGHT:
                    iteraciones_idx = min(len(ITERACIONES_DISPONIBLES) - 1, iteraciones_idx + 1)
                elif evento.key == pygame.K_DOWN:
                    numero_agentes = max(1, numero_agentes - 1)
                elif evento.key == pygame.K_UP:
                    numero_agentes = min(max_agentes, numero_agentes + 1)
                elif evento.key == pygame.K_RETURN:
                    algoritmo, es_informado, nombre = ALGORITMOS[algoritmo_idx]
                    return (
                        MAPAS[mapa_idx], algoritmo, es_informado, nombre,
                        numero_agentes, ITERACIONES_DISPONIBLES[iteraciones_idx],
                        K_TURNOS_DISPONIBLES[k_turnos_idx]
                    )

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                posicion = evento.pos
                if boton_mapa.collidepoint(posicion):
                    mapa_idx = (mapa_idx + 1) % len(MAPAS)
                    max_agentes = obtener_maximo_agentes(MAPAS[mapa_idx])
                    numero_agentes = min(numero_agentes, max_agentes)
                elif boton_algoritmo.collidepoint(posicion):
                    algoritmo_idx = (algoritmo_idx + 1) % len(ALGORITMOS)
                elif boton_agentes_menos.collidepoint(posicion):
                    numero_agentes = max(1, numero_agentes - 1)
                elif boton_agentes_mas.collidepoint(posicion):
                    numero_agentes = min(max_agentes, numero_agentes + 1)
                elif boton_iteraciones_menos.collidepoint(posicion):
                    iteraciones_idx = max(0, iteraciones_idx - 1)
                elif boton_iteraciones_mas.collidepoint(posicion):
                    iteraciones_idx = min(len(ITERACIONES_DISPONIBLES) - 1, iteraciones_idx + 1)
                elif boton_k_turnos.collidepoint(posicion):
                    k_turnos_idx = (k_turnos_idx + 1) % len(K_TURNOS_DISPONIBLES)
                elif boton_iniciar.collidepoint(posicion):
                    algoritmo, es_informado, nombre = ALGORITMOS[algoritmo_idx]
                    return (
                        MAPAS[mapa_idx], algoritmo, es_informado, nombre,
                        numero_agentes, ITERACIONES_DISPONIBLES[iteraciones_idx],
                        K_TURNOS_DISPONIBLES[k_turnos_idx]
                    )

        pantalla.fill((22, 28, 34))
        pantalla.blit(fuente_titulo.render("Escape de la torre", True, (240, 245, 248)), (48, 42))
        pantalla.blit(fuente_pequena.render("Selecciona la configuracion de la simulacion", True, (170, 185, 195)), (50, 78))

        for texto, y in (("Mapa", 115), ("Algoritmo", 175), ("Agentes", 235), ("Iteraciones", 305), ("Fuego cada K turnos", 375)):
            pantalla.blit(fuente.render(texto, True, (220, 225, 230)), (80, y))

        dibujar_boton(pantalla, fuente, boton_mapa, MAPAS[mapa_idx].replace(".txt", ""), True)
        dibujar_boton(pantalla, fuente, boton_algoritmo, ALGORITMOS[algoritmo_idx][2], True)
        dibujar_boton(pantalla, fuente, boton_agentes_menos, "-", False)
        dibujar_boton(pantalla, fuente, boton_agentes_mas, "+", False)
        dibujar_boton(pantalla, fuente, boton_iteraciones_menos, "-", False)
        dibujar_boton(pantalla, fuente, boton_iteraciones_mas, "+", False)

        valor_agentes = fuente.render(f"{numero_agentes} / {max_agentes}", True, (245, 245, 245))
        pantalla.blit(valor_agentes, valor_agentes.get_rect(center=(471, 246)))
        valor_iteraciones = fuente.render(str(ITERACIONES_DISPONIBLES[iteraciones_idx]), True, (245, 245, 245))
        pantalla.blit(valor_iteraciones, valor_iteraciones.get_rect(center=(471, 316)))
        dibujar_boton(pantalla, fuente, boton_k_turnos, str(K_TURNOS_DISPONIBLES[k_turnos_idx]), True)
        dibujar_boton(pantalla, fuente, boton_iniciar, "Iniciar", True)
        ayuda = "M: mapa | A: algoritmo | K: fuego | Flechas: valores | Enter: iniciar | Esc: salir"
        pantalla.blit(fuente_pequena.render(ayuda, True, (170, 185, 195)), (55, 545))
        pygame.display.flip()
        reloj.tick(30)


def ejecutar_simulacion_visual(
    mapa_archivo,
    algoritmo_clase,
    es_informado,
    nombre_algoritmo,
    numero_agentes,
    numero_iteraciones,
    k_turnos_fuego,
):
    gestor = crear_gestor(mapa_archivo, algoritmo_clase, es_informado, numero_agentes, k_turnos_fuego)
    tam_casilla = 15
    ancho_mapa = gestor.grilla.columnas * tam_casilla
    alto_mapa = gestor.grilla.filas * tam_casilla
    panel_alto = 72
    pantalla = pygame.display.set_mode((ancho_mapa, alto_mapa + panel_alto))
    pygame.display.set_caption(f"Evacuacion - {nombre_algoritmo} | {mapa_archivo}")
    vista = VistaGrilla(tam_casilla)
    reloj = pygame.time.Clock()
    fuente_panel = pygame.font.SysFont("Arial", 15)
    iteraciones_completadas = 0
    resultado_registrado = False
    siguiente_iteracion_en = 0
    ejecutando = True

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    ejecutando = False
                elif evento.key == pygame.K_r:
                    gestor = crear_gestor(mapa_archivo, algoritmo_clase, es_informado, numero_agentes, k_turnos_fuego)
                    resultado_registrado = False
                    if iteraciones_completadas >= numero_iteraciones:
                        iteraciones_completadas = 0
                elif evento.key == pygame.K_SPACE and gestor.simulacion_terminada():
                    gestor = crear_gestor(mapa_archivo, algoritmo_clase, es_informado, numero_agentes, k_turnos_fuego)
                    resultado_registrado = False

        if not gestor.simulacion_terminada():
            gestor.ejecutar_turno()
        elif not resultado_registrado:
            iteraciones_completadas += 1
            resultado_registrado = True
            siguiente_iteracion_en = pygame.time.get_ticks() + 700
        elif iteraciones_completadas < numero_iteraciones and pygame.time.get_ticks() >= siguiente_iteracion_en:
            gestor = crear_gestor(mapa_archivo, algoritmo_clase, es_informado, numero_agentes, k_turnos_fuego)
            resultado_registrado = False

        pantalla.fill((255, 255, 255))
        vista.dibujar(pantalla, gestor)
        pygame.draw.rect(pantalla, (30, 30, 30), (0, alto_mapa, ancho_mapa, panel_alto))
        sobrevivientes, total, tasa, turnos = gestor.obtener_resultados()
        fallecidos = sum(agente.fallecido for agente in gestor.agentes)
        estado = "Finalizada" if gestor.simulacion_terminada() else "En curso"
        iteracion_visible = min(
            iteraciones_completadas + (0 if resultado_registrado else 1),
            numero_iteraciones
        )
        texto = f"Iteracion {iteracion_visible}/{numero_iteraciones} | {estado} | Turno: {turnos}"
        texto2 = f"Agentes: {total} | Sobrevivientes: {sobrevivientes} | Bajas: {fallecidos} | Fuego: cada {k_turnos_fuego} | R: reiniciar | Esc: salir"
        pantalla.blit(fuente_panel.render(texto, True, (255, 255, 255)), (8, alto_mapa + 8))
        pantalla.blit(fuente_panel.render(texto2, True, (255, 255, 255)), (8, alto_mapa + 32))
        pygame.display.flip()
        reloj.tick(8)

    pygame.quit()


if __name__ == "__main__":
    configuracion = elegir_configuracion()
    if configuracion is not None:
        ejecutar_simulacion_visual(*configuracion)
