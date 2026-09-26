from .casilla import costo_congestion_cuadratica

class Agente:
    def __init__(self, id_agente, posicion_inicial, algoritmo_busqueda, es_informado=True, color=(0, 0, 255)):
        self.id = id_agente
        self.posicion = posicion_inicial
        self.posicion_anterior = None
        self.algoritmo = algoritmo_busqueda
        self.es_informado = es_informado
        self.color = color
        self.evacuado = False
        self.fallecido = False
        self.turno_evacuacion = None
        self.ruta_planeada = [] # guarda la ruta generada para no recalcular en cada paso si no es necesario
        self.turnos_esperando = 0  # cantidad de turnos retenido por espera por el cuello de botella
        self.turnos_hasta_reintento = 0  # tiempo de enfriamiento si falla la búsqueda

    def mover(self, grilla, objetivo):
        if self.evacuado or self.fallecido:
            return

        casilla_act = grilla.obtener_casilla(self.posicion[0], self.posicion[1])

        if casilla_act.tipo == "fuego":
            self.fallecido = True
            casilla_act.remover_agente(self)
            return

        if self.posicion == objetivo:
            self.evacuado = True
            casilla_act.remover_agente(self)
            return

        # decrementa el contador de espera para reintentar búsqueda si está activo
        if self.turnos_hasta_reintento > 0:
            self.turnos_hasta_reintento -= 1

        # comprueba si se requiere recalcular la ruta
        necesita_recalcular = False
        if not self.ruta_planeada or len(self.ruta_planeada) <= 1:
            # solo recalcula si no está en período de enfriamiento
            if self.turnos_hasta_reintento == 0:
                necesita_recalcular = True
        else:
            siguiente_paso = self.ruta_planeada[1]
            casilla_paso = grilla.obtener_casilla(siguiente_paso[0], siguiente_paso[1])
            # se fuerza el cálculo si el siguiente paso se incendió o bloqueó (y expiró el enfriamiento)
            if (not casilla_paso or not casilla_paso.puede_entrar()) and self.turnos_hasta_reintento == 0:
                necesita_recalcular = True

        # si necesita recalcular y finalizó el enfriamiento
        if necesita_recalcular:
            resultado_busqueda = self.algoritmo.buscar(
                grilla.tablero,
                self.posicion,
                objetivo,
                funcion_costo=costo_congestion_cuadratica
            )

            # normaliza rutas simples, tuplas y respuestas None de algoritmos sin solución.
            if isinstance(resultado_busqueda, tuple):
                ruta, encontro_ruta = resultado_busqueda
            else:
                ruta = resultado_busqueda
                encontro_ruta = bool(ruta) and len(ruta) > 1 and ruta[-1] == objetivo

            if ruta is None:
                ruta = []
                encontro_ruta = False

            if encontro_ruta:
                self.ruta_planeada = ruta
                self.turnos_hasta_reintento = 0
            else:
                self.ruta_planeada = []
                self.turnos_hasta_reintento = 5  # bloquea reintentos por 5 turnos

        siguiente = None
        origen_ruta = False  # para saber si hay que consumirla
        if self.ruta_planeada and len(self.ruta_planeada) > 1:
            siguiente = self.ruta_planeada[1]
            origen_ruta = True
        else:
            # si no hay ruta a la meta avanza a un vecino válido evitando volver a la casilla inmediatamente anterior
            vecinos = grilla.obtener_vecinos(self.posicion)
            validos = [v for v in vecinos if grilla.obtener_casilla(v[0], v[1]).puede_entrar()]

            # prioriza casillas que no sean la posición anterior
            opciones = [v for v in validos if v != self.posicion_anterior]
            if opciones:
                siguiente = opciones[0]
            elif validos:
                siguiente = validos[0]  # si está acorralado debe retroceder

        if siguiente is None:
            # si está acorralado sin ningún vecino transitable debe esperar
            self.turnos_esperando += 1
            return

        casilla_sig = grilla.obtener_casilla(siguiente[0], siguiente[1])
        if not casilla_sig or not casilla_sig.puede_entrar():
            self.turnos_esperando += 1
            return
        
        if siguiente != objetivo and casilla_sig.esta_congestionada():
            self.turnos_esperando += 1
            return

        # ejecuta el movimiento en la grilla
        casilla_act.remover_agente(self)
        self.posicion_anterior = self.posicion
        self.posicion = siguiente
        casilla_sig.agregar_agente(self)

        # solo consumimos el paso de la ruta planeada si efectivamente nos movimos
        if origen_ruta:
            self.ruta_planeada.pop(0)

        if self.posicion == objetivo:
            self.evacuado = True
            casilla_sig.remover_agente(self)