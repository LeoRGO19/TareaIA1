import numpy as np
from Logica.gestor_de_eventos import GestorDeEventos
from Logica.bfs import BusquedaBFS
from Logica.dfs import BusquedaDFS
from Logica.a_estrella import BusquedaEstrella
from Logica.ida import AlgoritmoBusquedaIDAEstrella
from Logica.algoritmo_genetico import AlgoritmoGenetico
NUMERO_DE_ITERACIONES = 100
KTURNOS_FUEGO = 4
def evaluar_configuracion(mapa_file, nombre_mapa, algoritmo_cls, es_informado, nombre_algo, n_iteraciones=NUMERO_DE_ITERACIONES):
    tasas_supervivencia = []
    tiempos_despeje = []

    for _ in range(n_iteraciones):
        gestor = GestorDeEventos(mapa_file, algoritmo_cls, es_informado=es_informado, k_turnos_fuego=KTURNOS_FUEGO)
        
        while not gestor.simulacion_terminada() and gestor.turnos_totales < 300:
            gestor.ejecutar_turno()

        sobrevivientes, total, tasa, turnos_despeje = gestor.obtener_resultados()
        tasas_supervivencia.append(tasa)
        if turnos_despeje is not None:
            tiempos_despeje.append(turnos_despeje)
        iteracion_actual = _ + 1

        if iteracion_actual % (max(1, n_iteraciones // 10)) == 0 or iteracion_actual == n_iteraciones:
            print(f"  > Progreso: {iteracion_actual}/{n_iteraciones} simulaciones completadas...", flush=True)

    print(f"[{nombre_mapa}] -> Algoritmo: {nombre_algo}")
    print(f"  Tasa Supervivencia Media: {np.mean(tasas_supervivencia) * 100:.2f}%")
    if tiempos_despeje:
        print(f"  Turnos Despeje (Media ± Std): {np.mean(tiempos_despeje):.2f} ± {np.std(tiempos_despeje):.2f}")
        print(f"  Rango Turnos [Min, Max]: [{np.min(tiempos_despeje)}, {np.max(tiempos_despeje)}]")
    else:
        print("  Turnos Despeje: N/A (ninguna simulación tuvo agentes evacuados)")
    print(f"  Corridas con tiempo definido: {len(tiempos_despeje)}/{n_iteraciones}")
    print("-" * 50)

if __name__ == "__main__":
    mapas = [
        ("mapa_cuello_botella50x50.txt", "Mapa 1: Cuello de Botella"),
        ("mapa_corporativo50x50.txt", "Mapa 2: Laberinto Corporativo"),
        ("mapa_abierto50x50.txt", "Mapa 3: Dispersión Abierta")
    ]

    algoritmos = [
        (BusquedaBFS, False, "BFS (No Informado)"),
        (BusquedaDFS, False, "DFS (No Informado)"),
        (BusquedaEstrella, True, "A* (Informado)"),
        (AlgoritmoBusquedaIDAEstrella, True, "IDA* (Informado)"),
        (AlgoritmoGenetico, True, "Algoritmo Genético (Informado)"),

    ]

    print("=" * 60)
    print(f"EJECUTANDO SUITE DE BENCHMARKING ({NUMERO_DE_ITERACIONES} Iteraciones por Configuración)")
    print("=" * 60)

    for ruta_mapa, nombre_mapa in mapas:
        for alg_cls, es_inf, nombre_alg in algoritmos:
            evaluar_configuracion(ruta_mapa, nombre_mapa, alg_cls, es_inf, nombre_alg, n_iteraciones=NUMERO_DE_ITERACIONES)