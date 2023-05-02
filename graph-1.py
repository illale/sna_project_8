import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as mcm
import difflib
import itertools

def compare_main_topic_articles(topic_a, topic_b, df):
    #Compare two groups of articles with different main topics.

    #Get the rows in dataset df, that share the main topics
    topic_a_rows = df.get_group(topic_a)
    topic_b_rows = df.get_group(topic_b)
    article_count = 0

    #Loop over the list of all_topics of each article from main topics A and B
    for all_topics_a in list(topic_a_rows["topics"]):
        for all_topics_b in list(topic_b_rows["topics"]):
            #Sort the list of topics, so that SequenceMatcher can correctly identify similar lists
            all_topics_a.sort()
            all_topics_b.sort()
            #Compare the two lists of topics.
            if difflib.SequenceMatcher(None, all_topics_a, all_topics_b).ratio() > 0.50:
                article_count += 1
        #If there are more than two articles fitting the criteria, return the tuple representation of the edge. Else return None
        if article_count >= 2:
            return (topic_a, topic_b, article_count)
    return None

def check_nodes_in_community(node, community):
    for dict in community:
        if node in dict:
            return True
    return False
             
def create_colors(G, comm):
    colors = []
    cmap = mcm.get_cmap("tab20")
    node_colors = cmap.colors
    for node in G:
        index = 0
        for community in comm:
            if check_nodes_in_community(node, community):
                colors.append(node_colors[index])
                break
            index += 1
    return colors

def create_graph(df):
    main_topics = df["main_topic"].unique()
    df["topics"] = list(df["all_topics"].str.split(";"))
    G = nx.Graph()
    edges = []    
    df = df.groupby(["main_topic"])
    combinations = list(itertools.combinations(main_topics, 2))
    for combination in combinations:
        edge = compare_main_topic_articles(combination[0], combination[1], df)
        if edge != None:
            edges.append(edge)

    G.add_nodes_from(main_topics)
    G.add_weighted_edges_from(edges)
    return G

def plot_network(G, pos):
    plt.plot()
    nx.drawing.draw_networkx(G, with_labels=True, pos=pos, font_size=6)
    labels = nx.get_edge_attributes(G,'weight')
    nx.drawing.draw_networkx_edge_labels(G, pos=pos, edge_labels=labels)
    plt.show()

def create_adjacency_and_stat_table(G):
    
    #Create adjacency matrix
    graph_df = nx.convert_matrix.to_pandas_adjacency(G)

    #Create measurement table
    table_headers = ["number_of_nodes", "diameter", "average_shortest_path_length", "average_clustering", "number_of_connected_components"]
    table =  pd.DataFrame(columns=table_headers)
    table = table.append(
        {"number_of_nodes": G.number_of_nodes(),
        "diameter": nx.distance_measures.diameter(G),
        "average_shortest_path_length": nx.average_shortest_path_length(G),
        "average_clustering": nx.algorithms.cluster.average_clustering(G),
        "number_of_connected_components": nx.number_connected_components(G)}, ignore_index = True
    )

    #Save adjacency matrix and measurement table to csv files
    graph_df.to_csv("adjacency.csv")
    table.to_csv("measurements.csv")

def calculate_girvan_newman(G):
    GN = nx.algorithms.community.girvan_newman(G)
    return list(GN)

def plot_girvan_newman_iteration(G, GNN, iteration):
    colors = create_colors(G, GNN[iteration])
    plt.plot()
    nx.drawing.draw_networkx(G, pos=pos, node_color=colors, with_labels=True)
    plt.show()

def calculate_and_plot_girvan_newman_measurements(G, GGN):
    modularities = []
    qualities = []

    for partition in GGN:
        modularities.append(nx.algorithms.community.quality.modularity(G, partition))
        qualities.append(nx.algorithms.community.quality.partition_quality(G, partition))

    plt.figure()
    plt.plot(modularities)
    plt.show()

    plt.figure()
    plt.plot(qualities)
    plt.show()

if __name__ == "__main__":
    df = pd.read_csv("arxiv.csv")
    G = create_graph(df)
    pos = nx.drawing.layout.circular_layout(G)
    plot_network(G, pos)

    #Remove unconnected nodes.
    G.remove_nodes_from(list(nx.isolates(G)))

    pos = nx.drawing.layout.kamada_kawai_layout(G)
    plot_network(G, pos)

    create_adjacency_and_stat_table(G)
    GGN = calculate_girvan_newman(G)
    plot_girvan_newman_iteration(G, GGN, 10)
    calculate_and_plot_girvan_newman_measurements(G, GGN)