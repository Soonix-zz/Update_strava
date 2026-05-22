import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

def generate_myzone_graph(graph_data, output_path):
    """
    Génère un graphique à barres reprenant les couleurs des zones Myzone.
    """
    times = []
    values = []
    colors = []
    
    for point in graph_data:
        try:
            # ex: "2026-04-17 12:23"
            t = datetime.datetime.strptime(point['time'], "%Y-%m-%d %H:%M")
        except:
            t = datetime.datetime.now() # fallback
            
        val = point.get('value', 0)
        
        times.append(t)
        values.append(val)
        
        # Attribution des couleurs (Zonage Myzone)
        if val >= 90:
            colors.append('#ff0000') # Rouge
        elif val >= 80:
            colors.append('#ffea00') # Jaune
        elif val >= 70:
            colors.append('#00aa00') # Vert
        elif val >= 60:
            colors.append('#0000ff') # Bleu
        elif val >= 50:
            colors.append('#666666') # Gris foncé
        else:
            colors.append('#dddddd') # Gris clair (repos)

    if not times:
        return

    # Configuration de la figure
    fig, ax = plt.subplots(figsize=(10, 3.5), facecolor='white')
    width = 1 / (24 * 60) * 0.9 
    
    ax.bar(times, values, width=width, color=colors, edgecolor='white', linewidth=0.5, align='center')
    ax.set_ylim(0, 100)
    
    # Axe Y
    ax.set_ylabel('Effort', fontsize=10, fontweight='bold', color='#333333')
    ax.set_yticks([]) 
    
    # Axe X : Label temporel propre qui s'adapte à la durée
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    from matplotlib.ticker import MaxNLocator
    ax.xaxis.set_major_locator(MaxNLocator(nbins=20)) # Maximum 20 labels sur l'axe X pour éviter les chevauchements
    plt.xticks(rotation=0, fontsize=8, color='#666')
    
    # Esthétique globale
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#cccccc')
    
    ax.grid(axis='y', linestyle='-', alpha=0.2)
    
    plt.title("Graphique d'activités", loc='left', pad=15, fontsize=12, color='#333333')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    # Test avec des données fictives proches de la capture
    test_data = [
        {"time": f"2026-04-17 08:{i:02d}", "value": v} 
        for i, v in enumerate([
            45, 40, 42, 41, 40, 43, 41, 44, 42, 47, 
            65, 75, 73, 70, 78, 68, 72, 85, 82, 84,
            81, 88, 70, 80, 95, 72, 80, 95, 82, 85,
            86, 75, 60, 58, 65, 55, 57, 59, 65, 70,
            70, 78, 82, 85, 84, 65, 75, 76, 58, 60,
            55, 70, 85, 82, 88, 88, 85, 83, 72, 60,
            75, 78, 85, 88, 80, 79, 88, 85, 84, 86,
            85, 88, 75, 77, 60, 55, 53, 50
        ])
    ]
    generate_myzone_graph(test_data, 'test_graph.png')
    print("Graphique de test généré : test_graph.png")
