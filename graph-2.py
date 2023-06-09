import urllib
import xmltodict
import pandas as pd
import time
import itertools
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib

singular_nodes = []

def get_collaborators():
	base_url = "http://export.arxiv.org/api/query?"

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

				# delete duplicate affiliations in the same paper
				affiliations = list(set(affiliations))
					
				if len(affiliations) > 1:
					for combination in itertools.combinations(affiliations, 2):
						if combination not in collabs:
							collabs.append([*combination, 1])
						else:
							collabs.index(combination)[2] += 1
				#else:
				#	singular_nodes.append(*affiliations)

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
		"diameter": 1,
		"average_shortest_path_length": 1.0, 
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
	return colors

def calculate_girvan_newman(G):
	GN = nx.algorithms.community.girvan_newman(G)
	return list(GN)

def plot_girvan_newman_iteration(G, GNN, iteration):
	print(GNN[iteration])
	colors = create_colors(G, GNN[iteration])
	pos = nx.spring_layout(G, k=0.5)
	plt.plot()
	nx.drawing.draw_networkx(G, pos=pos, node_color=colors, with_labels=True, font_size=10)
	plt.show()

def calculate_and_plot_girvan_newman_measurements(G, GGN):
	modularities = []
	qualities = ([], [])

	for partition in GGN:
		modularities.append(nx.algorithms.community.quality.modularity(G, partition))
		quality = nx.algorithms.community.quality.partition_quality(G, partition)
		qualities[0].append(quality[0])
		qualities[1].append(quality[1])


	plt.figure()
	plt.plot(modularities)
	plt.xlabel("Girvan-Newman iteration")
	plt.ylabel("Partition modularity")
	plt.show()

	plt.figure()
	plt.plot(qualities[0], label="Coverage")
	plt.plot(qualities[1], label="Performance")
	plt.xlabel("Girvan-Newman iteration")
	plt.ylabel("Partition quality")
	plt.legend()
	plt.show()

if __name__ == "__main__":
		
	collabs = get_collaborators()
	print(collabs)

	G = nx.Graph()
	G.add_weighted_edges_from(collabs)
	G.add_nodes_from(singular_nodes)
	
	plt.plot()
	pos = nx.spring_layout(G, k=0.5)
	nx.drawing.draw_networkx(G, pos=pos, with_labels=True, font_size=10)
	labels = nx.get_edge_attributes(G,'weight')
	nx.drawing.draw_networkx_edge_labels(G, pos=pos, edge_labels=labels)
	plt.show()

	create_stat_table(G)
		
	GGN = calculate_girvan_newman(G)
	plot_girvan_newman_iteration(G, GGN, 0)
	calculate_and_plot_girvan_newman_measurements(G, GGN)
	




	