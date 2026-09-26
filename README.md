# Escape de la Torre — Tarea 1, Inteligencia Artificial

Simulación de evacuación de un edificio en llamas. Un grupo de agentes debe alcanzar la
única salida de cada piso antes de ser alcanzado por el fuego o quedar atrapado por
embotellamientos en los pasillos. El proyecto implementa y compara tres paradigmas de
navegación: búsqueda no informada, búsqueda informada y optimización bioinspirada para resolver un problema de evacuación de un edificio en llamas.

## Integrantes

- Leonardo Rafael Guerrero Ortega

## Descripción del Proyecto
El entorno se modela como una grilla bidimensional con obstáculos (muros), una única salida (`S`) y posiciones iniciales para los agentes (`A`).

### Mecánicas Principales:
- **Propagación del Fuego:** Cada $k$ turnos, el fuego (`F`) se propaga de forma estocástica a casillas transitables adyacentes.
- **Congestión y Capacidad:** Las celdas poseen una capacidad máxima física. Si una celda está saturada, el agente ejecuta la acción de **esperar** en su posición actual. Adicionalmente, se aplica una función de penalización cuadrática sobre la ocupación para los algoritmos guiados por costo.
- **Movimiento Discreto:** Movimientos ortogonales (arriba, abajo, izquierda, derecha) y acción de espera.

## Algoritmos implementados

## Algoritmos Implementados
- **Búsqueda No Informada:** BFS (Búsqueda en Anchura) y DFS (Búsqueda en Profundidad).
- **Búsqueda Informada:** A* e IDA* (utilizando la distancia Manhattan como heurística admisible).
- **Metaheurística Bioinspirada:** Algoritmo Genético (con representación de movimientos, selección por elitismo, cruce de un punto y mutación aleatoria).

## Estructura del proyecto y repositorio

```
Tarea1IA/
├── Logica/                     
│   ├── casilla.py              # celda de la grilla
│   ├── grilla.py               # grilla 2D y vecindad
│   ├── agente.py               # lógica de movimiento/espera de cada agente
│   ├── algoritmo_de_busqueda.py # clase base abstracta 
│   ├── bfs.py                  # búsquedas no informadas
│   ├── dfs.py 
│   ├── a_estrella.py           # búsquedas informadas
│   ├── ida.py
│   ├── algoritmo_genetico.py   # metaheurística bioinspirada (AG)
│   ├── gestor_de_eventos.py    # turnos, movimiento de agentes y propagación del fuego
│   └── lector_de_mapas.py      # carga de mapas; resuelve Assets/ automáticamente
├── Interfaz/                    
│   └── vista_*.py               # renderizado (pygame)
├── Assets/
│   ├── mapa_*.txt                # los 3 mapas de prueba
│   ├── Laberinto*.png            # imágenes fuente de los mapas
│   └── scriptmap.py              # utilitario (imagen a txt)
├── README.md
├── INFORME.pdf                    # informe con metodología, resultados y análisis
├── main.py                        # simulación con pygame y benchmark en la interfaz grafica
└── benchmark.py                  # benchmark normal, este es el que se usó para el informe
```
`Logica/` y `Interfaz/` son paquetes Python normales (usan imports relativos entre sí);
`main.py` y `benchmark.py` los importan como `Logica.xxx` / `Interfaz.xxx`, por lo que deben
ejecutarse siempre desde la carpeta `Tarea1IA/`.

## Requisitos

- Python 3.13+
- `pygame`, `numpy`, `pil`

Instalar dependencias:

```bash
pip install pygame numpy pillow
```

## Cómo ejecutar

**Simulación visual** (elige el algoritmo y mapa editando `main.py`, sección `__main__`):

```bash
python main.py
```

**Suite de benchmarking** (80 iteraciones por combinación de mapa/algoritmo, imprime
supervivencia y estadísticas de turnos):

```bash
python benchmark.py
```

## Resultados

Ver el informe para la metodología completa, la tabla de resultados y el
análisis de cada algoritmo.

## Uso de IA generativa

Se utilizó Claude (Anthropic) y Gemini como asistentes para: revisar el código contra el enunciado, diagnosticar si los resultados eran los esperados, implementar el algoritmo genético y ayuda para ida estrella, apoyo en errores específicos, visualización gráfica con pygame y utilitarios para traducir de imagen pixeleada a documento de texto y leer el mapa. 
