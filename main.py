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
        self.root.title("Sistema de Optimización de Rutas Logísticas")
        self.root.geometry("130x550")
        self.root.minsize(1000, 600)
        
        # Variable de estado para el zoom de las gráficas
        self.zoomed = False
        self.posiciones_originales = {} # NUEVO: Para guardar las posiciones exactas
        
        # Estilos
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TButton", font=("Arial", 11, "bold"))
        
        # Panel Izquierdo (Controles)
        self.panel_izquierdo = tk.Frame(root, width=300, bg="#f0f0f0", padx=15, pady=15)
        self.panel_izquierdo.pack(side="left", fill="y")
        
        # Panel Derecho (Gráficas)
        self.panel_derecho = tk.Frame(root, bg="white")
        self.panel_derecho.pack(side="right", fill="both", expand=True)

        # Configurar figura incrustada y habilitar el clic
        self.fig = plt.Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.panel_derecho)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # EVENTO: Escuchar los clics del mouse sobre las gráficas
        self.canvas.mpl_connect('button_press_event', self.on_click_grafica)
        
        self.construir_controles()

    def construir_controles(self):
        # Título Controles
        tk.Label(self.panel_izquierdo, text="⚙️ Panel de Control", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=(0, 20))
        
        # Formulario
        ttk.Label(self.panel_izquierdo, text="Número de Ciudades (5-50):", background="#f0f0f0").pack(anchor="w")
        self.n_ciudades = tk.IntVar(value=15)
        ttk.Entry(self.panel_izquierdo, textvariable=self.n_ciudades).pack(fill="x", pady=(0, 15))
        
        ttk.Label(self.panel_izquierdo, text="Iteraciones SA (100-10000):", background="#f0f0f0").pack(anchor="w")
        self.iters = tk.IntVar(value=3000)
        ttk.Entry(self.panel_izquierdo, textvariable=self.iters).pack(fill="x", pady=(0, 15))
        
        ttk.Label(self.panel_izquierdo, text="Seleccionar Acción:", background="#f0f0f0").pack(anchor="w")
        self.accion = tk.StringVar(value="Comparar Heurística vs Metaheurística")
        acciones = ['Dijkstra (A -> B)', 'Comparar Heurística vs Metaheurística', 'Experimento Masivo']
        ttk.Combobox(self.panel_izquierdo, textvariable=self.accion, values=acciones, state="readonly").pack(fill="x", pady=(0, 25))
        
        # Botón Ejecutar
        self.btn_ejecutar = ttk.Button(self.panel_izquierdo, text="▶ Ejecutar Simulación", command=self.ejecutar)
        self.btn_ejecutar.pack(fill="x", ipady=5)
        
        # Consola de Resultados
        tk.Label(self.panel_izquierdo, text="📊 Resultados:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(30, 5))
        self.texto_resultados = tk.Text(self.panel_izquierdo, height=12, width=30, font=("Consolas", 10), state="disabled", bg="#ffffff")
        self.texto_resultados.pack(fill="both", expand=True)

    def log(self, mensaje):
        """Escribe en la consola de resultados"""
        self.texto_resultados.config(state="normal")
        self.texto_resultados.insert("end", mensaje + "\n")
        self.texto_resultados.see("end")
        self.texto_resultados.config(state="disabled")

    def on_click_grafica(self, event):
        """Maneja el zoom in / zoom out al hacer clic en un panel"""
        # Si hizo clic fuera de un área de dibujo o solo hay una gráfica visible, ignorar
        if event.inaxes is None or len(self.fig.axes) <= 1:
            return

        if not self.zoomed:
            # === ZOOM IN ===
            self.zoomed = True
            
            # 1. GUARDAR LAS POSICIONES ORIGINALES AQUI
            self.posiciones_originales = {}
            for ax in self.fig.axes:
                self.posiciones_originales[ax] = ax.get_position()
                
            for ax in self.fig.axes:
                if ax != event.inaxes:
                    ax.set_visible(False) # Ocultar las gráficas que no se clickearon
                    
            # Expandir la gráfica seleccionada
            event.inaxes.set_position([0.08, 0.1, 0.85, 0.85])
        else:
            # === ZOOM OUT ===
            self.zoomed = False
            for ax in self.fig.axes:
                ax.set_visible(True) # Volver a mostrar todas
                # 2. RESTAURAR LA POSICIÓN EXACTA ORIGINAL
                ax.set_position(self.posiciones_originales[ax])
                            
        self.canvas.draw()

    def ejecutar(self):
        try:
            n = int(self.n_ciudades.get())
            iters = int(self.iters.get())
            accion = self.accion.get()
            if not (5 <= n <= 50): raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa valores numéricos válidos (Ciudades: 5-50).")
            return

        self.texto_resultados.config(state="normal")
        self.texto_resultados.delete(1.0, "end")
        self.texto_resultados.config(state="disabled")
        
        self.log("⏳ Calculando...")
        self.root.update()
        
        # Limpiar figura y estado de zoom
        self.zoomed = False
        self.fig.clf()

        try:
            if accion == 'Dijkstra (A -> B)':
                grafo = GrafoLogistica(n_ciudades=n, semilla=random.randint(1,1000))
                origen, destino = 0, n-1
                dists, preds, _ = dijkstra(grafo, origen, destino)
                ruta = reconstruir_ruta(preds, origen, destino)
                
                ax = self.fig.add_subplot(111)
                grafo.visualizar(ax, ruta, titulo=f"Dijkstra: {origen} -> {destino} ({dists[destino]:.2f} km)", color_ruta='blue')
                self.log(f"Distancia Óptima:\n{dists[destino]:.2f} km")

            elif accion == 'Comparar Heurística vs Metaheurística':
                grafo = GrafoLogistica(n_ciudades=n, semilla=random.randint(1,1000))
                ruta_nn, dist_nn = nearest_neighbor_tsp(grafo)
                ruta_sa, dist_sa, hist_dist, hist_temp = simulated_annealing_tsp(grafo, iteraciones_max=iters)
                
                mejora = ((dist_nn - dist_sa)/dist_nn)*100
                
                ax1 = self.fig.add_subplot(221)
                ax2 = self.fig.add_subplot(222)
                ax3 = self.fig.add_subplot(223)
                ax4 = self.fig.add_subplot(224)
                
                grafo.visualizar(ax1, ruta_nn, titulo=f"Nearest Neighbor: {dist_nn:.2f} km", color_ruta='green')
                grafo.visualizar(ax2, ruta_sa, titulo=f"Simulated Annealing: {dist_sa:.2f} km", color_ruta='red')
                
                x_iters = [i * 50 for i in range(len(hist_dist))]
                ax3.plot(x_iters, hist_dist, color='red', linewidth=2)
                ax3.axhline(y=dist_nn, color='green', linestyle='--', label=f'NN: {dist_nn:.1f}')
                ax3.set_xlabel('Iteración')
                ax3.set_ylabel('Distancia (km)')
                ax3.set_title('Convergencia SA')
                ax3.legend()
                
                ax4.plot(x_iters, hist_temp, color='orange', linewidth=2)
                ax4.set_xlabel('Iteración')
                ax4.set_ylabel('Temperatura')
                ax4.set_title('Enfriamiento')
                
                self.log(f"Heurística (NN):\n{dist_nn:.2f} km\n")
                self.log(f"Metaheurística (SA):\n{dist_sa:.2f} km\n")
                self.log(f"¡Mejora obtenida!\n{mejora:.2f}%")
                self.log("\n(Haz clic en cualquier\ngráfica para ampliarla)")

            elif accion == 'Experimento Masivo':
                tamanos = [5, 10, 15, 20]
                dist_nn, dist_sa, t_nn, t_sa = [], [], [], []
                
                for size in tamanos:
                    grafo_exp = GrafoLogistica(n_ciudades=size, semilla=123)
                    
                    t0 = time.time()
                    _, d_nn = nearest_neighbor_tsp(grafo_exp)
                    t_nn.append((time.time() - t0) * 1000)
                    dist_nn.append(d_nn)
                    
                    t0 = time.time()
                    _, d_sa, _, _ = simulated_annealing_tsp(grafo_exp, iteraciones_max=max(1000, size*200))
                    t_sa.append((time.time() - t0) * 1000)
                    dist_sa.append(d_sa)

                ax1 = self.fig.add_subplot(131)
                ax2 = self.fig.add_subplot(132)
                ax3 = self.fig.add_subplot(133)
                
                x = np.arange(len(tamanos))
                width = 0.35

                ax1.bar(x - width/2, dist_nn, width, label='Nearest Neighbor', color='steelblue')
                ax1.bar(x + width/2, dist_sa, width, label='Simulated Annealing', color='salmon')
                ax1.set_xlabel('N° Ciudades')
                ax1.set_ylabel('Distancia total (km)')
                ax1.set_title('Distancias')
                ax1.set_xticks(x)
                ax1.set_xticklabels(tamanos)
                ax1.legend()

                ax2.plot(tamanos, t_nn, 'o-', color='steelblue', label='Nearest Neighbor')
                ax2.plot(tamanos, t_sa, 's-', color='salmon', label='Simulated Annealing')
                ax2.set_xlabel('N° Ciudades')
                ax2.set_ylabel('Tiempo (ms)')
                ax2.set_title('Complejidad Temporal')
                ax2.legend()

                mejoras = [((d_nn - d_sa) / d_nn * 100) if d_nn > 0 else 0 for d_nn, d_sa in zip(dist_nn, dist_sa)]
                colores = ['green' if m > 0 else 'red' for m in mejoras]
                bars = ax3.bar(tamanos, mejoras, color=colores)
                ax3.axhline(y=0, color='black', linewidth=1)
                ax3.set_xlabel('N° Ciudades')
                ax3.set_ylabel('Mejora (%)')
                ax3.set_title('Mejora vs Heurística')
                for bar, val in zip(bars, mejoras):
                    ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1, f'{val:.1f}%', ha='center', va='bottom')

                self.fig.suptitle('Análisis Comparativo y Escalabilidad', fontweight='bold')
                self.log("Experimento Finalizado.\n\n(Haz clic en cualquier\ngráfica para ampliarla)")

            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error en la simulación:\n{str(e)}")
            self.log("❌ Error en ejecución.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogisticaApp(root)
    root.mainloop()