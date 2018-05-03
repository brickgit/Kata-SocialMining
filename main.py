import os
import argparse
import twitter
import re
import networkx as nx
from networkx.drawing.nx_agraph import write_dot

consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token_key = os.environ.get('access_token_key')
access_token_secret = os.environ.get('access_token_secret')


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("k", help="Keyword")
    parser.add_argument("n", type=int, help="number")
    args = parser.parse_args()
    return args.k, args.n


def get_rt_sources(tweet):
    rt_patterns = re.compile(r"(RT|via)((?:\b\W*@\w+))", re.IGNORECASE)
    return [
        rt_source.strip()
        for rt_tuple in rt_patterns.findall(tweet)
        for rt_source in rt_tuple
        if rt_source not in ("RT", "via")
    ]


def main():
    keyword, number = get_arguments()

    g = nx.DiGraph()

    api = twitter.Api(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token_key=access_token_key,
        access_token_secret=access_token_secret,
    )

    tweets = []

    while len(tweets) < number:
        max_id = "" if len(tweets) == 0 else ("&max_id=" + tweets[-1].id_str)
        count = "&count=100"
        query = "q=" + keyword + count + max_id

        next_tweets = api.GetSearch(raw_query=query)
        if len(tweets) != 0 and tweets[-1].id_str == next_tweets[0].id_str:
            next_tweets.pop(0)

        tweets += next_tweets

    for tweet in tweets:
        rt_sources = get_rt_sources(tweet.text)
        if not rt_sources:
            continue
        for rt_source in rt_sources:
            if rt_source[0] == '@':
                rt_source = rt_source[1:]
            g.add_edge(rt_source, tweet.user.screen_name)

    write_dot(g, "keyword.dot")


if __name__ == "__main__":
    main()
