import random
from .lector_de_mapas import LectorDeMapas
from .agente import Agente
TOTAL_AGENTES = 80
AGENTES_MIN_POR_CASILLA = 2
AGENTES_MAX_POR_CASILLA = 6
class GestorDeEventos:
    def __init__(self, ruta_mapa: str, clase_algoritmo, es_informado=True, k_turnos_fuego: int = 3):
        self.grilla, self.objetivo, pos_agentes = LectorDeMapas.cargar_mapa(ruta_mapa)
        self.k_turnos_fuego = k_turnos_fuego
        self.turnos_totales = 0
        self.agentes = []

        distribucion = self.distribuir_agentes_exactos(
            pos_agentes=pos_agentes,
            total_agentes=TOTAL_AGENTES,
            min_c=AGENTES_MIN_POR_CASILLA,
            max_c=AGENTES_MAX_POR_CASILLA
        )

        # creación e instanciación de agentes
        id_actual = 0
        for pos, cantidad in zip(pos_agentes, distribucion):
            for _ in range(cantidad):
                ag = Agente(
                    id_agente=id_actual,
                    posicion_inicial=pos,
                    algoritmo_busqueda=clase_algoritmo(),
                    es_informado=es_informado
                )
                self.agentes.append(ag)
                
                casilla = self.grilla.obtener_casilla(pos[0], pos[1])
                if casilla:
                    casilla.agregar_agente(ag)
                
                id_actual += 1

    def distribuir_agentes_exactos(self, pos_agentes, total_agentes: int, min_c: int, max_c: int) -> list[int]:
        n_casillas = len(pos_agentes)
        
        # validar si el total solicitado es matemáticamente realizable
        if total_agentes < n_casillas * min_c or total_agentes > n_casillas * max_c:
            raise ValueError(
                f"No se pueden distribuir {total_agentes} agentes en {n_casillas} casillas "
                f"con el rango especificado [{min_c}, {max_c}]."
            )

        # asignación inicial aleatoria dentro del rango
        conteo = []
        for _ in range(n_casillas):
            numero_aleatorio = random.randint(min_c, max_c)
            conteo.append(numero_aleatorio)

        diferencia = total_agentes - sum(conteo)

        # ajuste si faltan agentes para llegar a 80
        while diferencia > 0:
            idx = random.randint(0, n_casillas - 1)
            if conteo[idx] < max_c:
                conteo[idx] += 1
                diferencia -= 1

        # ajuste si sobran agentes para llegar a 80
        while diferencia < 0:
            idx = random.randint(0, n_casillas - 1)
            if conteo[idx] > min_c:
                conteo[idx] -= 1
                diferencia += 1

        return conteo

    def simulacion_terminada(self) -> bool:
        return all(ag.evacuado or ag.fallecido for ag in self.agentes)

    def ejecutar_turno(self):
        if self.simulacion_terminada():
            return
        self.turnos_totales += 1

        # filtra agentes que aún siguen activos en la simulación
        agentes_activos = []
        for ag in self.agentes:
            if not ag.evacuado and not ag.fallecido:
                agentes_activos.append(ag)
        
        # mezcla el orden de turno para evitar sesgos en el movimiento
        random.shuffle(agentes_activos)

        for ag in agentes_activos:
            ag.mover(self.grilla, self.objetivo)
        # propagación del fuego cada k turnos
        if self.turnos_totales % self.k_turnos_fuego == 0:
            self.propagar_fuego()

    def propagar_fuego(self):
        nuevos_fuegos = []
        for f in range(self.grilla.filas):
            for c in range(self.grilla.columnas):
                if self.grilla.tablero[f][c].tipo == "fuego":
                    for nf, nc in self.grilla.obtener_vecinos((f, c)):
                        tipo_vecino = self.grilla.tablero[nf][nc].tipo
                        if tipo_vecino != "fuego" and tipo_vecino != "objetivo":
                            # variación estocástica con 75% de probabilidad
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