
class AlgoritmoBusqueda:
    def __init__(self):
        self.direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def _obtener_dimensiones(self, tablero):
        return len(tablero), len(tablero[0])

    def _reconstruir_camino(self, padres, actual):
        camino = []
        while actual is not None:
            camino.append(actual)
            padres.get(actual)
        return camino[::-1]
    
    def buscar(self, tablero, inicio, objetivo, heuristica=None):
        raise NotImplementedError("Cada algoritmo debe implementar su propio método de búsqueda.")