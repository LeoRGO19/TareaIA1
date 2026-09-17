class Casilla:
    def __init__(self, tipo="camino", capacidad_max=3):
        self.tipo = tipo          # "camino", "muro", "fuego"
        self.capacidad_max = capacidad_max
        self.individuos_actuales = 0

    def puede_entrar(self):
        if self.tipo == "muro" or self.tipo == "fuego":
            return False
        if self.individuos_actuales >= self.capacidad_max:
            return False
        return True