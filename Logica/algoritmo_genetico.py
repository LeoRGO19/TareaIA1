from .algoritmo_de_busqueda import AlgoritmoBusqueda
import random


class AlgoritmoGenetico(AlgoritmoBusqueda):
    def __init__(self, tam_poblacion=40, generaciones=40, tasa_mutacion=0.15, prob_sesgo=0.65):
        super().__init__()
        self.tam_poblacion = tam_poblacion
        self.generaciones = generaciones
        self.tasa_mutacion = tasa_mutacion
        self.prob_sesgo = prob_sesgo
        # Movimientos ortogonales + acción 'esperar' (0,0) para el cromosoma
        self.acciones_ag = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    def _mejor_direccion(self, pos, objetivo):
        # Retorna la acción que más acerca al objetivo según Manhattan
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

    def buscar(self, tablero, inicio, objetivo, heuristica=None, funcion_costo=None):
        filas, columnas = self._obtener_dimensiones(tablero)
        longitud_cromo = filas + columnas + 10

        def evaluar(cromo):
            pos = inicio
            camino = [pos]
            costo_total = 0
            for df, dc in cromo:
                nf, nc = pos[0] + df, pos[1] + dc
                if 0 <= nf < filas and 0 <= nc < columnas:
                    casilla = tablero[nf][nc]
                    if casilla.puede_entrar():
                        pos = (nf, nc)
                        costo_total += casilla.obtener_costo(funcion_costo) if funcion_costo else 1.0
                        camino.append(pos)
                        if pos == objetivo:
                            break
                    else:
                        costo_total += 50.0 # Penalización por muro/fuego
                else:
                    costo_total += 50.0 # Penalización por salir del mapa
            dist = abs(pos[0] - objetivo[0]) + abs(pos[1] - objetivo[1])
            fitness = dist * 10 + costo_total
            return fitness, camino

        # Crea la población inicial
        poblacion = []
        for _ in range(self.tam_poblacion):
            poblacion.append(self._generar_individuo(inicio, objetivo, longitud_cromo))
        mejor_camino = [inicio]
        mejor_fit = float('inf')

        for _ in range(self.generaciones):
            evaluados = []
            for ind in poblacion:
                fit, cam = evaluar(ind)
                evaluados.append((fit, cam, ind))
            # Ordena por menor fitness
            evaluados.sort(key=lambda x: x[0])

            if evaluados[0][0] < mejor_fit:
                mejor_fit = evaluados[0][0]
                mejor_camino = evaluados[0][1]

            # Seleccionamos la mejor mitad de la población (elitismo)
            mitad = self.tam_poblacion // 2
            seleccionados = [item[2] for item in evaluados[:mitad]]
            nueva_pob = seleccionados[:]  

            # Reproducción y Cruzamiento
            while len(nueva_pob) < self.tam_poblacion:
                p1, p2 = random.sample(seleccionados, 2)
                corte = random.randint(1, longitud_cromo - 1)
                hijo = p1[:corte] + p2[corte:]
                if random.random() < self.tasa_mutacion:
                    idx = random.randint(0, longitud_cromo - 1)
                    hijo[idx] = random.choice(self.acciones_ag)
                nueva_pob.append(hijo)

            poblacion = nueva_pob

        return mejor_camino
