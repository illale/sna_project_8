import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import difflib
import itertools

def compare_main_topic_articles(topic_a, topic_b, df):
    topic_rows = df.get_group(topic_a)
    a_topic_rows = df.get_group(topic_b)
    article_count = 0
    for all_topics_a in list(topic_rows["topics"]):
        for all_topics_b in list(a_topic_rows["topics"]):
            all_topics_a.sort()
            all_topics_b.sort()
            if difflib.SequenceMatcher(None, all_topics_a, all_topics_b).ratio() > 0.50:
                article_count += 1
        if article_count > 2:
            return (topic_a, topic_b, article_count)
    return None

def check_nodes_in_community(node, community):
    for dict in community:
        if node in dict:
            return True
    return False
             
def create_colors(G, comm):
    colors = []
    node_colors = ["blue", "red", "green", "black", "orange", "yellow", "brown", "purple", "violet", "pink", "grey", "gold", "cyan",
                   "lime", "slategray", "thistle", "firebrick", "coral", "olive", "crimson"]
    for node in G:
        index = 0
        for community in comm:
            if check_nodes_in_community(node, community):
                colors.append(node_colors[index])
                break
            index += 1
    return colors

df = pd.read_csv("arxiv.csv")
G = nx.Graph()

main_topics = df["main_topic"].unique()
df["topics"] = list(df["all_topics"].str.split(", "))

edges = []

df = df.groupby(["main_topic"])
combinations = list(itertools.combinations(main_topics, 2))
for combination in combinations:
    edge = compare_main_topic_articles(combination[0], combination[1], df)
    if edge != None:
        edges.append(edge)

G.add_nodes_from(main_topics)
G.add_weighted_edges_from(edges)
G.remove_nodes_from(list(nx.isolates(G)))

plt.plot()
pos = nx.drawing.layout.circular_layout(G)
nx.drawing.draw_networkx(G, with_labels=True, pos=pos, font_size=6)
nx.drawing.draw_networkx_edge_labels(G, pos=pos)
plt.show()

graph_df = nx.convert_matrix.to_pandas_adjacency(G)
graph_df.to_csv("adjacency.csv")

table_headers = ["number_of_nodes", "diameter", "average_shortest_path_length", "average_clustering", "number_of_connected_components"]
table =  pd.DataFrame(columns=table_headers)

table = table.append(
    {"number_of_nodes": G.number_of_nodes(),
     "diameter": nx.distance_measures.diameter(G),
     "average_shortest_path_length": nx.average_shortest_path_length(G),
     "average_clustering": nx.algorithms.cluster.average_clustering(G),
     "number_of_connected_components": nx.number_connected_components(G)}, ignore_index = True
)

table.to_csv("measurements.csv")

GN = nx.algorithms.community.girvan_newman(G)
plt.plot()
l = list(GN)
print(len(l))
colors = create_colors(G, l[10])
nx.drawing.draw_networkx(G, pos=pos, node_color=colors, with_labels=True)
plt.show()

modularities = []
qualities = []

for partition in l:
    modularities.append(nx.algorithms.community.quality.modularity(G, partition))
    qualities.append(nx.algorithms.community.quality.partition_quality(G, partition))

plt.figure()
plt.plot(modularities)
plt.show()

plt.figure()
plt.plot(qualities)
plt.show()