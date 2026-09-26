from pathlib import Path
from .grilla import Grid


class LectorDeMapas:
    CARPETA_ASSETS = Path(__file__).resolve().parent.parent / "assets"

    @staticmethod
    def cargar_mapa(ruta_archivo: str):
        ruta = Path(ruta_archivo)
        if not ruta.is_absolute() and not ruta.exists():
            ruta = LectorDeMapas.CARPETA_ASSETS / ruta_archivo

        with open(ruta, 'r') as f:
            lineas = [linea.strip() for linea in f if linea.strip()]

        filas = len(lineas)
        columnas = len(lineas[0].split())
        grilla = Grid(filas, columnas)

        posicion_salida = None
        posiciones_agentes = []

        for f_idx, linea in enumerate(lineas):
            valores = linea.split()
            for c, val in enumerate(valores):
                if val == '1':
                    grilla.cambiar_tipo(f_idx, c, "muro")
                elif val == 'S':
                    grilla.cambiar_tipo(f_idx, c, "camino")
                    posicion_salida = (f_idx, c)
                elif val == 'A':
                    grilla.cambiar_tipo(f_idx, c, "camino")
                    posiciones_agentes.append((f_idx, c))
                else:
                    grilla.cambiar_tipo(f_idx, c, "camino")

        return grilla, posicion_salida, posiciones_agentes
