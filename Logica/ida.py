from .algoritmo_de_busqueda import AlgoritmoBusqueda

class AlgoritmoBusquedaIDAEstrella(AlgoritmoBusqueda):
    def buscar(self, tablero, inicio, objetivo, heuristica=None, funcion_costo=None):
        if heuristica is None:
            heuristica = lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1])

        limite = heuristica(inicio, objetivo)
        camino = [inicio]

        while True:
            t, res = self._buscar_rec(tablero, camino, 0, limite, objetivo, heuristica, funcion_costo)
            if res is not None:
                return res
            if t == float('inf'):
                return None
            limite = t

    def _buscar_rec(self, tablero, camino, g, limite, objetivo, heuristica, funcion_costo):
        actual = camino[-1]
        f = g + heuristica(actual, objetivo)

        if f > limite:
            return f, None
        if actual == objetivo:
            return f, list(camino)

        minimo = float('inf')
        filas, columnas = self._obtener_dimensiones(tablero)
        f_act, c_act = actual

        for df, dc in self.direcciones:
            nf, nc = f_act + df, c_act + dc
            vecino = (nf, nc)

            if 0 <= nf < filas and 0 <= nc < columnas:
                casilla = tablero[nf][nc]
                if casilla.puede_entrar() and vecino not in camino:
                    costo_paso = casilla.obtener_costo(funcion_costo) if funcion_costo else 1.0
                    camino.append(vecino)
                    t, res = self._buscar_rec(tablero, camino, g + costo_paso, limite, objetivo, heuristica, funcion_costo)
                    if res is not None:
                        return t, res
                    if t < minimo:
                        minimo = t
                    camino.pop()
        return minimo, None