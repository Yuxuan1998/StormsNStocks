import os
import re
from typing import List
import spacy
from multiprocessing import Pool
from collections import Counter
from src.us_location_resolver import USLocationResolver
import us


class ParallelTextProcessor:
    def __init__(self, model="en_core_web_sm", chunk_size=1000000):
        self.location_resolver = USLocationResolver()
        self.nlp = spacy.load(model)
        self.chunk_size = chunk_size

    @staticmethod
    def analyze_chunk(text_nlp_tuple):
        text, nlp = text_nlp_tuple
        doc = nlp(text)
        entities = {}
        summary = {}

        for ent in doc.ents:
            entities.setdefault(ent.label_, []).append(ent.text)

        # Summarize entity occurrences
        for label, texts in entities.items():
            summary[label] = dict(Counter(texts))
        return summary

    def process_text(self, text, year):
        # Divide the text into manageable chunks
        chunks = [
            (text[i : i + self.chunk_size], self.nlp)
            for i in range(0, len(text), self.chunk_size)
        ]

        # Use multiprocessing to analyze each chunk in parallel
        with Pool() as pool:
            chunk_summaries = pool.map(self.analyze_chunk, chunks)

        # Combine the summaries from each chunk
        combined_summary = {}

        for summary in chunk_summaries:
            for label, entities in summary.items():
                if label in combined_summary:
                    for entity, count in entities.items():
                        combined_summary[label][entity] = (
                            combined_summary[label].get(entity, 0) + count
                        )
                else:
                    combined_summary[label] = entities

        country_keywords = ["us", "united states", "united states of america", "usa"]
        filtered_dict_items = {
            key: value
            for key, value in combined_summary["GPE"].items()
            if key.lower() not in country_keywords
        }
        sorted_filtered_dict_items = sorted(
            filtered_dict_items.items(), key=lambda x: x[1], reverse=True
        )

        for i in range(1, len(sorted_filtered_dict_items) + 1):
            state_name = [item[0] for item in sorted_filtered_dict_items[i - 1 : i]]
            state = us.states.lookup(str(state_name))
            if (
                state is not None
                and state not in us.states.TERRITORIES
                and state not in us.states.OBSOLETE
            ):
                break
            else:
                state_name = [item[0] for item in sorted_filtered_dict_items[:1]]

        state_info = self.get_us_location(state_name, year)

        return state_info

    def get_us_location(self, division_names: List[str], year: int):
        result = []
        for name in division_names:
            state_info = self.location_resolver.convert_to_state_and_region(name, year)
            result.append(state_info)
        return result


def main():
    article_path = r"data/news/2019_08_26_20.txt"
    text_processor = ParallelTextProcessor(chunk_size=500000)

    with open(article_path, "r", encoding="utf-8") as file:
        article_text = file.read()

    parts = article_path.split("/")
    year = parts[-1].split("_")[0]
    result = text_processor.process_text(article_text, int(year))
    # print(combined_summary['PERSON'])
    print(result)


if __name__ == "__main__":
    main()
