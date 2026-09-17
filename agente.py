class Agente:
    def __init__(self, nombre, posicion_inicial, algoritmo_busqueda):
        self.nombre = nombre
        self.posicion = posicion_inicial
        self.algoritmo = algoritmo_busqueda 
        self.camino_actual = []

    def establecer_algoritmo(self, nuevo_algoritmo):
        self.algoritmo = nuevo_algoritmo

    def calcular_ruta(self, tablero, objetivo, heuristica=None):
        self.camino_actual = self.algoritmo.buscar(tablero, self.posicion, objetivo, heuristica)
        return self.camino_actual

    def mover(self):
        if self.camino_actual:
            self.posicion = self.camino_actual.pop(0)[0]
            
