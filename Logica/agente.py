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
        self.ruta_planeada = [] # Guarda la ruta generada para no recalcular en cada paso si no es necesario
        self.turnos_esperando = 0  # Cantidad de turnos retenido por espera por el cuello de botella/congestión

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

        # Comprobar si la ruta actual sigue siendo válida (si el siguiente paso no se quemó)
        necesita_recalcular = False
        if not self.ruta_planeada or len(self.ruta_planeada) <= 1:
            necesita_recalcular = True
        else:
            siguiente_paso = self.ruta_planeada[1]
            casilla_paso = grilla.obtener_casilla(siguiente_paso[0], siguiente_paso[1])
            # Se fuerza el calculo si el siguiente paso se incendió o bloqueó
            if not casilla_paso or not casilla_paso.puede_entrar():
                necesita_recalcular = True

        # Si no hay ruta o el camino fue bloqueado por fuego/muro, calculamos de nuevo
        if necesita_recalcular:
            self.ruta_planeada = self.algoritmo.buscar(
                grilla.tablero,
                self.posicion,
                objetivo,
                funcion_costo=costo_congestion_cuadratica
            )

        siguiente = None
        origen_ruta = False  # True si "siguiente" viene de ruta_planeada (para saber si hay que consumirla)
        if self.ruta_planeada and len(self.ruta_planeada) > 1:
            siguiente = self.ruta_planeada[1]
            origen_ruta = True
        else:
            # Si no hay ruta a la meta (callejón sin salida),
            # avanza a un vecino válido evitando volver a la casilla inmediatamente anterior
            vecinos = grilla.obtener_vecinos(self.posicion)
            validos = [v for v in vecinos if grilla.obtener_casilla(v[0], v[1]).puede_entrar()]

            # Prioriza casillas que no sean la 'posicion_anterior'
            opciones = [v for v in validos if v != self.posicion_anterior]
            if opciones:
                siguiente = opciones[0]
            elif validos:
                siguiente = validos[0]  # Si está acorralado, no le queda opción más que retroceder

        if siguiente is None:
            # Acorralado sin ningún vecino transitable: la única acción posible es esperar.
            self.turnos_esperando += 1
            return

        casilla_sig = grilla.obtener_casilla(siguiente[0], siguiente[1])
        if not casilla_sig or not casilla_sig.puede_entrar():
            self.turnos_esperando += 1
            return
        
        if siguiente != objetivo and casilla_sig.esta_congestionada():
            self.turnos_esperando += 1
            return

        # Ejecutar el movimiento en la grilla
        casilla_act.remover_agente(self)
        self.posicion_anterior = self.posicion
        self.posicion = siguiente
        casilla_sig.agregar_agente(self)

        # Sólo consumimos el paso de la ruta planeada si efectivamente nos movimos
        if origen_ruta:
            self.ruta_planeada.pop(0)

        if self.posicion == objetivo:
            self.evacuado = True
            casilla_sig.remover_agente(self)
