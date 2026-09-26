# Escape de la torre

Simulador de evacuación en una grilla bidimensional. Los agentes deben llegar a una salida mientras el fuego se propaga y la ocupación de los pasillos genera congestión. El proyecto compara búsqueda no informada, búsqueda informada y una metaheurística genética en tres mapas de 50 × 50.

## Algoritmos

- **BFS:** búsqueda en anchura.
- **DFS:** búsqueda en profundidad.
- **A\*:** búsqueda informada con distancia Manhattan y costo de ocupación.
- **IDA\*:** búsqueda informada iterativa con distancia Manhattan, prevención de ciclos, control de estados y un límite de 500 nodos expandidos por búsqueda.
- **Algoritmo genético:** cromosomas de movimientos ortogonales y espera; usa población de 8 individuos, hasta 8 generaciones, cruce de un punto y mutación del 15 %. Una mutación siempre cambia la acción seleccionada. Si no obtiene una ruta factible, el agente usa memoria dispersa de visitas para orientar su movimiento de respaldo y reducir ciclos. Esta memoria se habilita solo para el genético.

## Modelo de simulación

- Los mapas se leen desde archivos de texto: `1` representa un muro, `S` la salida y `A` una posición inicial de agente; las demás celdas se interpretan como transitables.
- Los movimientos son ortogonales. Las celdas tienen capacidad física de 6 agentes; una celda saturada no admite otro agente, salvo la salida. La congestión también se refleja en un costo cuadrático `1 + n²`, donde `n` es la cantidad de agentes en la celda.
- El fuego se propaga cada `k` turnos. La probabilidad de propagación a una celda transitable vecina es 0,75. Puede atravesar muros según el parámetro `p_pared`; para un muro de grosor `d`, la probabilidad utilizada es `p_pared ** d`. Las celdas incendiadas dejan de ser transitables y los agentes que se encuentren en ellas fallecen.
- La posición inicial del fuego y el orden de actuación de los agentes son aleatorios. No se fija una semilla global.
- El número máximo admitido por la interfaz es de 80 agentes, limitado además por las posiciones disponibles en el mapa seleccionado.

## Estructura del proyecto

```text
Tarea1IA/
├── assets/
│   ├── mapa_cuello_botella50x50.txt
│   ├── mapa_corporativo50x50.txt
│   ├── mapa_abierto50x50.txt
│   ├── imágenes de mapas
│   └── scriptmap.py             # Conversión de imagen PNG a mapa TXT
├── Interfaz/
│   └── vista_*.py               # Renderizado Pygame
├── Logica/
│   ├── agente.py                # Movimiento, espera y memoria de respaldo del genético
│   ├── algoritmo_de_busqueda.py # Clase base de los algoritmos
│   ├── bfs.py
│   ├── dfs.py
│   ├── a_estrella.py
│   ├── ida.py
│   ├── algoritmo_genetico.py
│   ├── casilla.py y grilla.py
│   ├── gestor_de_eventos.py     # Turnos, fuego y coordinación de agentes
│   └── lector_de_mapas.py
├── main.py                      # Interfaz Pygame: simulación y benchmark
├── benchmark.py                 # Benchmark por consola
├── INFORME.pdf                  # Informe del proyecto
└── README.md
```

El lector resuelve automáticamente la carpeta `assets/` para los nombres de mapas incluidos. Ejecuta los comandos desde la raíz del proyecto, donde están `main.py` y `benchmark.py`.

## Requisitos e instalación

Se requiere Python 3.10 o posterior, junto con Pygame, NumPy y Pillow (Pillow se utiliza para el conversor de mapas).

```bash
python -m pip install pygame numpy pillow
```

## Ejecución

### Interfaz gráfica

```bash
python main.py
```

La interfaz ofrece dos modos:

- **Simulación:** permite elegir mapa, algoritmo, cantidad de agentes, frecuencia (k), probabilidad de atravesar paredes y velocidad visual. A la izquierda aparecen los controles y a la derecha se muestra el mapa en ejecución; al finalizar, esa zona muestra el resultado y las métricas. Se puede pausar o terminar forzadamente una simulación para iniciar otra. La velocidad inicial es aproximadamente 8 turnos por segundo; los valores iniciales de (k) y (p_{pared}) son 5 y 0 %, respectivamente.
- **Benchmark:** ejecuta repeticiones sin animar cada turno y compara los cinco algoritmos. Permite escoger un mapa o incluirlos todos, y presenta resultados parciales, avance y una estimación del tiempo restante. Las opciones de repeticiones son 1, 5, 10, 25, 50 y 100. Las métricas incluyen supervivencia, turnos de despeje, variabilidad, rango, corridas con despeje definido y tiempo medio de ejecución por repetición.

El tiempo restante del benchmark es una estimación basada en las operaciones recientes. El benchmark visual tiene un límite de 300 turnos por corrida. La finalización forzada está disponible para la simulación visual individual.

### Benchmark por consola

```bash
python benchmark.py
```

El benchmark por consola usa los valores definidos al comienzo de `benchmark.py`: actualmente 200 repeticiones por algoritmo y mapa, `k=3`, probabilidad de propagación normal de 0,75 y probabilidad de atravesar paredes de 0,25. Para comparar `k=3` y `k=4`, cambia `KTURNOS_FUEGO` y ejecuta nuevamente el programa. Cada simulación termina cuando todos los agentes evacuaron o fallecieron, o al alcanzar el límite de 300 turnos.

La tasa de supervivencia corresponde a la proporción de agentes evacuados. Los turnos de despeje se calculan como el turno de evacuación más tardío entre los agentes que evacuaron; las ejecuciones sin agentes evacuados no tienen un tiempo definido y no se incluyen en los estadísticos de despeje. Estos turnos describen el avance de la simulación, no el tiempo de ejecución computacional.

## Uso de IA generativa

Gemini, GitHub Copilot y Codex se utilizaron como herramientas de apoyo durante la implementación y documentación. La implementación inicial de BFS, DFS y A\* fue realizada por el autor; las herramientas apoyaron modificaciones y adaptaciones posteriores ante cambios, errores y problemas de integración. También se utilizaron para apoyar la implementación del algoritmo genético, la corrección de problemas de complejidad temporal de IDA\* y del genético, el desarrollo de la interfaz gráfica, utilitarios de conversión y lectura de mapas, la refactorización, optimización y compatibilidad entre cambios, y aspectos de gestión de eventos.

Las herramientas también apoyaron la redacción y revisión del informe, incluida la corrección de estilo y ortotipográfica, su estructuración en LaTeX y la maquetación de ecuaciones, tablas y figuras. La integración, revisión y adaptación del código al proyecto, así como las decisiones sobre parámetros, estructura de clases, agentes, gestor de eventos, funcionamiento del fuego y configuración experimental, fueron responsabilidad del autor.
