import pygame
from .vista_casilla import VistaCasilla
from .vista_agente import VistaAgente

class VistaGrilla:
    def __init__(self, tam_casilla=35):
        self.tam_casilla = tam_casilla
        self.fuente = None

    def _inicializar_fuente(self):
        if self.fuente is None:
            # Tamaño de letra proporcional al tamaño de la casilla
            tam_letra = max(11, int(self.tam_casilla // 2.2))
            self.fuente = pygame.font.SysFont("Arial", tam_letra, bold=True)

    def dibujar(self, superficie, gestor):
        self._inicializar_fuente()
        grilla = gestor.grilla

        # PASO 1: Dibujar el terreno base (camino, muro, fuego)
        for f in range(grilla.filas):
            for c in range(grilla.columnas):
                casilla = grilla.tablero[f][c]
                x = c * self.tam_casilla
                y = f * self.tam_casilla
                VistaCasilla.dibujar(superficie, casilla, x, y, self.tam_casilla)

        # PASO 2: Resaltar la Salida de Evacuación (S)
        if gestor.objetivo:
            obj_f, obj_c = gestor.objetivo
            rect_obj = pygame.Rect(
                obj_c * self.tam_casilla, 
                obj_f * self.tam_casilla, 
                self.tam_casilla, 
                self.tam_casilla
            )
            pygame.draw.rect(superficie, (0, 220, 0), rect_obj, max(2, self.tam_casilla // 10))

        # PASO 3: Dibujar Agentes activos
        for agente in gestor.agentes:
            if not agente.evacuado and not agente.fallecido:
                f, c = agente.posicion
                x = c * self.tam_casilla
                y = f * self.tam_casilla
                VistaAgente.dibujar(superficie, agente, x, y, self.tam_casilla)

        # PASO 4: Dibujar LOS TEXTOS DE CONGESTIÓN AL FINAL (encima de todo)
        for f in range(grilla.filas):
            for c in range(grilla.columnas):
                casilla = grilla.tablero[f][c]
                cant_personas = len(casilla.individuos_actuales)

                # Solo dibuja el indicador si hay 2 o más personas en la misma casilla
                if cant_personas > 1:
                    x = c * self.tam_casilla
                    y = f * self.tam_casilla

                    # Texto en color rojo brillante
                    txt = self.fuente.render(f"x{cant_personas}", True, (255, 0, 0))
                    
                    # Dibujar una pequeña sombra negra detrás del texto para que contraste con cualquier fondo
                    sombra = self.fuente.render(f"x{cant_personas}", True, (0, 0, 0))
                    superficie.blit(sombra, (x + 3, y + 3))
                    superficie.blit(txt, (x + 2, y + 2))