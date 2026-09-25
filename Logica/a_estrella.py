from .algoritmo_de_busqueda import AlgoritmoBusqueda
import heapq

class BusquedaEstrella(AlgoritmoBusqueda):
    def buscar(self, tablero, inicio, objetivo, heuristica=None, funcion_costo=None):
        if heuristica is None:
            heuristica = lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1])

        filas, columnas = self._obtener_dimensiones(tablero)
        pq = []
        # Elementos en la cola de prioridad = (f_score, g_score, nodo_actual)
        heapq.heappush(pq, (0 + heuristica(inicio, objetivo), 0, inicio))
        
        g_score = {inicio: 0}
        padres = {inicio: None}

        while pq:
            _, g, actual = heapq.heappop(pq)
            if actual == objetivo:
                return self._reconstruir_camino(padres, actual)

            f, c = actual
            for df, dc in self.direcciones:
                nf, nc = f + df, c + dc
                vecino = (nf, nc)

                if 0 <= nf < filas and 0 <= nc < columnas:
                    casilla = tablero[nf][nc]
                    if casilla.puede_entrar():
                        # Considera el costo de congestión de la casilla
                        costo_paso = casilla.obtener_costo(funcion_costo) if funcion_costo else 1.0
                        nuevo_g = g + costo_paso

                        if vecino not in g_score or nuevo_g < g_score[vecino]:
                            g_score[vecino] = nuevo_g
                            f_score = nuevo_g + heuristica(vecino, objetivo)
                            padres[vecino] = actual
                            heapq.heappush(pq, (f_score, nuevo_g, vecino))
        return None