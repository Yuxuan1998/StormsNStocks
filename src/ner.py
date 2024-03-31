import spacy
import os
from collections import Counter

# Load the pre-trained spaCy model
nlp = spacy.load("en_core_web_sm")

class NewsEntityExtractor:
    """
    A class for extracting and summarizing named entities from news articles using spaCy.
    """
    
    def __init__(self, model='en_core_web_sm'):
        """
        Initializes the entity extractor with a specified spaCy model.
        
        Args:
        model (str): The name of the spaCy model to load.
        """
        self.nlp = spacy.load(model)
    
    def process_article(self, article_text):
        result = self.nlp(article_text)
        return result
    
    def extract_entities(self, doc):
        entities = {}
        for ent in doc.ents:
            entities.setdefault(ent.label_, []).append(ent.text)
        return entities
    
    def summarize_entities(self, entities):
        summary = {}
        for label, texts in entities.items():
            summary[label] = dict(Counter(texts))
        return summary

    def analyze_article(self, article_text):
        """
        Analyzes a news article to extract and summarize named entities.
        
        Args:
        article_text (str): The text of the news article to analyze.
        
        Returns:
        dict: A summary of named entities and their frequencies in the article.
        """
        doc = self.process_article(article_text)
        entities = self.extract_entities(doc)
        result = self.summarize_entities(entities)
        return result


def main() -> None:
    extractor = NewsEntityExtractor()
    directory_path = r'./data/disaster_news/guardian_articles'
    report_file_name = 'entity_summary_report.txt'
    report_file_path = os.path.join(directory_path, report_file_name)

    text_files = [file for file in os.listdir(directory_path) if file.endswith('.txt')]
    text_files.sort()
    
    for file in text_files:
        print(f"Reading {file}...",end="", flush=True)
        with open(os.path.join(directory_path, file), 'r', encoding='utf-8') as f:
            article_text = f.read()

        entity_summary = extractor.analyze_article(article_text)

        with open(report_file_path, 'a', encoding='utf-8') as report_file:
            report_file.write(f"Entities in {file}:\n")
            for label, entities in entity_summary.items():
                report_file.write(f"{label}:\n")
                for entity, count in entities.items():
                    report_file.write(f"  {entity}: {count}\n")
            report_file.write("==========================\n")
            report_file.write("\n")
        print("[DONE]")
    
    print(f"Report generated and saved to: {report_file_path}")

        # print(f"Entities in {file}:")
        # for label, entities in entity_summary.items():
        #     print(f"{label}:")
        #     for entity, count in entities.items():
        #         print(f"  {entity}: {count}")
        # print("==========================\n")


if __name__ == "__main__":
   main()