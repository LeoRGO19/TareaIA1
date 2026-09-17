from algoritmo_de_busqueda import AlgoritmoBusqueda
from collections import deque
class BusquedaBFS(AlgoritmoBusqueda):
    def buscar(self, tablero, inicio, objetivo):
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
                n_f, n_c = f + df, c + dc
                vecino = (n_f, n_c)

                if 0 <= n_f < filas and 0 <= n_c < columnas:
                    if tablero[n_f][n_c].puede_entrar() and vecino not in visitados:
                        visitados.add(vecino)
                        padres[vecino] = actual
                        cola.append(vecino)
        return None