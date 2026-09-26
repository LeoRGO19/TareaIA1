from .algoritmo_de_busqueda import AlgoritmoBusqueda

class AlgoritmoBusquedaIDAEstrella(AlgoritmoBusqueda):
    MAX_NODOS_POR_BUSQUEDA = 500

    def buscar(self, tablero, inicio, objetivo, heuristica=None, funcion_costo=None):
        self.nodos_explorados = 0
        self.limite_nodos_alcanzado = False
        self.llamadas_busqueda = getattr(self, "llamadas_busqueda", 0) + 1
        if not hasattr(self, "limites_nodos_acumulados"):
            self.limites_nodos_acumulados = 0
        if heuristica is None:
            heuristica = lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1])

        limite = heuristica(inicio, objetivo)
        camino = [inicio]
        nodos_explorados = [0]

        while True:
            mejores_costos = {}
            t, res = self._buscar_rec(
                tablero,
                camino,
                0,
                limite,
                objetivo,
                heuristica,
                funcion_costo,
                mejores_costos,
                nodos_explorados
            )
            if res is not None:
                return res
            if t == float('inf'):
                return None
            limite = t

    def _buscar_rec(
        self,
        tablero,
        camino,
        g,
        limite,
        objetivo,
        heuristica,
        funcion_costo,
        mejores_costos,
        nodos_explorados
    ):
        if nodos_explorados[0] >= self.MAX_NODOS_POR_BUSQUEDA:
            if not self.limite_nodos_alcanzado:
                self.limite_nodos_alcanzado = True
                self.limites_nodos_acumulados += 1
            return float('inf'), None
        nodos_explorados[0] += 1
        self.nodos_explorados = nodos_explorados[0]

        actual = camino[-1]
        f = g + heuristica(actual, objetivo)

        if f > limite:
            return f, None
        if actual == objetivo:
            return f, list(camino)

        mejor_g_conocido = mejores_costos.get(actual)
        if mejor_g_conocido is not None and mejor_g_conocido <= g:
            return float('inf'), None
        mejores_costos[actual] = g

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
                    t, res = self._buscar_rec(
                        tablero,
                        camino,
                        g + costo_paso,
                        limite,
                        objetivo,
                        heuristica,
                        funcion_costo,
                        mejores_costos,
                        nodos_explorados
                    )
                    if res is not None:
                        return t, res
                    if t < minimo:
                        minimo = t
                    camino.pop()
        return minimo, None
