class Agente:
    def __init__(self, nombre, posicion_inicial, algoritmo_busqueda):
        self.nombre = nombre
        self.posicion = posicion_inicial
        self.algoritmo = algoritmo_busqueda 
        self.camino_actual = []

    def establecer_algoritmo(self, nuevo_algoritmo):
        self.algoritmo = nuevo_algoritmo

    def calcular_ruta(self, tablero, objetivo, heuristica=None):
        return self.algoritmo.buscar(
            tablero,
            self.posicion,
            objetivo,
            heuristica,
            self.funcion_costo
        )

    def mover(self, tablero, objetivo, heuristica=None):
        ruta = self.calcular_ruta(tablero, objetivo, heuristica)

        if len(ruta) > 1:
            siguiente_posicion = ruta[1]

            self.posicion = siguiente_posicion
        else:
            self.esperar()
            
    def esperar(self):
        pass
