from algoritmo_de_busqueda import AlgoritmoBusqueda
from collections import heapq
class BusquedaAStar(AlgoritmoBusqueda):
    def buscar(self, tablero, inicio, objetivo, heuristica):
        filas, columnas = self._obtener_dimensiones(tablero)
        
        # Elementos en la cola de prioridad: (costo_f, costo_g, coordenada)
        # heapq ordena automaticamente priorizando el primer elemento de la tupla (costo_f)
        cola_prioridad = []
        heapq.heappush(cola_prioridad, (0 + heuristica(inicio, objetivo), 0, inicio))
        
        g_score = {inicio: 0}
        padres = {inicio: None}

        while cola_prioridad:
            _, g, actual = heapq.heappop(cola_prioridad)  # <--- Extrae el de menor f(n)

            if actual == objetivo:
                return self._reconstruir_camino(padres, actual)

            f, c = actual
            for df, dc in self.direcciones:
                n_f, n_c = f + df, c + dc
                vecino = (n_f, n_c)

                if 0 <= n_f < filas and 0 <= n_c < columnas:
                    if tablero[n_f][n_c].puede_entrar():
                        # En grillas uniformes, dar un paso cuesta 1
                        nuevo_g = g + 1 
                        
                        if vecino not in g_score or nuevo_g < g_score[vecino]:
                            g_score[vecino] = nuevo_g
                            f_score = nuevo_g + heuristica(vecino, objetivo)
                            padres[vecino] = actual
                            heapq.heappush(cola_prioridad, (f_score, nuevo_g, vecino))
        return None