# 🗺️ Sistema de Optimización de Rutas Logísticas

Sistema de escritorio desarrollado en Python para modelar y resolver el Problema del Agente Viajero (TSP) aplicado a redes logísticas. El sistema contrasta la eficiencia de diferentes enfoques algorítmicos vistos en la teoría de diseño de algoritmos.

## 🧠 Algoritmos Implementados
* **Algoritmo Exacto:** Camino mínimo punto a punto utilizando **Dijkstra** (con Cola de Prioridad/Min-Heap).
* **Heurística Constructiva:** Búsqueda rápida mediante el algoritmo voraz **Vecino Más Cercano (Nearest Neighbor)**.
* **Metaheurística Estocástica:** Optimización global mediante **Recocido Simulado (Simulated Annealing)** con operador de intercambio 2-opt.

## 🗂️ Estructura del Proyecto
* `main.py`: Contiene el modelado de grafos matemáticos, los motores algorítmicos, el análisis de convergencia y la interfaz gráfica basada en Tkinter.
* `requirements.txt`: Lista de dependencias matemáticas y de graficación necesarias para ejecutar el sistema.
* `README.md`: Documentación e instrucciones operativas.

## 🚀 Instrucciones de Instalación

1. **Clonar o descargar el proyecto:**
   Abre la carpeta del proyecto en Visual Studio Code.

2. **Abrir la terminal:**
   Abre una nueva terminal integrada en VS Code navegando a `Terminal > New Terminal` o presiona Ctrl + ñ dentro de VS Code.

3. **Instalar las dependencias:**
   Ejecuta el siguiente comando para instalar las librerías necesarias (como matplotlib y networkx):
   ```bash
   pip install -r requirements.txt
4. **Ejecucion del proyecto:**
   Ejecuta el siguiente comando para insialisar el archivo main.py:
    ```bash
    python main.py
## 🎮 Uso de la Interfaz
Al ejecutar main.py, se abrirá una ventana de controles:

1. Define el Número de Ciudades (el tamaño del grafo a generar).

2. Ajusta las Iteraciones SA (cuántos ciclos de temperatura correrá el Recocido Simulado).

3. Selecciona la Acción en el menú desplegable (Ruta exacta, Comparativa heurística o Experimento Masivo).

4. Haz clic en Ejecutar Simulación. Las ventanas interactivas con las gráficas de red y desempeño se abrirán automáticamente. Cierra las gráficas para evaluar una nueva simulación.