import os
import re
import json
import pandas as pd
from summa import keywords
from newsapi import NewsApiClient


ERRORS = {
    "news-api": {
        "error": {
            "text": "Search yielded no results!",
            "reason": "We could not find related articles in any of the sources."
        }
    },
    "keywords": {
        "error": {
            "text": "Keyword extraction failed!",
            "reason": "One frequent explanation is that the text is too short."
        }
    }
}


def get_keywords(text, min_results=2, max_results=3, min_score=.2, language='en'):
    try:
        kwds = pd.DataFrame(
            keywords.keywords(text, ratio=1.0, split=True, scores=True), 
            columns=["keyword", "score"]).sort_values("score", ascending=False)
        to_keep = max(min((kwds["score"] > min_score).sum(), min_results), max_results)
        return " ".join(kwds["keyword"].head(to_keep).values)
    except IndexError:
        return ""

def fetch_articles(text, start_date=None, end_date=None, language=None):
    newsapi = NewsApiClient(api_key=load_key())
    kwds = get_keywords(text, language=language)
    print("Keywords: {}".format(kwds))
    if kwds:
        articles = newsapi.get_everything(
            q=kwds,
            sources=filter_sources(language=language),
            # domains='bbc.co.uk,techcrunch.com',
            from_param=start_date or None,
            to=end_date or None,
            language=language or None,
            sort_by='relevancy')
        if articles["totalResults"]:
            return sort_articles(articles, load_sources())
        else:
            return ERRORS["news-api"]
    return ERRORS["keywords"]


def sort_articles(articles, sources_categories):
    source_map = {source: key for key, sources in sources_categories.items() for source in sources}
    sorted_sources = {key: [] for key in sources_categories.keys()}
    for article in articles["articles"]:
        if article["source"]["id"] in source_map:
            sorted_sources[source_map[article["source"]["id"]]].append(article)
    return sorted_sources


def absolute_path(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def load_key():
    with open(absolute_path("apikey")) as f:
        return f.read().strip()


def load_sources():
    with open(absolute_path("api_sources.json")) as f:
        return json.load(f)


def filter_sources(influence="all", language="en"):
    sources = load_sources()
    if influence == "all":
        sources_list = [s for l in sources.values() for s in l]
    else:
        assert influence in sources.keys(), "{} not in available political leanings".format(influence)
        sources_list = sources[influence]
    return ",".join(sources_list)


if __name__ == "__main__":
    from pprint import pprint
    # Test API
    text = """Democrat Stacey Abrams acknowledges that Republican Brian Kemp will be certified as 
    the next Georgia governor, but says she is not offering a speech of concession because that 
    would suggest the election process was just: "The state failed its voters" - @MSNBC"""
    articles = fetch_articles(text, "2018-11-02")
    pprint(articles)
    # with open(absolute_path('results.json'), 'w') as f:
    #     json.dump(articles, f)
