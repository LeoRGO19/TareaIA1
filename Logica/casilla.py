CAPACIDAD_MAXIMA_CASILLA = 6 # capacidad máxima de individuos por casilla, para simular congestión y cuello de botella



def costo_congestion_cuadratica(casilla) -> float:
    # función de costo por congestión, con un costo por defecto de 1
    n = len(casilla.individuos_actuales)
    return 1.0 + (n ** 2)


class Casilla:
    def __init__(self, col: int, fila: int, tipo="camino", capacidad_maxima: int = CAPACIDAD_MAXIMA_CASILLA):
        self.col = col
        self.fila = fila
        self.tipo = tipo          # camino, fuego, muro
        self.individuos_actuales = []  # lista de agentes parados en esta casilla
        self.capacidad_maxima = capacidad_maxima

    def puede_entrar(self) -> bool:
        return self.tipo not in ("muro", "fuego")

    def esta_congestionada(self) -> bool:
        # cuello de botella si alcanza la capacidad máxima de la casilla
        return len(self.individuos_actuales) >= self.capacidad_maxima

    def obtener_costo(self, funcion_costo=costo_congestion_cuadratica) -> float:
        if self.tipo == "fuego" or self.tipo == "muro":
            return float('inf')
        return funcion_costo(self)

    def agregar_agente(self, agente):
        if agente not in self.individuos_actuales:
            self.individuos_actuales.append(agente)

    def remover_agente(self, agente):
        if agente in self.individuos_actuales:
            self.individuos_actuales.remove(agente)
