from abc import ABC, abstractmethod
# clase base para los algoritmos de búsqueda. 
# proporciona métodos auxiliares para obtener dimensiones del tablero y reconstruir el camino desde el nodo objetivo hasta el nodo inicial
class AlgoritmoBusqueda(ABC):
    def __init__(self):
        self.direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)] #desplazamientos

    def _obtener_dimensiones(self, tablero):
        return len(tablero), len(tablero[0])

    def _reconstruir_camino(self, padres, actual):
        camino = []
        while actual is not None:
            camino.append(actual)
            actual = padres.get(actual)
        return camino[::-1]

    @abstractmethod
    def buscar(self, tablero, inicio, objetivo, heuristica=None, funcion_costo=None):
        # método a implementar por las clases hijas
        pass
