from .algoritmo_de_busqueda import AlgoritmoBusqueda
import random

class AlgoritmoGenetico(AlgoritmoBusqueda):
    def __init__(self, tam_poblacion=15, generaciones=20, tasa_mutacion=0.15, prob_sesgo=0.65):
        super().__init__()
        self.tam_poblacion = tam_poblacion
        self.generaciones = generaciones
        self.tasa_mutacion = tasa_mutacion
        self.prob_sesgo = prob_sesgo
        # añadimos el movimiento de esperar, por eso no uso el que creé en la clase base
        self.acciones_ag = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    def _mejor_direccion(self, pos, objetivo):
        # retorna la acción que más acerca al objetivo según manhattan
        mejor = self.acciones_ag[0]
        dist_minima = float('inf')
        
        for d in self.acciones_ag:
            dist = abs((pos[0] + d[0]) - objetivo[0]) + abs((pos[1] + d[1]) - objetivo[1])
            if dist < dist_minima:
                dist_minima = dist
                mejor = d
                
        return mejor
    # genera un individuo aleatorio, con cierta probabilidad de sesgo hacia la mejor dirección        
    def _generar_individuo(self, inicio, objetivo, longitud):
        individuo = []
        pos_tentativa = inicio
        for _ in range(longitud):
            if random.random() < self.prob_sesgo:
                gen = self._mejor_direccion(pos_tentativa, objetivo)
            else:
                gen = random.choice(self.acciones_ag)
            individuo.append(gen)
            pos_tentativa = (pos_tentativa[0] + gen[0], pos_tentativa[1] + gen[1])
        return individuo

    def buscar(self, tablero, inicio, objetivo, heuristica=None, funcion_costo=None):
        filas, columnas = self._obtener_dimensiones(tablero)
        longitud_cromo = filas + columnas + 10

        def evaluar(cromo):
            pos = inicio
            camino = [pos]
            costo_acumulado = 0.0
            llego_objetivo = False
            
            for df, dc in cromo:
                nf, nc = pos[0] + df, pos[1] + dc
                
                # fuera de los límites de la grilla
                if not (0 <= nf < filas and 0 <= nc < columnas):
                    costo_acumulado += 2.0  # Penalización por perder el turno contra el borde
                    camino.append(pos)
                    continue

                casilla = tablero[nf][nc]
                
                # casilla transitable
                if casilla.puede_entrar():
                    pos = (nf, nc)
                    costo_paso = casilla.obtener_costo(funcion_costo) if funcion_costo else 1.0
                    costo_acumulado += costo_paso
                    camino.append(pos)
                    
                    if pos == objetivo:
                        llego_objetivo = True
                        break
                else:
                    # permanece donde está pero penaliza
                    if casilla.tipo == "fuego":
                        costo_acumulado += 10.0  # penaliza por intentar cruzar fuego
                    else:
                        costo_acumulado += 1.5   # penaliza por chocar contra un muro

            # distancia manhattan restante al objetivo desde donde quedó el agente
            dist_restante = abs(pos[0] - objetivo[0]) + abs(pos[1] - objetivo[1])

            # fitness base prioriza cercanía y menor costo
            fitness = (dist_restante * 15.0) + costo_acumulado

            # si no llegó, se penaliza proporcionalmente a la distancia faltante + bonus constante
            if not llego_objetivo:
                fitness += 200.0 + (dist_restante * 10.0)

            return fitness, camino, llego_objetivo

        # crear población inicial
        poblacion = [
            self._generar_individuo(inicio, objetivo, longitud_cromo) 
            for _ in range(self.tam_poblacion)
        ]
        
        mejor_camino = [inicio]
        mejor_fit = float('inf')
        solucion_encontrada = False

        for _ in range(self.generaciones):
            evaluados = []
            for ind in poblacion:
                fit, cam, llego = evaluar(ind)
                evaluados.append((fit, cam, ind, llego))
            
            # ordena por menor fitness
            evaluados.sort(key=lambda x: x[0])

            # actualizar mejor solución priorizando si realmente llegó
            top_fit, top_cam, _, top_llego = evaluados[0]
            
            # Acepta el nuevo camino si
            # o si encontró la meta por primera vez
            # o si ya tenía una solución válida y esta nueva es más eficiente
            # o si aún no encuentra la meta, pero este individuo llegó más cerca que los anteriores
            if (top_llego and not solucion_encontrada) or \
               (top_llego and top_fit < mejor_fit) or \
               (not solucion_encontrada and top_fit < mejor_fit):
                mejor_fit = top_fit
                mejor_camino = top_cam
                if top_llego:
                    solucion_encontrada = True

            # selección de la mejor mitad
            mitad = self.tam_poblacion // 2
            seleccionados = [item[2] for item in evaluados[:mitad]]
            nueva_pob = seleccionados[:]

            # reproducción y cruzamiento
            while len(nueva_pob) < self.tam_poblacion:
                p1, p2 = random.sample(seleccionados, 2)
                corte = random.randint(1, longitud_cromo - 1)
                hijo = p1[:corte] + p2[corte:]
                
                # mutación
                if random.random() < self.tasa_mutacion:
                    idx = random.randint(0, longitud_cromo - 1)
                    hijo[idx] = random.choice(self.acciones_ag)
                    
                nueva_pob.append(hijo)

            poblacion = nueva_pob

        return mejor_camino


