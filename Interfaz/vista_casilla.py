import pygame

class VistaCasilla:
    COLORES = {
        "camino": (240, 240, 240),
        "muro": (50, 50, 50),
        "fuego": (220, 50, 30)
    }

    @staticmethod
    def dibujar(superficie, casilla, x, y, tam):
        color = VistaCasilla.COLORES.get(casilla.tipo, (255, 255, 255))
        rect = pygame.Rect(x, y, tam, tam)
        pygame.draw.rect(superficie, color, rect)
        pygame.draw.rect(superficie, (180, 180, 180), rect, 1) # Bordes marcados