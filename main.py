"""Interfaz Pygame para simulaciones individuales y benchmarking por lotes."""
from __future__ import annotations

import queue
import statistics
import threading
import time
from collections import Counter

import pygame

from Logica.a_estrella import BusquedaEstrella
from Logica.algoritmo_genetico import AlgoritmoGenetico
from Logica.bfs import BusquedaBFS
from Logica.dfs import BusquedaDFS
from Logica.gestor_de_eventos import GestorDeEventos
from Logica.ida import AlgoritmoBusquedaIDAEstrella
from Logica.lector_de_mapas import LectorDeMapas


MAPAS = (
    ("Cuello", "mapa_cuello_botella50x50.txt"),
    ("Laberinto", "mapa_corporativo50x50.txt"),
    ("Abierto", "mapa_abierto50x50.txt"),
)
ALGORITMOS = (
    ("BFS", BusquedaBFS, False),
    ("DFS", BusquedaDFS, False),
    ("A*", BusquedaEstrella, True),
    ("IDA*", AlgoritmoBusquedaIDAEstrella, True),
    ("Genético", AlgoritmoGenetico, True),
)
ITERACIONES = (1, 5, 10, 25, 50, 100)
VALORES_K = (1, 2, 3, 4, 5, 10)
PROBABILIDADES_PARED = (0.0, 0.02, 0.05, 0.10, 0.25)
VELOCIDADES = (1, 2, 4, 8, 12, 20, 30)
LIMITE_AGENTES = 80
LIMITE_TURNOS = 300

FONDO = (17, 24, 34)
PANEL = (27, 37, 50)
BORDE = (57, 73, 91)
TEXTO = (234, 240, 246)
SECUNDARIO = (162, 178, 194)
ACENTO = (55, 166, 190)
VERDE = (79, 190, 130)


def maximo_agentes(mapa_idx, modo, mapa_idx_benchmark):
    indices = range(len(MAPAS)) if modo == "Benchmark" and mapa_idx_benchmark == len(MAPAS) else (mapa_idx,)
    disponibles = [len(LectorDeMapas.cargar_mapa(MAPAS[i][1])[2]) for i in indices]
    return min(LIMITE_AGENTES, min(disponibles, default=1))


def crear_gestor(mapa_idx, algoritmo_idx, agentes, k, prob_pared):
    nombre_mapa, archivo = MAPAS[mapa_idx]
    _, algoritmo, informado = ALGORITMOS[algoritmo_idx]
    total_disponible = len(LectorDeMapas.cargar_mapa(archivo)[2])
    return GestorDeEventos(
        archivo,
        algoritmo,
        es_informado=informado,
        k_turnos_fuego=k,
        numero_agentes=min(LIMITE_AGENTES, agentes, total_disponible),
        probabilidad_atravesar_pared=prob_pared,
    )


def resumir(mapa, nombre_algoritmo, tasas, despejes, duraciones, total,
            busquedas_ida=0, limites_ida=0):
    return {
        "mapa": mapa,
        "algoritmo": nombre_algoritmo,
        "supervivencia": statistics.fmean(tasas) * 100 if tasas else 0.0,
        "media": statistics.fmean(despejes) if despejes else None,
        "desviacion": statistics.pstdev(despejes) if len(despejes) > 1 else 0.0,
        "minimo": min(despejes) if despejes else None,
        "maximo": max(despejes) if despejes else None,
        "corridas_validas": len(despejes),
        "corridas": total,
        "segundos_por_corrida": statistics.fmean(duraciones) if duraciones else 0.0,
        "busquedas_ida": busquedas_ida,
        "limites_ida": limites_ida,
    }


def ejecutar_benchmark(configuracion, eventos, cancelacion):
    """Ejecuta el benchmark sin animación; la ventana permanece receptiva."""
    if configuracion["mapa"] == "Todos":
        mapas = MAPAS
    else:
        mapas = (MAPAS[configuracion["mapa"]],)
    total_operaciones = len(mapas) * len(ALGORITMOS) * configuracion["iteraciones"]
    completadas = 0
    duraciones_recientes = []
    inicio = time.perf_counter()
    resultados = []

    for etiqueta_mapa, archivo_mapa in mapas:
        disponibles = len(LectorDeMapas.cargar_mapa(archivo_mapa)[2])
        for nombre_algoritmo, algoritmo, informado in ALGORITMOS:
            tasas, despejes, duraciones = [], [], []
            llamadas_ida, limites_ida = 0, 0
            for indice in range(configuracion["iteraciones"]):
                if cancelacion.is_set():
                    eventos.put(("cancelado", resultados))
                    return
                inicio_corrida = time.perf_counter()
                gestor = GestorDeEventos(
                    archivo_mapa, algoritmo, es_informado=informado,
                    k_turnos_fuego=configuracion["k"],
                    numero_agentes=min(LIMITE_AGENTES, configuracion["agentes"], disponibles),
                    probabilidad_atravesar_pared=configuracion["prob_pared"],
                )
                while not gestor.simulacion_terminada() and gestor.turnos_totales < LIMITE_TURNOS:
                    gestor.ejecutar_turno()
                _, _, tasa, despeje = gestor.obtener_resultados()
                duracion = time.perf_counter() - inicio_corrida
                tasas.append(tasa)
                duraciones.append(duracion)
                if despeje is not None:
                    despejes.append(despeje)
                llamadas_ida += sum(getattr(ag.algoritmo, "llamadas_busqueda", 0)
                                    for ag in gestor.agentes)
                limites_ida += sum(getattr(ag.algoritmo, "limites_nodos_acumulados", 0)
                                    for ag in gestor.agentes)

                completadas += 1
                duraciones_recientes.append(duracion)
                eta = statistics.fmean(duraciones_recientes[-30:]) * (
                    total_operaciones - completadas)
                eventos.put(("progreso", {
                    "hechas": completadas, "total": total_operaciones,
                    "mapa": etiqueta_mapa, "algoritmo": nombre_algoritmo,
                    "corrida": indice + 1,
                    "corridas_config": configuracion["iteraciones"],
                    "eta": eta, "transcurrido": time.perf_counter() - inicio,
                }))

            fila = resumir(etiqueta_mapa, nombre_algoritmo, tasas, despejes,
                           duraciones, configuracion["iteraciones"],
                           llamadas_ida, limites_ida)
            resultados.append(fila)
            eventos.put(("resultado", fila))
    eventos.put(("terminado", {"resultados": resultados,
                                "transcurrido": time.perf_counter() - inicio}))


def ejecutar_benchmark_seguro(configuracion, eventos, cancelacion):
    try:
        ejecutar_benchmark(configuracion, eventos, cancelacion)
    except Exception as error:
        eventos.put(("error", str(error)))


def texto(superficie, fuente, contenido, posicion, color=TEXTO):
    superficie.blit(fuente.render(str(contenido), True, color), posicion)


def boton(superficie, fuente, rect, etiqueta, activo=True):
    pygame.draw.rect(superficie, ACENTO if activo else (42, 55, 71), rect,
                     border_radius=7)
    pygame.draw.rect(superficie, BORDE, rect, 1, border_radius=7)
    renderizado = fuente.render(str(etiqueta), True, TEXTO)
    superficie.blit(renderizado, renderizado.get_rect(center=rect.center))


def formato_duracion(segundos):
    if segundos is None:
        return "calculando..."
    segundos = max(0, int(segundos))
    horas, resto = divmod(segundos, 3600)
    minutos, seg = divmod(resto, 60)
    return f"{horas:d}:{minutos:02d}:{seg:02d}" if horas else f"{minutos:d}:{seg:02d}"


def capturar_estado(gestor, mapa, algoritmo, iteracion=1):
    return {
        "mapa": mapa, "algoritmo": algoritmo, "iteracion": iteracion,
        "turno": gestor.turnos_totales,
        "filas": gestor.grilla.filas, "columnas": gestor.grilla.columnas,
        "tablero": tuple(tuple(c.tipo for c in fila) for fila in gestor.grilla.tablero),
        "salida": gestor.objetivo,
        "agentes": tuple((a.posicion, a.color) for a in gestor.agentes
                         if not a.evacuado and not a.fallecido),
        "evacuados": sum(a.evacuado for a in gestor.agentes),
        "bajas": sum(a.fallecido for a in gestor.agentes),
        "k": gestor.k_turnos_fuego,
        "prob_pared": gestor.probabilidad_atravesar_pared,
    }


def dibujar_mapa(pantalla, marco, rect, fuente):
    pygame.draw.rect(pantalla, PANEL, rect, border_radius=10)
    encabezado = (f"{marco['mapa']} · {marco['algoritmo']} · turno {marco['turno']} · "
                  f"k={marco['k']}")
    texto(pantalla, fuente, encabezado, (rect.x + 18, rect.y + 14))
    area = pygame.Rect(rect.x + 20, rect.y + 46, rect.width - 40, rect.height - 90)
    filas, columnas = marco["filas"], marco["columnas"]
    tam = max(1, min(area.width // columnas, area.height // filas))
    x0 = area.x + (area.width - columnas * tam) // 2
    y0 = area.y + (area.height - filas * tam) // 2
    colores = {"camino": (235, 237, 239), "muro": (58, 65, 73), "fuego": (226, 69, 46)}
    for f, fila in enumerate(marco["tablero"]):
        for c, tipo in enumerate(fila):
            celda = pygame.Rect(x0 + c * tam, y0 + f * tam, tam, tam)
            pygame.draw.rect(pantalla, colores.get(tipo, (235, 237, 239)), celda)
            if tam > 7:
                pygame.draw.rect(pantalla, (180, 185, 191), celda, 1)
    if marco["salida"]:
        f, c = marco["salida"]
        pygame.draw.rect(pantalla, VERDE, (x0 + c * tam, y0 + f * tam, tam, tam),
                         max(2, tam // 5))
    cantidades = Counter(pos for pos, _ in marco["agentes"])
    fuente_conteo = pygame.font.SysFont("Arial", max(10, min(14, tam)), bold=True)
    for pos, color in marco["agentes"]:
        centro = (x0 + pos[1] * tam + tam // 2, y0 + pos[0] * tam + tam // 2)
        pygame.draw.circle(pantalla, color, centro, max(2, tam // 3))
    for (f, c), cantidad in cantidades.items():
        if cantidad > 1:
            marca = fuente_conteo.render(f"x{cantidad}", True, (255, 70, 55))
            sombra = fuente_conteo.render(f"x{cantidad}", True, (20, 20, 20))
            x, y = x0 + c * tam + 1, y0 + f * tam + 1
            pantalla.blit(sombra, (x + 1, y + 1))
            pantalla.blit(marca, (x, y))
    texto(pantalla, fuente,
          f"Activos: {len(marco['agentes'])}   Evacuados: {marco['evacuados']}   "
          f"Bajas: {marco['bajas']}   Transmisión por pared: {marco['prob_pared']:.0%}",
          (rect.x + 18, rect.bottom - 30), SECUNDARIO)


def dibujar_resultados(pantalla, filas, rect, fuentes, mensaje, titulo="Resultados del benchmark"):
    fuente, pequena, fuente_titulo = fuentes
    pygame.draw.rect(pantalla, PANEL, rect, border_radius=10)
    texto(pantalla, fuente_titulo, titulo, (rect.x + 20, rect.y + 16))
    texto(pantalla, pequena, mensaje, (rect.x + 22, rect.y + 55), SECUNDARIO)
    columnas = (rect.x + 22, rect.x + 248, rect.x + 354, rect.x + 455,
                rect.x + 526, rect.x + 622, rect.x + 730)
    encabezados = ("Mapa / algoritmo", "Superv.", "Turnos μ", "DE", "Mín–Máx", "Válidas", "s/rep")
    for x, valor in zip(columnas, encabezados):
        texto(pantalla, pequena, valor, (x, rect.y + 105), SECUNDARIO)
    pygame.draw.line(pantalla, BORDE, (rect.x + 20, rect.y + 129),
                     (rect.right - 18, rect.y + 129), 1)
    paso = min(31, max(22, (rect.height - 145) // max(1, len(filas))))
    for i, fila in enumerate(filas):
        y = rect.y + 140 + i * paso
        mapa = fila["mapa"].replace("Cuello de botella", "Cuello").replace(
            "Laberinto corporativo", "Laberinto").replace("Dispersión abierta", "Abierto")
        despeje = "N/D" if fila["media"] is None else f"{fila['media']:.1f}"
        rango = "N/D" if fila["minimo"] is None else f"{fila['minimo']}–{fila['maximo']}"
        valores = (f"{mapa} · {fila['algoritmo']}", f"{fila['supervivencia']:.1f}%",
                   despeje, f"{fila['desviacion']:.1f}", rango,
                   f"{fila['corridas_validas']}/{fila['corridas']}",
                   f"{fila['segundos_por_corrida']:.2f}")
        for x, valor in zip(columnas, valores):
            texto(pantalla, pequena, valor, (x, y))
        if fila["algoritmo"] == "IDA*":
            texto(pantalla, pequena,
                  f"Límite de nodos: {fila['limites_ida']}/{fila['busquedas_ida']} llamadas",
                  (rect.x + 22, y + 14), SECUNDARIO)


def dibujar_configuracion(pantalla, fuentes, estado):
    fuente, pequena, _ = fuentes
    rect = pygame.Rect(18, 92, 306, 648)
    pygame.draw.rect(pantalla, PANEL, rect, border_radius=12)
    config, botones = estado["config"], estado["botones"]
    texto(pantalla, fuente, "Configuración", (38, 110))

    texto(pantalla, pequena, "Modo", (38, 151), SECUNDARIO)
    boton(pantalla, pequena, botones["modo"], config["modo"], not estado["ocupado"])
    texto(pantalla, pequena, "Mapa", (38, 207), SECUNDARIO)
    boton(pantalla, pequena, botones["mapa"], config["mapa"], not estado["ocupado"])
    texto(pantalla, pequena, "Algoritmo de la simulación", (38, 263), SECUNDARIO)
    boton(pantalla, pequena, botones["algoritmo"],
          config["algoritmo"] if config["modo"] == "Simulación" else "Todos",
          config["modo"] == "Simulación" and not estado["ocupado"])
    texto(pantalla, pequena, "Personas (máximo 80)", (38, 319), SECUNDARIO)
    boton(pantalla, pequena, botones["menos_agentes"], "−", not estado["ocupado"])
    boton(pantalla, pequena, botones["mas_agentes"], "+", not estado["ocupado"])
    texto(pantalla, fuente, f"{config['agentes']} / {config['max_agentes']}", (183, 358))
    texto(pantalla, pequena, "Fuego cada k turnos", (38, 402), SECUNDARIO)
    boton(pantalla, pequena, botones["k"], str(config["k"]), not estado["ocupado"])
    texto(pantalla, pequena, "Prob. de atravesar pared", (38, 458), SECUNDARIO)
    boton(pantalla, pequena, botones["pared"], f"{config['prob_pared']:.0%}", not estado["ocupado"])

    if config["modo"] == "Simulación":
        texto(pantalla, pequena, "Velocidad de visualización", (38, 514), SECUNDARIO)
        boton(pantalla, pequena, botones["menos_velocidad"], "−", not estado["ocupado"])
        boton(pantalla, pequena, botones["mas_velocidad"], "+", not estado["ocupado"])
        texto(pantalla, fuente, f"{config['velocidad']} turnos/s aprox.", (118, 552))
        texto(pantalla, pequena, "Una simulación por ejecución.", (38, 592), SECUNDARIO)
    else:
        texto(pantalla, pequena, "Repeticiones por algoritmo", (38, 514), SECUNDARIO)
        boton(pantalla, pequena, botones["menos_iter"], "−", not estado["ocupado"])
        boton(pantalla, pequena, botones["mas_iter"], "+", not estado["ocupado"])
        texto(pantalla, fuente, str(config["iteraciones"]), (183, 552))
        texto(pantalla, pequena, "Benchmark sin animación.", (38, 592), SECUNDARIO)

    if estado["progreso"] and config["modo"] == "Benchmark":
        p = estado["progreso"]
        texto(pantalla, pequena, f"{p['hechas']}/{p['total']} operaciones", (38, 617))
        texto(pantalla, pequena, f"Restante ~{formato_duracion(p['eta'])}", (38, 638), VERDE)
    elif estado["mensaje"]:
        texto(pantalla, pequena, estado["mensaje"][:39], (38, 628), SECUNDARIO)

    if config["modo"] == "Benchmark":
        etiqueta = "Benchmark en curso" if estado["ocupado"] else "Iniciar benchmark"
        accion_habilitada = not estado["ocupado"]
    elif estado["sim_activa"]:
        etiqueta = "Forzar fin"
        accion_habilitada = True
    else:
        etiqueta = "Nueva simulación" if estado["sim_finalizada"] else "Iniciar simulación"
        accion_habilitada = True
    boton(pantalla, fuente, botones["accion"], etiqueta, accion_habilitada)
    if config["modo"] == "Simulación":
        boton(pantalla, pequena, botones["pausa"], "Reanudar" if estado["pausada"] else "Pausar",
              estado["sim_activa"])
    texto(pantalla, pequena, "Esc: salir", (38, 713), SECUNDARIO)


def dibujar_pantalla(pantalla, fuentes, estado):
    pantalla.fill(FONDO)
    _, pequena, fuente_titulo = fuentes
    texto(pantalla, fuente_titulo, "Escape de la torre", (22, 17))
    texto(pantalla, pequena, "Simulación visual y evaluación comparativa", (24, 56), SECUNDARIO)
    dibujar_configuracion(pantalla, fuentes, estado)
    rect_derecho = pygame.Rect(338, 92, 884, 648)
    resultados_visibles = (estado["config"]["modo"] == "Benchmark"
                           or estado["sim_finalizada"])
    if resultados_visibles:
        if estado["config"]["modo"] == "Benchmark":
            dibujar_resultados(pantalla, estado["resultados"], rect_derecho, fuentes,
                               estado["mensaje"] or "Resultados parciales mientras avanza el benchmark.")
        else:
            r = estado["resultado_sim"]
            if r:
                _, _, tasa, despeje = r
                fallecidos = estado["fallecidos"]
                titulo = "Resultado de la simulación"
                mensaje = (f"Evacuados: {r[0]}/{r[1]} ({tasa * 100:.1f}%)   ·   "
                           f"Bajas: {fallecidos}   ·   Turno de despeje: "
                           f"{despeje if despeje is not None else 'N/D'}")
                dibujar_resultados(pantalla, [resumir(
                    estado["mapa_nombre"], estado["algoritmo_nombre"], [tasa],
                    [despeje] if despeje is not None else [],
                    [estado["duracion_sim"]], 1)], rect_derecho, fuentes, mensaje, titulo)
            else:
                pygame.draw.rect(pantalla, PANEL, rect_derecho, border_radius=10)
    elif estado["marco"]:
        dibujar_mapa(pantalla, estado["marco"], rect_derecho, pequena)
    else:
        pygame.draw.rect(pantalla, PANEL, rect_derecho, border_radius=10)
        texto(pantalla, fuentes[0], "La simulación aparecerá aquí", (rect_derecho.x + 24,
              rect_derecho.y + 24))
        texto(pantalla, pequena, "Configura las opciones y pulsa Iniciar / reiniciar.",
              (rect_derecho.x + 24, rect_derecho.y + 64), SECUNDARIO)
    pygame.display.flip()


def main():
    pygame.init()
    pygame.display.set_caption("Escape de la torre")
    pantalla = pygame.display.set_mode((1240, 760))
    fuentes = (pygame.font.SysFont("Arial", 16), pygame.font.SysFont("Arial", 14),
               pygame.font.SysFont("Arial", 25, bold=True))
    reloj = pygame.time.Clock()
    eventos = queue.Queue()
    cancelacion = threading.Event()

    modo = "Simulación"
    mapa_idx = 0
    algoritmo_idx = 4
    k_idx = VALORES_K.index(5)
    pared_idx = 0
    iter_idx = 2
    velocidades_idx = VELOCIDADES.index(8)
    max_agentes = maximo_agentes(mapa_idx, modo, mapa_idx)
    agentes = min(80, max_agentes)

    botones = {
        "modo": pygame.Rect(152, 145, 150, 36),
        "mapa": pygame.Rect(152, 201, 150, 36),
        "algoritmo": pygame.Rect(152, 257, 150, 36),
        "menos_agentes": pygame.Rect(151, 324, 42, 36),
        "mas_agentes": pygame.Rect(244, 324, 42, 36),
        "k": pygame.Rect(152, 396, 150, 36),
        "pared": pygame.Rect(152, 452, 150, 36),
        "menos_velocidad": pygame.Rect(151, 519, 42, 36),
        "mas_velocidad": pygame.Rect(244, 519, 42, 36),
        "menos_iter": pygame.Rect(151, 519, 42, 36),
        "mas_iter": pygame.Rect(244, 519, 42, 36),
        "accion": pygame.Rect(38, 660, 180, 38),
        "pausa": pygame.Rect(228, 660, 74, 38),
    }
    progreso = None
    resultados = []
    mensaje = ""
    benchmark_ocupado = False
    sim_activa = False
    pausada = False
    sim_finalizada = False
    gestor = None
    marco = None
    resultado_sim = None
    inicio_sim = 0.0
    duracion_sim = 0.0

    ejecutando = True
    while ejecutando:
        while True:
            try:
                tipo, datos = eventos.get_nowait()
            except queue.Empty:
                break
            if tipo == "progreso":
                progreso = datos
            elif tipo == "resultado":
                resultados.append(datos)
            elif tipo == "terminado":
                benchmark_ocupado = False
                mensaje = f"Benchmark finalizado en {formato_duracion(datos['transcurrido'])}."
            elif tipo == "cancelado":
                benchmark_ocupado = False
                resultados = datos
                mensaje = "Benchmark cancelado."
            elif tipo == "error":
                benchmark_ocupado = False
                mensaje = f"Error: {datos}"

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
                cancelacion.set()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                ejecutando = False
                cancelacion.set()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE and sim_activa:
                pausada = not pausada
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                p = evento.pos
                ocupado = benchmark_ocupado or sim_activa
                if (modo == "Simulación" and sim_activa
                        and botones["accion"].collidepoint(p)):
                    sim_activa = False
                    pausada = False
                    sim_finalizada = True
                    duracion_sim = time.perf_counter() - inicio_sim
                    resultado_sim = gestor.obtener_resultados()
                    mensaje = "Simulación terminada manualmente; se muestran sus métricas parciales."
                    marco = capturar_estado(gestor, MAPAS[mapa_idx][0],
                                            ALGORITMOS[algoritmo_idx][0])
                elif botones["modo"].collidepoint(p) and not ocupado:
                    modo = "Benchmark" if modo == "Simulación" else "Simulación"
                    if modo == "Simulación" and mapa_idx >= len(MAPAS):
                        mapa_idx = 0
                    max_agentes = maximo_agentes(mapa_idx, modo, len(MAPAS))
                    agentes = min(agentes, max_agentes)
                    mensaje = ""
                elif botones["mapa"].collidepoint(p) and not ocupado:
                    cantidad = len(MAPAS) if modo == "Benchmark" else len(MAPAS)
                    mapa_idx = (mapa_idx + 1) % (cantidad + (1 if modo == "Benchmark" else 0))
                    max_agentes = maximo_agentes(mapa_idx if mapa_idx < len(MAPAS) else 0,
                                                modo, mapa_idx)
                    agentes = min(agentes, max_agentes)
                elif botones["algoritmo"].collidepoint(p) and modo == "Simulación" and not ocupado:
                    algoritmo_idx = (algoritmo_idx + 1) % len(ALGORITMOS)
                elif botones["menos_agentes"].collidepoint(p) and not ocupado:
                    agentes = max(1, agentes - 5)
                elif botones["mas_agentes"].collidepoint(p) and not ocupado:
                    agentes = min(max_agentes, agentes + 5, LIMITE_AGENTES)
                elif botones["k"].collidepoint(p) and not ocupado:
                    k_idx = (k_idx + 1) % len(VALORES_K)
                elif botones["pared"].collidepoint(p) and not ocupado:
                    pared_idx = (pared_idx + 1) % len(PROBABILIDADES_PARED)
                elif modo == "Simulación" and botones["menos_velocidad"].collidepoint(p) and not ocupado:
                    velocidades_idx = max(0, velocidades_idx - 1)
                elif modo == "Simulación" and botones["mas_velocidad"].collidepoint(p) and not ocupado:
                    velocidades_idx = min(len(VELOCIDADES) - 1, velocidades_idx + 1)
                elif modo == "Benchmark" and botones["menos_iter"].collidepoint(p) and not ocupado:
                    iter_idx = max(0, iter_idx - 1)
                elif modo == "Benchmark" and botones["mas_iter"].collidepoint(p) and not ocupado:
                    iter_idx = min(len(ITERACIONES) - 1, iter_idx + 1)
                elif botones["pausa"].collidepoint(p) and sim_activa:
                    pausada = not pausada
                elif botones["accion"].collidepoint(p) and not ocupado:
                    if modo == "Simulación":
                        try:
                            gestor = crear_gestor(mapa_idx, algoritmo_idx, agentes,
                                                  VALORES_K[k_idx], PROBABILIDADES_PARED[pared_idx])
                        except Exception as error:
                            mensaje = f"Error: {error}"
                        else:
                            resultado_sim = None
                            sim_activa = True
                            pausada = False
                            sim_finalizada = False
                            mensaje = "Simulación en curso."
                            inicio_sim = time.perf_counter()
                            duracion_sim = 0.0
                            mensaje_nombre_mapa = MAPAS[mapa_idx][0]
                            mensaje_nombre_algoritmo = ALGORITMOS[algoritmo_idx][0]
                            marco = capturar_estado(gestor, mensaje_nombre_mapa,
                                                    mensaje_nombre_algoritmo)
                    else:
                        resultados.clear()
                        progreso = None
                        mensaje = "Benchmark en ejecución sin animación."
                        cancelacion.clear()
                        benchmark_ocupado = True
                        mapa_benchmark = "Todos" if mapa_idx == len(MAPAS) else mapa_idx
                        configuracion = {
                            "mapa": mapa_benchmark,
                            "iteraciones": ITERACIONES[iter_idx],
                            "k": VALORES_K[k_idx],
                            "agentes": min(agentes, LIMITE_AGENTES),
                            "prob_pared": PROBABILIDADES_PARED[pared_idx],
                        }
                        threading.Thread(target=ejecutar_benchmark_seguro,
                                         args=(configuracion, eventos, cancelacion),
                                         daemon=True).start()

        if sim_activa and not pausada and gestor is not None:
            if not gestor.simulacion_terminada() and gestor.turnos_totales < LIMITE_TURNOS:
                gestor.ejecutar_turno()
            if gestor.simulacion_terminada() or gestor.turnos_totales >= LIMITE_TURNOS:
                sim_activa = False
                sim_finalizada = True
                pausada = False
                duracion_sim = time.perf_counter() - inicio_sim
                resultado_sim = gestor.obtener_resultados()
                mensaje = ("Simulación finalizada." if gestor.simulacion_terminada()
                           else f"Límite de {LIMITE_TURNOS} turnos alcanzado.")
            marco = capturar_estado(gestor, MAPAS[mapa_idx][0],
                                    ALGORITMOS[algoritmo_idx][0])

        ocupado = benchmark_ocupado or sim_activa
        mapa_etiqueta = "Todos" if modo == "Benchmark" and mapa_idx == len(MAPAS) else MAPAS[min(mapa_idx, len(MAPAS)-1)][0]
        config_ui = {
            "modo": modo, "mapa": mapa_etiqueta,
            "algoritmo": ALGORITMOS[algoritmo_idx][0],
            "agentes": agentes, "max_agentes": max_agentes,
            "k": VALORES_K[k_idx], "prob_pared": PROBABILIDADES_PARED[pared_idx],
            "velocidad": VELOCIDADES[velocidades_idx],
            "iteraciones": ITERACIONES[iter_idx],
        }
        estado = {
            "config": config_ui, "botones": botones, "ocupado": ocupado,
            "progreso": progreso, "resultados": resultados, "mensaje": mensaje,
            "sim_activa": sim_activa, "pausada": pausada,
            "sim_finalizada": sim_finalizada,
            "marco": marco,
            "resultado_sim": resultado_sim,
            "fallecidos": sum(a.fallecido for a in gestor.agentes) if gestor else 0,
            "duracion_sim": duracion_sim,
            "mapa_nombre": MAPAS[mapa_idx][0],
            "algoritmo_nombre": ALGORITMOS[algoritmo_idx][0],
        }
        dibujar_pantalla(pantalla, fuentes, estado)
        reloj.tick(VELOCIDADES[velocidades_idx] if modo == "Simulación" else 30)

    pygame.quit()


if __name__ == "__main__":
    main()
