from .casilla import Casilla

class Grid:
    def __init__(self, filas: int, columnas: int):
        self.filas = filas
        self.columnas = columnas
        self.tablero = []
        for f in range(filas):
            fila_casillas = []
            for c in range(columnas):
                fila_casillas.append(Casilla(f, c))
            self.tablero.append(fila_casillas)

    def obtener_casilla(self, fila: int, columna: int) -> Casilla:
        if 0 <= fila < self.filas and 0 <= columna < self.columnas:
            return self.tablero[fila][columna]
        return None

    def cambiar_tipo(self, fila: int, columna: int, nuevo_tipo: str):
        casilla = self.obtener_casilla(fila, columna)
        if casilla:
            casilla.tipo = nuevo_tipo

    def obtener_vecinos(self, pos):
        # devuelve las coordenadas ortogonales válidas adyacentes a pos
        f, c = pos
        vecinos = []
        for df, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nf, nc = f + df, c + dc
            if 0 <= nf < self.filas and 0 <= nc < self.columnas:
                vecinos.append((nf, nc))
        return vecinos