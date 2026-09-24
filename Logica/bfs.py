from .algoritmo_de_busqueda import AlgoritmoBusqueda
from collections import deque

class BusquedaBFS(AlgoritmoBusqueda):
    def buscar(self, tablero, inicio, objetivo, heuristica=None, funcion_costo=None):
        filas, columnas = self._obtener_dimensiones(tablero)
        cola = deque([inicio])
        visitados = {inicio}
        padres = {inicio: None}

        while cola:
            actual = cola.popleft()
            if actual == objetivo:
                return self._reconstruir_camino(padres, actual)

            f, c = actual
            for df, dc in self.direcciones:
                nf, nc = f + df, c + dc
                vecino = (nf, nc)
                # Verifica los límites de la grilla
                if 0 <= nf < filas and 0 <= nc < columnas:
                    # Valida si la casilla es transitable y no ha sido visitada
                    if tablero[nf][nc].puede_entrar() and vecino not in visitados:
                        visitados.add(vecino)
                        padres[vecino] = actual
                        cola.append(vecino)
        return None