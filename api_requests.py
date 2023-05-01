import arxiv
import pandas as pd


def authors_to_list(authors):
  res = ""
  for author in authors:
    res += (author.name + ";")
  res = res.removesuffix(";")
  return res

search = arxiv.Search(
  query = "automatic text summarization OR text summarization OR automatic document summarization",
  max_results = 1100
)

headers = ["title", "date", "article_id", "url", "main_topic", "all_topics", "authors", "year"]

df = pd.DataFrame(columns=headers)

results = []
searchResults = search.results()

while len(results) < 1000:
  result = next(searchResults)
  if result.published.year >= 2000:
    results.append(
      {"title": result.title,
      "date": result.published,
      "article_id": result.entry_id.split("/")[-1],
      "url": result.entry_id,
      "main_topic": result.primary_category,
      "all_topics": ";".join(result.categories),
      "authors": authors_to_list(result.authors),
      "year": result.published.year
      }
    )
  print(len(results))

df = pd.DataFrame.from_records(results)

df.to_csv("arxiv.csv")
