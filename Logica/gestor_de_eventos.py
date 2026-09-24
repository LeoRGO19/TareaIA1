import random
from .lector_de_mapas import LectorDeMapas
from .agente import Agente

class GestorDeEventos:
    def __init__(self, ruta_mapa: str, clase_algoritmo, es_informado=True, k_turnos_fuego: int = 3):
        self.grilla, self.objetivo, pos_agentes = LectorDeMapas.cargar_mapa(ruta_mapa)
        self.k_turnos_fuego = k_turnos_fuego
        self.turnos_totales = 0
        self.agentes = []

        for i, pos in enumerate(pos_agentes):
            ag = Agente(
                id_agente=i,
                posicion_inicial=pos,
                algoritmo_busqueda=clase_algoritmo(),
                es_informado=es_informado
            )
            self.agentes.append(ag)
            casilla = self.grilla.obtener_casilla(pos[0], pos[1])
            if casilla:
                casilla.agregar_agente(ag)

    def simulación_terminada(self) -> bool:
        return all(ag.evacuado or ag.fallecido for ag in self.agentes)

    def ejecutar_turno(self):
        if self.simulación_terminada():
            return

        # Filtra agentes que aún siguen activos en la simulación
        agentes_activos = []
        for ag in self.agentes:
            if not ag.evacuado and not ag.fallecido:
                agentes_activos.append(ag)
        
        # Mezcla el orden de turno para evitar sesgos en el movimiento
        random.shuffle(agentes_activos)

        for ag in agentes_activos:
            ag.mover(self.grilla, self.objetivo)
        # Propagación del fuego cada k turnos
        if self.turnos_totales % self.k_turnos_fuego == 0:
            self._propagar_fuego()

    def _propagar_fuego(self):
        nuevos_fuegos = []
        for f in range(self.grilla.filas):
            for c in range(self.grilla.columnas):
                if self.grilla.tablero[f][c].tipo == "fuego":
                    for nf, nc in self.grilla.obtener_vecinos((f, c)):
                        if self.grilla.tablero[nf][nc].tipo == "camino":
                            # Variación estocástica: el fuego se propaga con 75% de probabilidad
                            if random.random() < 0.75:
                                nuevos_fuegos.append((nf, nc))

        for f, c in nuevos_fuegos:
            self.grilla.cambiar_tipo(f, c, "fuego")
            casilla = self.grilla.obtener_casilla(f, c)
            for ag in list(casilla.individuos_actuales):
                ag.fallecido = True
                casilla.remover_agente(ag)

    def obtener_resultados(self):
        total = len(self.agentes)
        sobrevivientes = sum(1 for ag in self.agentes if ag.evacuado)
        tasa_supervivencia = (sobrevivientes / total) if total > 0 else 0.0
        return sobrevivientes, total, tasa_supervivencia, self.turnos_totales