import urllib
import feedparser
import xmltodict
import pandas as pd
import time
import itertools
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib

def get_collaborators():
	base_url = "http://export.arxiv.org/api/query?"
	feedparser.mixin._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
	feedparser.mixin._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'

	df = pd.read_csv("arxiv.csv")

	id_list = df["article_id"].tolist()
	collabs = []

	# The query url would be too long with 1000 ids
	for i in range(2):
		id_list_string = ",".join(id_list[i*500:(i+1)*500])

		query = "id_list=%s&max_results=%i" % (id_list_string, 500)
        
		response = urllib.request.urlopen(base_url+query).read()

		xmldict = xmltodict.parse(response)

		for entry in xmldict["feed"]["entry"]:
			authors = entry["author"]
			affiliations = []
			try:
				if type(authors) is dict:
					authors = [authors]
				for author in authors:
					affiliations.append(author["arxiv:affiliation"]["#text"])

				# delete duplicate affiliations
				affiliations = list(set(affiliations))
                
				if len(affiliations) > 1:
					for combination in itertools.combinations(affiliations, 2):
						collabs.append(combination)
			except:
				pass

		time.sleep(3)

	

	return collabs


def create_stat_table(G):

    #Create measurement table
    table_headers = ["number_of_nodes", "diameter", "average_shortest_path_length", "average_clustering", "number_of_connected_components"]
    table =  pd.DataFrame(columns=table_headers)
    table = table._append(
        {"number_of_nodes": G.number_of_nodes(),
        "diameter": "infinite",
        #"average_shortest_path_length": nx.average_shortest_path_length(G),
        "average_clustering": nx.algorithms.cluster.average_clustering(G),
        "number_of_connected_components": nx.number_connected_components(G)}, ignore_index = True
    )
    
    table.to_csv("measurements_2.csv")
    
def check_nodes_in_community(node, community):
    for dict in community:
        if node in dict:
            return True
    return False

def create_colors(G, comm):
    colors = []
    cmap = matplotlib.colormaps["tab20"]
    node_colors = cmap.colors
    for node in G:
        index = 0
        for community in comm:
            if check_nodes_in_community(node, community):
                colors.append(node_colors[index])
                break
            index += 1

def calculate_girvan_newman(G):
    GN = nx.algorithms.community.girvan_newman(G)
    return list(GN)

def plot_girvan_newman_iteration(G, GNN, iteration):
    colors = create_colors(G, GNN[iteration])
    plt.plot()
    nx.drawing.draw_networkx(G, node_color=colors, with_labels=True)
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
		
	collabs = get_collaborators()
	print(collabs)

	G = nx.Graph()
	G.add_edges_from(collabs)
	
	plt.plot()
	nx.drawing.draw_networkx(G, with_labels=True, font_size=6)
	plt.show()

	create_stat_table(G)
		
	GGN = calculate_girvan_newman(G)
	plot_girvan_newman_iteration(G, GGN, len(GGN) - 1)
	calculate_and_plot_girvan_newman_measurements(G, GGN)
	




	