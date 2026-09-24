CAPACIDAD_MAXIMA_CASILLA = 2  # Número de personas que caben antes de generar cuello de botella


def costo_congestion_cuadratica(casilla) -> float:
    # Función de costo por congestión (Penalización cuadrática)
    # Costo base = 1. A mayor número de ocupantes, el costo aumenta cuadráticamente como 1 + n^2, donde n es el número de individuos en la casilla.
    n = len(casilla.individuos_actuales)
    return 1.0 + (n ** 2)


class Casilla:
    def __init__(self, col: int, fila: int, tipo="camino", capacidad_maxima: int = CAPACIDAD_MAXIMA_CASILLA):
        self.col = col
        self.fila = fila
        self.tipo = tipo          # "camino", "muro", "fuego"
        self.individuos_actuales = []  # Lista de agentes parados en esta casilla
        self.capacidad_maxima = capacidad_maxima

    def puede_entrar(self) -> bool:
        return self.tipo not in ("muro", "fuego")

    def esta_congestionada(self) -> bool:
        # Indica si la casilla ya alcanzó su capacidad física máxima.
        # Permite simular el cuello de botella físico (acción 'esperar')
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
