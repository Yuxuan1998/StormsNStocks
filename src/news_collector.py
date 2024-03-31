import argparse
import json
import calendar
import requests
import backoff
import pandas as pd
import numpy as np
from newsplease import NewsPlease
import logging

from src.text_mining_util import text_preprocessing, detect_key_word

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

DISASTER_KEY_WORDS = [
    "earthquake",
    "tsunami",
    "typhoon",
    "cyclone",
    "hurricane",
    "tornado",
    "flood",
    "drought",
    "wildfire",
    "blizzard",
    "storm",
    "derecho",
    "bomb cyclone",
]


class NewsCollector:
    def __init__(self, api_key: str, path_prefix: str, start_year: int, end_year: int):
        self.disaster_key_words = DISASTER_KEY_WORDS
        self.api_key = api_key
        self.search_query = None
        self.path_prefix = path_prefix
        self.start_year = start_year
        self.end_year = end_year

    def create_search_query(self):
        country = ["United States", "US", "USA", "America"]
        country_query = []
        for w in country:
            if " " in w:
                country_query.append(f'"{w.replace(" ", "%20")}"')
            else:
                country_query.append(w)
        country_query = "%20OR%20".join(country_query)

        disaster_query = []
        for w in DISASTER_KEY_WORDS:
            if " " in w:
                disaster_query.append(f'"{w.replace(" ", "%20")}"')
            else:
                disaster_query.append(w)
        disaster_query = "%20OR%20".join(disaster_query)

        return "%20AND%20".join([f"({disaster_query})", f"({country_query})"])

    def create_url(self, from_date, to_date) -> str:
        if not self.search_query:
            self.search_query = self.create_search_query()
        return f"https://content.guardianapis.com/search?q={self.search_query}&page-size=50&section=us-news&from-date={from_date}&to-date={to_date}&api-key={self.api_key}"

    @staticmethod
    @backoff.on_exception(
        backoff.expo, requests.exceptions.RequestException, max_tries=5
    )
    def query_meta_data(url):
        # http request
        request_headers = {"Accept": "application/json"}
        response = requests.get(url, headers=request_headers)

        # load
        data = json.loads(response.text)

        return data["response"]["results"]

    @staticmethod
    @backoff.on_exception(
        backoff.expo, requests.exceptions.RequestException, max_tries=5
    )
    def qeury_main_text(url):
        """
        Query content of news article
        """
        article = NewsPlease.from_url(url)
        return article.maintext

    @staticmethod
    def create_metadata_df(data):
        df = {"webPublicationDate": [], "webTitle": [], "webUrl": [], "type": []}
        for doc in data:
            for k in df.keys():
                df[k].append(doc[k])
        df = pd.DataFrame(df)

        # tokenize title
        df["title_tokens"] = df["webTitle"].apply(text_preprocessing)

        return df

    def filter_news(self, df):
        """
        Filter news based on title and type
        """
        # material type is news article
        df = df[df.type == "article"].reset_index(drop=True)

        # drop US briefing:
        s = "US briefing:"
        df = df[df.webTitle.apply(lambda x: x[: len(s)] != s)].reset_index(drop=True)

        # detect disaster
        df["disaster_type"] = pd.Series()
        for disaster in self.disaster_key_words:
            df["disaster_type"] = np.where(
                df.title_tokens.apply(lambda x: detect_key_word(disaster, x)),
                disaster,
                df.disaster_type,
            )

        df = df.drop(columns=["title_tokens"])[~df.disaster_type.isna()].reset_index(
            drop=True
        )

        return df

    def save_articles(self, df) -> pd.DataFrame:
        """
        Query the content of news article based on the url in metadata df
        Creat path column in metadata df
        """
        path = []
        for i, row in df.iterrows():
            article = self.qeury_main_text(row.webUrl)
            # compute path
            fn = row.webPublicationDate[:10].replace("-", "_") + f"_{i}.txt"
            file_path = self.path_prefix + fn
            path.append(file_path)
            # write txt
            with open(file_path, "w") as file:
                # Write the string to the file
                file.write(article)
        df["path"] = path
        return df

    def collect_news(self):
        # create and save metadata df
        df_ls = []
        for year in range(self.start_year, self.end_year + 1):
            for month in range(1, 13):
                last_day = calendar.monthrange(year, month)[1]
                from_date = f"{year}-{str(month).zfill(2)}-01"
                to_date = f"{year}-{str(month).zfill(2)}-{last_day}"

                url = self.create_url(from_date, to_date)
                data = self.query_meta_data(url)
                df = self.create_metadata_df(data)
                df_ls.append(df.copy())

                logging.info(f"Done: metadata for {year}-{month}")

        meta_df = pd.concat(df_ls, ignore_index=True)
        meta_df = self.filter_news(meta_df).reset_index(drop=True)
        meta_df = self.save_articles(meta_df)
        logging.info(f"Done: save news content to txt")
        meta_df.to_csv(f"{self.path_prefix}/news_metadata.csv", index=False)
        logging.info(f"Done: save metadata")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--api_key", required=True, help="The Guardian API key")
    parser.add_argument(
        "--path_prefix", default="data/news/", help="path to data folder"
    )
    parser.add_argument("--start_year", default="2019")
    parser.add_argument("--end_year", default="2023")

    args = vars(parser.parse_args())
    api_key = args["api_key"]
    path_prefix = args["path_prefix"]
    start_year = int(args["start_year"])
    end_year = int(args["end_year"])

    news_collector = NewsCollector(api_key, path_prefix, start_year, end_year)
    news_collector.collect_news()
