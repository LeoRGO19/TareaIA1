import random
from .algoritmo_de_busqueda import AlgoritmoBusqueda

class AlgoritmoGenetico(AlgoritmoBusqueda):
    usa_memoria_respaldo = True

    def __init__(self, tam_poblacion=8, generaciones=8, tasa_mutacion=0.15, prob_sesgo=0.65, longitud_maxima=60):
        super().__init__()
        self.tam_poblacion = max(2, tam_poblacion)
        self.generaciones = max(1, generaciones)
        self.tasa_mutacion = tasa_mutacion
        self.prob_sesgo = prob_sesgo
        self.longitud_maxima = longitud_maxima
        # Movimiento de esperar incluido
        self.acciones_ag = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def _mejor_direccion(self, pos, objetivo):
        mejor = self.acciones_ag[0]
        dist_minima = float('inf')
        
        for d in self.acciones_ag:
            dist = abs((pos[0] + d[0]) - objetivo[0]) + abs((pos[1] + d[1]) - objetivo[1])
            if dist < dist_minima:
                dist_minima = dist
                mejor = d
                
        return mejor

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

    def _mutar(self, individuo):
        """Cambia un gen por una acción distinta; una mutación nunca es un no-op."""
        if not individuo:
            return individuo
        indice = random.randrange(len(individuo))
        accion_actual = individuo[indice]
        alternativas = [accion for accion in self.acciones_ag if accion != accion_actual]
        individuo[indice] = random.choice(alternativas)
        return individuo

    def buscar(self, tablero, inicio, objetivo, heuristica=None, funcion_costo=None):
        filas, columnas = self._obtener_dimensiones(tablero)
        # se debe limitar la longitud del cromosoma para evitar que se generen rutas demasiado largas que no tengan sentido
        longitud_cromo = min(filas + columnas + 10, self.longitud_maxima)

        def evaluar(cromo):
            pos = inicio
            camino = [pos]
            costo_acumulado = 0.0
            llego_objetivo = False
            
            for df, dc in cromo:
                nf, nc = pos[0] + df, pos[1] + dc
                
                # Fuera de límites
                if not (0 <= nf < filas and 0 <= nc < columnas):
                    costo_acumulado += 2.0
                    camino.append(pos)
                    continue

                casilla = tablero[nf][nc]
                
         
                if casilla.puede_entrar():
                    pos = (nf, nc)
                    costo_paso = casilla.obtener_costo(funcion_costo) if funcion_costo else 1.0
                    costo_acumulado += costo_paso
                    camino.append(pos)
                    
                    if pos == objetivo:
                        llego_objetivo = True
                        break
                else:
                    if casilla.tipo == "fuego":
                        costo_acumulado += 10.0
                    else:
                        costo_acumulado += 1.5

            dist_restante = abs(pos[0] - objetivo[0]) + abs(pos[1] - objetivo[1])
            fitness = (dist_restante * 15.0) + costo_acumulado

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
        mejor_camino_factible = None
        mejor_costo_factible = float('inf')
        generaciones_sin_mejora = 0

        for _ in range(self.generaciones):
            evaluados = []
            for ind in poblacion:
                fit, cam, llego = evaluar(ind)
                evaluados.append((fit, cam, ind, llego))
            
            evaluados.sort(key=lambda x: x[0])

            for fit, cam, _, llego in evaluados:
                if llego and fit < mejor_costo_factible:
                    mejor_camino_factible = cam
                    mejor_costo_factible = fit
                    solucion_encontrada = True

            top_fit, top_cam, _, top_llego = evaluados[0]
            
            if (top_llego and not solucion_encontrada) or \
               (top_llego and top_fit < mejor_fit) or \
               (not solucion_encontrada and top_fit < mejor_fit):
                if top_fit < mejor_fit:
                    generaciones_sin_mejora = 0
                else:
                    generaciones_sin_mejora += 1
                mejor_fit = top_fit
                mejor_camino = top_cam
                if top_llego:
                    solucion_encontrada = True
            else:
                generaciones_sin_mejora += 1

            if generaciones_sin_mejora >= 3:
                break

            # selección
            mitad = max(2, self.tam_poblacion // 2)
            seleccionados = [item[2] for item in evaluados[:mitad]]
            nueva_pob = seleccionados[:]

            # reproducción y cruzamiento
            while len(nueva_pob) < self.tam_poblacion:
                p1, p2 = random.sample(seleccionados, 2)
                corte = random.randint(1, longitud_cromo - 1) if longitud_cromo > 1 else 1
                hijo = p1[:corte] + p2[corte:]
                
                # mutación
                if random.random() < self.tasa_mutacion:
                    self._mutar(hijo)
                    
                nueva_pob.append(hijo)

            poblacion = nueva_pob

        if mejor_camino_factible is not None:
            return mejor_camino_factible, True
        return mejor_camino, False
