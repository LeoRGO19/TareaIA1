from abc import ABC, abstractmethod

class AlgoritmoBusqueda(ABC):

    def __init__(self):
        self.direcciones = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]

    def _obtener_dimensiones(self, tablero):
        return len(tablero), len(tablero[0])

    def _reconstruir_camino(self, padres, actual):
        camino = []

        while actual is not None:
            camino.append(actual)
            actual = padres.get(actual)

        return camino[::-1]

    @abstractmethod

    
    def buscar(self, tablero, inicio, objetivo, heuristica=None,
               funcion_costo=None):
        pass