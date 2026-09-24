from .algoritmo_de_busqueda import AlgoritmoBusqueda

class BusquedaDFS(AlgoritmoBusqueda):
    def buscar(self, tablero, inicio, objetivo, heuristica=None, funcion_costo=None):
        filas, columnas = self._obtener_dimensiones(tablero)
        pila = [inicio]
        visitados = {inicio}
        padres = {inicio: None}

        while pila:
            actual = pila.pop()
            if actual == objetivo:
                return self._reconstruir_camino(padres, actual)

            f, c = actual
            for df, dc in self.direcciones:
                nf, nc = f + df, c + dc
                vecino = (nf, nc)
                if 0 <= nf < filas and 0 <= nc < columnas:
                    if tablero[nf][nc].puede_entrar() and vecino not in visitados:
                        visitados.add(vecino)
                        padres[vecino] = actual
                        pila.append(vecino)
        return None