import pygame
import math

class VistaAgente:
    @staticmethod
    def dibujar(superficie, agente, x, y, tam):
        centro_x = x + tam // 2
        centro_y = y + tam // 2
        
        # Radio proporcional al tamaño de la casilla (aproximadamente un tercio)
        radio = max(3, tam // 3)

        pygame.draw.circle(superficie, agente.color, (centro_x, centro_y), radio)
        
