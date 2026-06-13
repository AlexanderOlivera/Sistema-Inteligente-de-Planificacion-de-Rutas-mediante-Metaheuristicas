import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import random
import time
import math
import heapq
from collections import defaultdict
import tkinter as tk
from tkinter import ttk, messagebox
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# MODELADO DEL GRAFO
# ==========================================
class GrafoLogistica:
    def __init__(self, n_ciudades, semilla=42):
        self.n = n_ciudades
        random.seed(semilla)
        np.random.seed(semilla)
        
        self.coordenadas = {i: (random.uniform(0, 100), random.uniform(0, 100)) for i in range(n_ciudades)}
        self.nombres = {i: f"Ciudad {i}" for i in range(n_ciudades)}
        self._construir_grafo()
    
    def _distancia_euclidiana(self, i, j):
        x1, y1 = self.coordenadas[i]
        x2, y2 = self.coordenadas[j]
        return round(math.sqrt((x2 - x1)**2 + (y2 - y1)**2), 2)
    
    def _construir_grafo(self):
        INF = float('inf')
        self.matriz = [[INF] * self.n for _ in range(self.n)]
        for i in range(self.n): self.matriz[i][i] = 0
        
        self.lista_ady = defaultdict(list)
        self.G = nx.Graph()
        for i in range(self.n):
            self.G.add_node(i, pos=self.coordenadas[i], label=self.nombres[i])
            
        aristas_creadas = set()
        for i in range(self.n):
            vecinos_posibles = list(range(self.n))
            vecinos_posibles.remove(i)
            n_conexiones = random.randint(max(2, self.n // 3), min(self.n - 1, max(3, self.n * 2 // 3)))
            vecinos_seleccionados = random.sample(vecinos_posibles, min(n_conexiones, len(vecinos_posibles)))
            
            for j in vecinos_seleccionados:
                if (i, j) not in aristas_creadas and (j, i) not in aristas_creadas:
                    dist = self._distancia_euclidiana(i, j)
                    self.matriz[i][j] = self.matriz[j][i] = dist
                    self.lista_ady[i].append((j, dist))
                    self.lista_ady[j].append((i, dist))
                    self.G.add_edge(i, j, weight=dist)
                    aristas_creadas.add((i, j))
        self._garantizar_conectividad()

    def _garantizar_conectividad(self):
        componentes = list(nx.connected_components(self.G))
        while len(componentes) > 1:
            i, j = random.choice(list(componentes[0])), random.choice(list(componentes[1]))
            dist = self._distancia_euclidiana(i, j)
            self.matriz[i][j] = self.matriz[j][i] = dist
            self.lista_ady[i].append((j, dist))
            self.lista_ady[j].append((i, dist))
            self.G.add_edge(i, j, weight=dist)
            componentes = list(nx.connected_components(self.G))

    def visualizar(self, ax, ruta=None, titulo="Red Logística", color_ruta='red'):
        pos = nx.get_node_attributes(self.G, 'pos')
        nx.draw_networkx_edges(self.G, pos, alpha=0.3, edge_color='gray', width=1, ax=ax)
        nx.draw_networkx_nodes(self.G, pos, node_color='steelblue', node_size=300, ax=ax)
        nx.draw_networkx_labels(self.G, pos, font_size=8, font_color='white', font_weight='bold', ax=ax)
        
        if ruta and len(ruta) > 1:
            aristas_ruta = [(ruta[k], ruta[k+1]) for k in range(len(ruta)-1)]
            nx.draw_networkx_edges(self.G, pos, edgelist=aristas_ruta, edge_color=color_ruta, width=2, arrows=True, ax=ax)
            nx.draw_networkx_nodes(self.G, pos, nodelist=ruta, node_color='orange', node_size=400, ax=ax)
            
        if self.n <= 15:
            edge_labels = nx.get_edge_attributes(self.G, 'weight')
            edge_labels = {k: f"{v:.0f}" for k, v in edge_labels.items()}
            nx.draw_networkx_edge_labels(self.G, pos, edge_labels, font_size=7, ax=ax)
            
        ax.set_title(titulo, fontsize=12, fontweight='bold')
        ax.axis('off')

# ==========================================
# ALGORITMOS
# ==========================================
def dijkstra(grafo, origen, destino=None):
    INF = float('inf')
    distancias = {i: INF for i in range(grafo.n)}
    distancias[origen] = 0
    predecesores = {i: None for i in range(grafo.n)}
    heap = [(0, origen)]
    visitados = set()
    iteraciones = 0
    
    while heap:
        dist_actual, nodo_actual = heapq.heappop(heap)
        iteraciones += 1
        if nodo_actual in visitados: continue
        visitados.add(nodo_actual)
        if destino is not None and nodo_actual == destino: break
            
        for vecino, peso in grafo.lista_ady[nodo_actual]:
            if vecino not in visitados:
                nueva_dist = dist_actual + peso
                if nueva_dist < distancias[vecino]:
                    distancias[vecino] = nueva_dist
                    predecesores[vecino] = nodo_actual
                    heapq.heappush(heap, (nueva_dist, vecino))
    return distancias, predecesores, iteraciones

def reconstruir_ruta(predecesores, origen, destino):
    ruta, nodo = [], destino
    while nodo is not None:
        ruta.append(nodo)
        nodo = predecesores[nodo]
    ruta.reverse()
    return ruta if ruta[0] == origen else []

def nearest_neighbor_tsp(grafo, inicio=0):
    n = grafo.n
    visitados = [False] * n
    ruta = [inicio]
    visitados[inicio] = True
    distancia_total = 0
    ciudad_actual = inicio
    
    for _ in range(n - 1):
        mejor_vecino = None
        mejor_distancia = float('inf')
        for ciudad in range(n):
            if not visitados[ciudad]:
                dist = grafo.matriz[ciudad_actual][ciudad]
                if dist < mejor_distancia:
                    mejor_distancia = dist
                    mejor_vecino = ciudad
                    
        if mejor_vecino is None or mejor_distancia == float('inf'):
            distancias_dijkstra, _, _ = dijkstra(grafo, ciudad_actual)
            for ciudad in range(n):
                if not visitados[ciudad] and distancias_dijkstra[ciudad] < mejor_distancia:
                    mejor_distancia = distancias_dijkstra[ciudad]
                    mejor_vecino = ciudad
                    
        ruta.append(mejor_vecino)
        visitados[mejor_vecino] = True
        distancia_total += mejor_distancia
        ciudad_actual = mejor_vecino
        
    dist_regreso = grafo.matriz[ciudad_actual][inicio]
    if dist_regreso == float('inf'):
        dists, _, _ = dijkstra(grafo, ciudad_actual)
        dist_regreso = dists[inicio]
        
    distancia_total += dist_regreso
    ruta.append(inicio)
    return ruta, distancia_total

def calcular_distancia_ruta(grafo, ruta):
    total = 0
    for i in range(len(ruta) - 1):
        d = grafo.matriz[ruta[i]][ruta[i+1]]
        if d == float('inf'):
            dists, _, _ = dijkstra(grafo, ruta[i])
            d = dists[ruta[i+1]]
        total += d
    return total

def simulated_annealing_tsp(grafo, temp_inicial=1000, enfriamiento=0.995, iteraciones_max=3000):
    ruta_inicial, _ = nearest_neighbor_tsp(grafo)
    ruta_actual = ruta_inicial[:-1]
    dist_actual = calcular_distancia_ruta(grafo, ruta_actual + [ruta_actual[0]])
    
    mejor_ruta, mejor_dist = ruta_actual[:], dist_actual
    temperatura = temp_inicial
    historial_distancias, historial_temperaturas = [dist_actual], [temperatura]
    
    for iteracion in range(iteraciones_max):
        i, j = sorted(random.sample(range(grafo.n), 2))
        nueva_ruta = ruta_actual[:]
        nueva_ruta[i], nueva_ruta[j] = nueva_ruta[j], nueva_ruta[i]
        
        nueva_dist = calcular_distancia_ruta(grafo, nueva_ruta + [nueva_ruta[0]])
        delta = nueva_dist - dist_actual
        
        if delta < 0 or random.random() < math.exp(-delta / temperatura):
            ruta_actual = nueva_ruta
            dist_actual = nueva_dist
            if dist_actual < mejor_dist:
                mejor_ruta = ruta_actual[:]
                mejor_dist = dist_actual
                
        temperatura *= enfriamiento
        if iteracion % 50 == 0:
            historial_distancias.append(mejor_dist)
            historial_temperaturas.append(temperatura)
            
    return mejor_ruta + [mejor_ruta[0]], mejor_dist, historial_distancias, historial_temperaturas


# ==========================================
# INTERFAZ GRÁFICA
# ==========================================
class LogisticaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Logístico")
        self.root.geometry("1300x750")
        self.zoomed = False
        self.original_geometry = None # NUEVO: Guardará la cuadrícula nativa de Matplotlib
        
        self.panel_izquierdo = tk.Frame(root, width=300, bg="#f0f0f0", padx=15, pady=15)
        self.panel_izquierdo.pack(side="left", fill="y")
        self.panel_derecho = tk.Frame(root, bg="white")
        self.panel_derecho.pack(side="right", fill="both", expand=True)

        self.fig = plt.Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.panel_derecho)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.mpl_connect('button_press_event', self.on_click_grafica)
        
        ttk.Label(self.panel_izquierdo, text="Ciudades:", background="#f0f0f0").pack(anchor="w")
        self.n_ciudades = tk.IntVar(value=15)
        ttk.Entry(self.panel_izquierdo, textvariable=self.n_ciudades).pack(fill="x", pady=5)
        
        self.accion = tk.StringVar(value="Comparar Heurística vs Metaheurística")
        ttk.Combobox(self.panel_izquierdo, textvariable=self.accion, values=['Dijkstra (A -> B)', 'Comparar Heurística vs Metaheurística'], state="readonly").pack(fill="x", pady=10)
        
        ttk.Button(self.panel_izquierdo, text="▶ Ejecutar", command=self.ejecutar).pack(fill="x", pady=10)
        self.texto_resultados = tk.Text(self.panel_izquierdo, height=10, state="disabled")
        self.texto_resultados.pack(fill="both", expand=True)

    def on_click_grafica(self, event):
        if event.inaxes is None or len(self.fig.axes) <= 1: return
        
        if not self.zoomed:
            self.zoomed = True
            self.clicked_ax = event.inaxes
            
            # SOLUCIÓN: Guardar la estructura de la cuadrícula (ej: 2x2, posición 1)
            self.original_geometry = self.clicked_ax.get_geometry()
            
            # Ocultar las demás gráficas
            for ax in self.fig.axes:
                if ax != self.clicked_ax: ax.set_visible(False)
            
            # Hacer que la seleccionada se comporte como si fuera la única en la ventana (1x1)
            self.clicked_ax.change_geometry(1, 1, 1)
            
        else:
            self.zoomed = False
            
            # Devolverle su comportamiento de cuadrícula original
            self.clicked_ax.change_geometry(*self.original_geometry)
            
            # Mostrar todas
            for ax in self.fig.axes:
                ax.set_visible(True)
                
            # Reacomodar (ahora tight_layout funciona perfecto porque la geometría está intacta)
            self.fig.tight_layout()
            
        self.canvas.draw()

    def ejecutar(self):
        self.zoomed = False
        self.fig.clf()
        n = self.n_ciudades.get()
        accion = self.accion.get()
        grafo = GrafoLogistica(n_ciudades=n, semilla=random.randint(1,1000))
        
        if accion == 'Dijkstra (A -> B)':
            origen, destino = 0, n-1
            _, preds = dijkstra(grafo, origen, destino)
            ruta = reconstruir_ruta(preds, origen, destino)
            ax = self.fig.add_subplot(111)
            grafo.visualizar(ax, ruta, "Dijkstra", 'blue')
        else:
            ruta_nn, dist_nn = nearest_neighbor_tsp(grafo)
            ruta_sa, dist_sa, hist_dist, hist_temp = simulated_annealing_tsp(grafo)
            ax1 = self.fig.add_subplot(221); ax2 = self.fig.add_subplot(222)
            ax3 = self.fig.add_subplot(223); ax4 = self.fig.add_subplot(224)
            grafo.visualizar(ax1, ruta_nn, f"NN: {dist_nn:.2f}km", 'green')
            grafo.visualizar(ax2, ruta_sa, f"SA: {dist_sa:.2f}km", 'red')
            x_iters = [i * 50 for i in range(len(hist_dist))]
            ax3.plot(x_iters, hist_dist, color='red'); ax4.plot(x_iters, hist_temp, color='orange')
        
        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = LogisticaApp(root)
    root.mainloop()