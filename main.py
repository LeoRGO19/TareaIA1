import pygame
import sys
from Logica.gestor_de_eventos import GestorDeEventos
from Interfaz.vista_grilla import VistaGrilla

# Importar algoritmos
from Logica.bfs import BusquedaBFS
from Logica.dfs import BusquedaDFS
from Logica.a_estrella import BusquedaEstrella
from Logica.ida import AlgoritmoBusquedaIDAEstrella
from Logica.algoritmo_genetico import AlgoritmoGenetico

def ejecutar_simulacion_visual(mapa_archivo, algoritmo_clase, es_informado, nombre_algoritmo):
    pygame.init()
    
    # Crear el gestor para el mapa y algoritmo seleccionados
    gestor = GestorDeEventos(mapa_archivo, algoritmo_clase, es_informado=es_informado, k_turnos_fuego=5)

    tam_casilla = 15
    ancho_mapa = gestor.grilla.columnas * tam_casilla
    alto_mapa = gestor.grilla.filas * tam_casilla
    panel_alto = 50

    pantalla = pygame.display.set_mode((ancho_mapa, alto_mapa + panel_alto))
    pygame.display.set_caption(f"Evacuación - {nombre_algoritmo} | {mapa_archivo}")

    vista = VistaGrilla(tam_casilla)
    reloj = pygame.time.Clock()
    fuente_panel = pygame.font.SysFont("Arial", 16)

    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

        # Avanzar 1 turno global
        if not gestor.simulacion_terminada():
            gestor.ejecutar_turno()

        # Dibujar escenario
        pantalla.fill((255, 255, 255))
        vista.dibujar(pantalla, gestor)

        # Dibujar Panel Superior con Métricas en Vivo
        pygame.draw.rect(pantalla, (30, 30, 30), (0, alto_mapa, ancho_mapa, panel_alto))
        
        sobrevivientes, total, tasa, turnos = gestor.obtener_resultados()
        fallecidos = sum(1 for a in gestor.agentes if a.fallecido)
        
        texto_status = f"Turno: {turnos} | Sobrevivientes: {sobrevivientes}/{total} ({tasa*100:.1f}%) | bajas: {fallecidos}"
        txt_surface = fuente_panel.render(texto_status, True, (255, 255, 255))
        pantalla.blit(txt_surface, (15, alto_mapa + 15))

        pygame.display.flip()
        
        # Ajusta la velocidad aquí (4 FPS te permite observar bien los movimientos)
        reloj.tick(4)

    pygame.quit()

if __name__ == "__main__":
    # Algoritmos: BusquedaEstrella, BusquedaBFS, BusquedaDFS, AlgoritmoBusquedaIDAEstrella, AlgoritmoGenetico
    
    ejecutar_simulacion_visual(
        mapa_archivo="mapa_cuello_botella50x50.txt",
        algoritmo_clase=BusquedaBFS,
        es_informado=True,
        nombre_algoritmo="BFS"
    )