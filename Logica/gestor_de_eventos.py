import random
from .lector_de_mapas import LectorDeMapas
from .agente import Agente
RADIO_PROTECCION_AGENTES = 1
FILAS_PROTEGIDAS_AL_FINAL = 8
PROBABILIDAD_PROPAGACION_FUEGO = 0.75
PROBABILIDAD_ATRAVESAR_PARED = 0.25


class GestorDeEventos:
    def __init__(self, ruta_mapa: str, clase_algoritmo, es_informado=True, k_turnos_fuego: int = 3, numero_agentes: int | None = None, probabilidad_fuego: float = PROBABILIDAD_PROPAGACION_FUEGO, probabilidad_atravesar_pared: float = PROBABILIDAD_ATRAVESAR_PARED):
        if k_turnos_fuego < 1:
            raise ValueError("k_turnos_fuego debe ser al menos 1")
        if not 0.0 <= probabilidad_fuego <= 1.0:
            raise ValueError("probabilidad_fuego debe estar entre 0 y 1")
        if not 0.0 <= probabilidad_atravesar_pared <= 1.0:
            raise ValueError("probabilidad_atravesar_pared debe estar entre 0 y 1")
        self.grilla, self.objetivo, pos_agentes = LectorDeMapas.cargar_mapa(ruta_mapa)
        if numero_agentes is not None:
            if numero_agentes < 1 or numero_agentes > len(pos_agentes):
                raise ValueError(
                    f"El mapa contiene {len(pos_agentes)} posiciones A; "
                    f"numero_agentes debe estar entre 1 y ese valor."
                )
            pos_agentes = pos_agentes[:numero_agentes]
        self.k_turnos_fuego = k_turnos_fuego
        self.probabilidad_fuego = probabilidad_fuego
        self.probabilidad_atravesar_pared = probabilidad_atravesar_pared
        self.turnos_totales = 0
        self.agentes = []

        for i, pos in enumerate(pos_agentes):
            algoritmo = clase_algoritmo()
            ag = Agente(
                id_agente=i,
                posicion_inicial=pos,
                algoritmo_busqueda=algoritmo,
                es_informado=es_informado,
                usar_memoria_respaldo=getattr(algoritmo, "usa_memoria_respaldo", False),
            )
            self.agentes.append(ag)
            casilla = self.grilla.obtener_casilla(pos[0], pos[1])
            if casilla:
                casilla.agregar_agente(ag)

        self.inicializar_fuego()

    def es_celda_valida_para_fuego(self, posicion: tuple[int, int]) -> bool:
        fila, columna = posicion
        casilla = self.grilla.obtener_casilla(fila, columna)
        return bool(
            casilla
            and casilla.tipo not in ("fuego", "muro")
            and posicion != self.objetivo
        )

    def obtener_posiciones_protegidas_fuego_inicial(self) -> set[tuple[int, int]]:
        posiciones_protegidas = set()

        for agente in self.agentes:
            fila_agente, columna_agente = agente.posicion
            for desplazamiento_fila in range(-RADIO_PROTECCION_AGENTES, RADIO_PROTECCION_AGENTES + 1):
                for desplazamiento_columna in range(-RADIO_PROTECCION_AGENTES, RADIO_PROTECCION_AGENTES + 1):
                    posicion = (
                        fila_agente + desplazamiento_fila,
                        columna_agente + desplazamiento_columna
                    )
                    if self.grilla.obtener_casilla(*posicion):
                        posiciones_protegidas.add(posicion)

        primera_fila_protegida = max(0, self.grilla.filas - FILAS_PROTEGIDAS_AL_FINAL)
        for fila in range(primera_fila_protegida, self.grilla.filas):
            for columna in range(self.grilla.columnas):
                posiciones_protegidas.add((fila, columna))

        return posiciones_protegidas

    def inicializar_fuego(self):
        posiciones_protegidas = self.obtener_posiciones_protegidas_fuego_inicial()
        posiciones_disponibles = [
            (fila, columna)
            for fila in range(self.grilla.filas)
            for columna in range(self.grilla.columnas)
            if (fila, columna) not in posiciones_protegidas
            and self.es_celda_valida_para_fuego((fila, columna))
        ]

        if posiciones_disponibles:
            posicion_fuego = random.choice(posiciones_disponibles)
            self.grilla.cambiar_tipo(*posicion_fuego, "fuego")

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
            if ag.evacuado and ag.turno_evacuacion is None:
                ag.turno_evacuacion = self.turnos_totales
        # propagación del fuego cada k turnos
        if self.turnos_totales % self.k_turnos_fuego == 0:
            self.propagar_fuego()

    def propagar_fuego(self):
        nuevos_fuegos = set()
        direcciones = ((-1, 0), (1, 0), (0, -1), (0, 1))
        for f in range(self.grilla.filas):
            for c in range(self.grilla.columnas):
                if self.grilla.tablero[f][c].tipo == "fuego":
                    for df, dc in direcciones:
                        nf, nc = f + df, c + dc
                        grosor_pared = 0
                        while 0 <= nf < self.grilla.filas and 0 <= nc < self.grilla.columnas:
                            casilla = self.grilla.obtener_casilla(nf, nc)
                            if casilla.tipo == "muro":
                                grosor_pared += 1
                                nf += df
                                nc += dc
                                continue
                            destino = (nf, nc)
                            if not self.es_celda_valida_para_fuego(destino):
                                break
                            probabilidad = self.probabilidad_fuego
                            if grosor_pared:
                                probabilidad = self.probabilidad_atravesar_pared ** grosor_pared
                            if random.random() < probabilidad:
                                nuevos_fuegos.add(destino)
                            break

        for f, c in nuevos_fuegos:
            self.grilla.cambiar_tipo(f, c, "fuego")
            casilla = self.grilla.obtener_casilla(f, c)
            if casilla:
                for ag in list(casilla.individuos_actuales):
                    ag.fallecido = True
                    casilla.remover_agente(ag)

    def obtener_resultados(self):
        total = len(self.agentes)
        sobrevivientes = sum(1 for ag in self.agentes if ag.evacuado)
        tasa_supervivencia = (sobrevivientes / total) if total > 0 else 0.0
        turnos_evacuacion = [
            ag.turno_evacuacion
            for ag in self.agentes
            if ag.turno_evacuacion is not None
        ]
        turnos_despeje = max(turnos_evacuacion) if turnos_evacuacion else None
        return sobrevivientes, total, tasa_supervivencia, turnos_despeje
