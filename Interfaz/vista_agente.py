import pygame
import math

class VistaAgente:
    @staticmethod
    def dibujar(superficie, agente, x, y, tam):
        centro_x = x + tam // 2
        centro_y = y + tam // 2
        
        # Radio proporcional al tamaño de la casilla (aproximadamente un tercio)
        radio = max(3, tam // 3)

        # Si prefieres dibujarlos como CÍRCULOS limpios:
        pygame.draw.circle(superficie, agente.color, (centro_x, centro_y), radio)
        
        # Opcional: Si los quieres como FLECHAS orientadas:
        """
        dx, dy = 0, -1
        if agente.posicion_anterior:
            df = agente.posicion[0] - agente.posicion_anterior[0]
            dc = agente.posicion[1] - agente.posicion_anterior[1]
            if (df, dc) != (0, 0):
                dx, dy = dc, df

        angulo = math.atan2(dy, dx)
        p1 = (centro_x + radio * math.cos(angulo), centro_y + radio * math.sin(angulo))
        p2 = (centro_x + radio * math.cos(angulo + 2.5), centro_y + radio * math.sin(angulo + 2.5))
        p3 = (centro_x + radio * math.cos(angulo - 2.5), centro_y + radio * math.sin(angulo - 2.5))

        pygame.draw.polygon(superficie, agente.color, [p1, p2, p3])
        """