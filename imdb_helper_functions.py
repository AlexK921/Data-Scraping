import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import networkx as nx
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS


def url_to_soup(url):
    headers = {
        'Accept-Language': 'en',
        'X-FORWARDED-FOR': '2.21.184.0',
        'User-Agent': 'Chrome/83.0.4103.116'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, features="html.parser")
    return soup


def current_year():
    return datetime.now().year


def save_pairwise_distances_to_csv(pairwise_distances, actors_list, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header_row = ['First Actor', 'First Actor Page', 'Second Actor', 'Second Actor Page', 'Distance']
        writer.writerow(header_row)
        for i, actor_start in enumerate(actors_list):
            for j, actor_end in enumerate(actors_list):
                if i != j:
                    distance = pairwise_distances[actor_start][actor_end]
                    row = [actor_start[0], actor_start[1], actor_end[0], actor_end[1], distance]
                    writer.writerow(row)


def read_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
    return data


def create_graph(data):
    G = nx.Graph()
    for row in data:
        actor1 = row['First Actor']
        actor2 = row['Second Actor']
        distance = float(row['Distance'])
        if distance != float('inf'):
            distance = int(distance)
            G.add_edge(actor1, actor2, weight=distance)
        #else:
        #    G.add_node(actor1)
        #    G.add_node(actor2)
    return G


def create_graph_per_distance(data, dist):
    G = nx.Graph()
    for row in data:
        actor1 = row['First Actor']
        actor2 = row['Second Actor']
        distance = float(row['Distance'])
        if distance != float('inf') and distance == dist:
            if distance == dist:
                distance = int(distance)
                G.add_edge(actor1, actor2, weight=dist)
    return G


def draw_graph_with_filtered_edges(G, dist):
    pos = nx.spring_layout(G)
    labels = {node: wrap_text(node) for node in G.nodes}
    nx.draw(G, pos, labels=labels, node_size=1500, node_color='skyblue', font_size=8)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    colors = ['red', 'green', 'blue']
    for distance in range(0, 3):
        edges = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] == distance]
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=colors[distance-1])
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title(f'Graph Movie Distance - {dist}', fontsize=14)
    plt.axis('off')
    # save figure to the Graphs folder
    plt.savefig(f'Graphs/graph_with_distances_{dist}.png')
    plt.show()


def wrap_text(text):
    words = text.split()
    lines = []
    current_line = []
    current_line_length = 0
    for word in words:
        if current_line_length + len(word) + 1 > 10:
            lines.append(' '.join(current_line))
            current_line = []
            current_line_length = 0
        current_line.append(word)
        current_line_length += len(word) + 1
    lines.append(' '.join(current_line))
    return '\n'.join(lines)


def draw_graph(G):
    pos = nx.spring_layout(G)
    labels = {node: wrap_text(node) for node in G.nodes}
    nx.draw(G, pos, labels=labels, node_size=2000, node_color='skyblue', font_size=8)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    colors = ['red', 'green', 'blue']
    for distance in range(0, 3):
        edges = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] == distance]
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=colors[distance-1])
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title('Graph Movie Distance', fontsize=14)
    plt.axis('off')
    # save figure to the Graphs folder
    plt.savefig('Graphs/Graph.png')
    plt.show()


def save_to_text_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for row in data:
            file.write('\t'.join(row) + '\n')


def read_from_text_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = [row.strip().split('\t') for row in file.readlines()]  # Read all lines and split them into rows
    return data


def build_word_cloud(data, name):
    mystopwords = list(STOPWORDS) + ['one', 'two', 'ten', 'three', 'year',
                                    'at', 'ex', 'must', 'new', 'man']
    text = ' '.join([description for description in data])
    wordcloud = WordCloud(width=800, height=800,
                            background_color='white',
                            stopwords=mystopwords,
                            min_font_size=10).generate(text)

    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    # save figure to the folder Word_Clouds
    plt.savefig(f"Word_Clouds/Word_cloud_{name.replace(' ', '_')}.png")
    plt.show()
