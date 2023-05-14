import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd


df = pd.read_csv("arxiv.csv")

topics = df["all_topics"].to_list()

all_topics = []
for topic in topics:
    for sub in topic.split(";"):
        all_topics.append(sub)


figure = plt.figure()
plt.hist(df["year"])
plt.ylabel("Number of publications")
plt.xlabel("Year")
plt.show()

figure = plt.figure()
plt.hist(df["main_topic"], align="mid", density=True)
plt.xlabel("Main topics")
plt.xticks(rotation=90)
plt.show()

figure = plt.figure()
plt.hist(all_topics, align="mid", density=True)
plt.xlabel("All topics")
plt.xticks(rotation=90)
plt.show()
