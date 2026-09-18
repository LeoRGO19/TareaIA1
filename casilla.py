class Casilla:
    def __init__(self, tipo="camino", capacidad_max=3):
        self.tipo = tipo          # "camino", "muro", "fuego"
        self.capacidad_max = capacidad_max
        self.individuos_actuales = 0

    def puede_entrar(self):
        return self.tipo != 1 and self.tipo != 2

    def obtener_costo(self, funcion_costo):
        return funcion_costo(self)

def costo_fibonacci(casilla):
    n = casilla.individuos_actuales

    if n == 0 or n == 1:
        return 1

    anterior = 1
    actual = 1

    for _ in range(2, n + 1):
        anterior, actual = actual, anterior + actual

    return actual    
