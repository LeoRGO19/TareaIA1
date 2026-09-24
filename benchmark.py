import numpy as np
from Logica.gestor_de_eventos import GestorDeEventos
from Logica.bfs import BusquedaBFS
from Logica.dfs import BusquedaDFS
from Logica.a_estrella import BusquedaEstrella
from Logica.ida import AlgoritmoBusquedaIDAEstrella
from Logica.algoritmo_genetico import AlgoritmoGenetico

def evaluar_configuracion(mapa_file, nombre_mapa, algoritmo_cls, es_informado, nombre_algo, n_iteraciones=80):
    tasas_supervivencia = []
    tiempos_despeje = []

    for _ in range(n_iteraciones):
        gestor = GestorDeEventos(mapa_file, algoritmo_cls, es_informado=es_informado, k_turnos_fuego=3)
        
        while not gestor.simulación_terminada() and gestor.turnos_totales < 300:
            gestor.ejecutar_turno()

        sobrevivientes, total, tasa, turnos = gestor.obtener_resultados()
        tasas_supervivencia.append(tasa)
        tiempos_despeje.append(turnos)

    print(f"[{nombre_mapa}] -> Algoritmo: {nombre_algo}")
    print(f"  Tasa Supervivencia Media: {np.mean(tasas_supervivencia) * 100:.2f}%")
    print(f"  Turnos Despeje (Media ± Std): {np.mean(tiempos_despeje):.2f} ± {np.std(tiempos_despeje):.2f}")
    print(f"  Rango Turnos [Min, Max]: [{np.min(tiempos_despeje)}, {np.max(tiempos_despeje)}]")
    print("-" * 50)

if __name__ == "__main__":
    mapas = [
        ("mapa_laberinto_cuello_botella.txt", "Mapa 1: Cuello de Botella"),
        ("mapa_laberinto_corporativo.txt", "Mapa 2: Laberinto Corporativo"),
        ("mapa_abierto.txt", "Mapa 3: Dispersión Abierta")
    ]

    algoritmos = [
        (BusquedaBFS, False, "BFS (No Informado)"),
        (BusquedaDFS, False, "DFS (No Informado)"),
        (BusquedaEstrella, True, "A* (Informado)"),
        (AlgoritmoBusquedaIDAEstrella, True, "IDA* (Informado)"),
        (AlgoritmoGenetico, True, "Algoritmo Genético (Bioinspirado)")
    ]

    print("=" * 60)
    print("EJECUTANDO SUITE DE BENCHMARKING (80 Iteraciones por Configuración)")
    print("=" * 60)

    for ruta_mapa, nombre_mapa in mapas:
        for alg_cls, es_inf, nombre_alg in algoritmos:
            evaluar_configuracion(ruta_mapa, nombre_mapa, alg_cls, es_inf, nombre_alg, n_iteraciones=80)