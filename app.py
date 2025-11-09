from flask import Flask, render_template, jsonify, request
import osmnx as ox
import random
import heapq
import pickle
import os
import os.path

app = Flask(__name__)

G = None

def load_graph():
    global G
    city = "Istanbul, Turkey"
    cache = "istanbul_graph.pkl"
    
    if os.path.exists(cache):
        print("Loading map data...")
        f = open(cache, 'rb')
        G = pickle.load(f)
        f.close()
        print("Done loading map")
    else:
        print("Downloading map (this takes a while)...")
        G = ox.graph_from_place(city, network_type="drive")
        f = open(cache, 'wb')
        pickle.dump(G, f)
        f.close()
        print("Map downloaded and saved")
    
    print("Processing roads...")
    for edge in G.edges:
        speed = 40
        if "maxspeed" in G.edges[edge]:
            try:
                s = G.edges[edge]["maxspeed"]
                if type(s) == list:
                    speed = int(s[0])
                else:
                    speed = int(s)
            except:
                speed = 40
        G.edges[edge]["maxspeed"] = speed
        G.edges[edge]["weight"] = G.edges[edge]["length"] / speed
    
    print(f"Total nodes: {len(G.nodes)}")
    print(f"Total edges: {len(G.edges)}")
    print("Ready!")

load_graph()

os.makedirs("static/output", exist_ok=True)

def color_unvisited(edge):        
    G.edges[edge]["color"] = "#d36206"
    G.edges[edge]["alpha"] = 0.2
    G.edges[edge]["linewidth"] = 0.5

def color_visited(edge):
    G.edges[edge]["color"] = "#d36206"
    G.edges[edge]["alpha"] = 1
    G.edges[edge]["linewidth"] = 1

def color_active(edge):
    G.edges[edge]["color"] = '#e8a900'
    G.edges[edge]["alpha"] = 1
    G.edges[edge]["linewidth"] = 1

def color_path(edge):
    G.edges[edge]["color"] = "white"
    G.edges[edge]["alpha"] = 1
    G.edges[edge]["linewidth"] = 1

def save_map(path):
    node_sizes = []
    edge_colors = []
    edge_alphas = []
    edge_widths = []
    
    for node in G.nodes:
        node_sizes.append(G.nodes[node]["size"])
    
    for edge in G.edges:
        edge_colors.append(G.edges[edge]["color"])
        edge_alphas.append(G.edges[edge]["alpha"])
        edge_widths.append(G.edges[edge]["linewidth"])
    
    fig, ax = ox.plot_graph(G, node_size=node_sizes, edge_color=edge_colors, 
                            edge_alpha=edge_alphas, edge_linewidth=edge_widths,
                            node_color="white", bgcolor="#18080e", show=False, close=False)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='#18080e')
    
    import matplotlib.pyplot as plt
    plt.close(fig)

def distance(node1, node2):
    x1, y1 = G.nodes[node1]["x"], G.nodes[node1]["y"]
    x2, y2 = G.nodes[node2]["x"], G.nodes[node2]["y"]
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

def dijkstra(start, end, saveto=None):
    for node in G.nodes:
        G.nodes[node]["visited"] = False
        G.nodes[node]["distance"] = float("inf")
        G.nodes[node]["previous"] = None
        G.nodes[node]["size"] = 0
    
    for edge in G.edges:
        color_unvisited(edge)
    
    G.nodes[start]["distance"] = 0
    G.nodes[start]["size"] = 50
    G.nodes[end]["size"] = 50
    
    queue = [(0, start)]
    iterations = 0
    
    while queue:
        current_dist, current = heapq.heappop(queue)
        
        if current == end:
            if saveto:
                save_map(saveto)
            return iterations
        
        if G.nodes[current]["visited"]:
            continue
            
        G.nodes[current]["visited"] = True
        
        for edge in G.out_edges(current):
            color_visited((edge[0], edge[1], 0))
            neighbor = edge[1]
            w = G.edges[(edge[0], edge[1], 0)]["weight"]
            
            new_dist = G.nodes[current]["distance"] + w
            if new_dist < G.nodes[neighbor]["distance"]:
                G.nodes[neighbor]["distance"] = new_dist
                G.nodes[neighbor]["previous"] = current
                heapq.heappush(queue, (new_dist, neighbor))
                
                for e in G.out_edges(neighbor):
                    color_active((e[0], e[1], 0))
        
        iterations += 1
    
    return iterations

def a_star(start, end, saveto=None):
    for node in G.nodes:
        G.nodes[node]["previous"] = None
        G.nodes[node]["size"] = 0
        G.nodes[node]["g_score"] = float("inf")
        G.nodes[node]["f_score"] = float("inf")
    
    for edge in G.edges:
        color_unvisited(edge)
    
    G.nodes[start]["size"] = 50
    G.nodes[end]["size"] = 50
    G.nodes[start]["g_score"] = 0
    G.nodes[start]["f_score"] = distance(start, end)
    
    queue = [(G.nodes[start]["f_score"], start)]
    iterations = 0
    
    while queue:
        f_val, current = heapq.heappop(queue)
        
        if current == end:
            if saveto:
                save_map(saveto)
            return iterations
        
        for edge in G.out_edges(current):
            color_visited((edge[0], edge[1], 0))
            neighbor = edge[1]
            new_g = G.nodes[current]["g_score"] + distance(current, neighbor)
            
            if new_g < G.nodes[neighbor]["g_score"]:
                G.nodes[neighbor]["previous"] = current
                G.nodes[neighbor]["g_score"] = new_g
                G.nodes[neighbor]["f_score"] = new_g + distance(neighbor, end)
                heapq.heappush(queue, (G.nodes[neighbor]["f_score"], neighbor))
                
                for e in G.out_edges(neighbor):
                    color_active((e[0], e[1], 0))
        
        iterations += 1
    
    return iterations

def get_path_info(start, end, saveto=None):
    for edge in G.edges:
        color_unvisited(edge)
    
    total_dist = 0
    speeds = []
    current = end
    
    while current != start:
        prev = G.nodes[current]["previous"]
        total_dist += G.edges[(prev, current, 0)]["length"]
        speeds.append(G.edges[(prev, current, 0)]["maxspeed"])
        color_path((prev, current, 0))
        current = prev
    
    dist_km = total_dist / 1000
    avg_spd = sum(speeds) / len(speeds) if speeds else 40
    time_mins = (dist_km / avg_spd) * 60 if avg_spd > 0 else 0
    
    if saveto:
        save_map(saveto)
    
    return dist_km, avg_spd, time_mins

LOCATIONS = {
    "1": ("Taksim Square", 41.0369, 28.9850),
    "2": ("Sultanahmet (Blue Mosque)", 41.0055, 28.9769),
    "3": ("Galata Tower", 41.0256, 28.9744),
    "4": ("Grand Bazaar", 41.0106, 28.9680),
    "5": ("Hagia Sophia", 41.0086, 28.9802),
    "6": ("Topkapi Palace", 41.0115, 28.9833),
    "7": ("Eminonu Ferry Port", 41.0174, 28.9736),
    "8": ("Besiktas", 41.0422, 28.9895),
    "9": ("Kadikoy", 40.9889, 29.0258),
    "10": ("Ortakoy", 41.0553, 29.0264),
    "11": ("Balat", 41.0297, 28.9484),
    "12": ("Fatih Mosque", 41.0195, 28.9500),
    "13": ("Suleymaniye Mosque", 41.0165, 28.9639),
    "14": ("Dolmabahce Palace", 41.0391, 29.0003),
    "15": ("Istiklal Street", 41.0338, 28.9780),
    "16": ("Bakirkoy (Far West - European)", 40.9833, 28.8667),
    "17": ("Atakoy (West Coast - European)", 40.9764, 28.8744),
    "18": ("Uskudar (Asian Side)", 41.0225, 29.0100),
    "19": ("Umraniye (Far East - Asian)", 41.0186, 29.1150),
    "20": ("Pendik (Very Far East - Asian)", 40.8764, 29.2333),
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compute', methods=['POST'])
def compute_route():
    data = request.json
    origin_id = data.get('origin')
    dest_id = data.get('destination')
    
    if origin_id == 'R':
        start = random.choice(list(G.nodes))
        start_name = f"Random ({G.nodes[start]['y']:.4f}, {G.nodes[start]['x']:.4f})"
    elif origin_id == 'C':
        lat = float(data.get('origin_lat'))
        lon = float(data.get('origin_lon'))
        start = ox.distance.nearest_nodes(G, X=lon, Y=lat)
        start_name = f"Custom ({lat:.4f}, {lon:.4f})"
    else:
        name, lat, lon = LOCATIONS[origin_id]
        start = ox.distance.nearest_nodes(G, X=lon, Y=lat)
        start_name = name
    
    if dest_id == 'R':
        end = random.choice(list(G.nodes))
        end_name = f"Random ({G.nodes[end]['y']:.4f}, {G.nodes[end]['x']:.4f})"
    elif dest_id == 'C':
        lat = float(data.get('dest_lat'))
        lon = float(data.get('dest_lon'))
        end = ox.distance.nearest_nodes(G, X=lon, Y=lat)
        end_name = f"Custom ({lat:.4f}, {lon:.4f})"
    else:
        name, lat, lon = LOCATIONS[dest_id]
        end = ox.distance.nearest_nodes(G, X=lon, Y=lat)
        end_name = name
    
    print(f"\nFinding route from {start_name} to {end_name}")
    
    print("Running Dijkstra...")
    dijkstra_steps = dijkstra(start, end, saveto="static/output/dijkstra_exploration.png")
    print("Done")
    
    dist_d, speed_d, time_d = get_path_info(start, end, saveto="static/output/dijkstra_path.png")
    print("Dijkstra finished")
    
    print("Running A*...")
    astar_steps = a_star(start, end, saveto="static/output/astar_exploration.png")
    print("Done")
    
    dist_a, speed_a, time_a = get_path_info(start, end, saveto="static/output/astar_path.png")
    print("A* finished")
    
    print("All complete!")
    
    return jsonify({
        'success': True,
        'route': f"{start_name} → {end_name}",
        'dijkstra': {
            'iterations': dijkstra_steps,
            'distance': f"{dist_d:.2f} km",
            'time': f"{time_d:.2f} min"
        },
        'astar': {
            'iterations': astar_steps,
            'distance': f"{dist_a:.2f} km",
            'time': f"{time_a:.2f} min"
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
