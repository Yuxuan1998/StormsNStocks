from multiprocessing import Pool
import os
import spacy
from collections import Counter

# Define the EnhancedNewsEntityExtractor class here
# Ensure spaCy model is loaded outside the multiprocessing function

nlp = spacy.load("en_core_web_sm")  # Load model once, use across processes

class EnhancedNewsEntityExtractor:
    def __init__(self, nlp):
        self.nlp = nlp
    
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


def process_article(article_path):
    extractor = EnhancedNewsEntityExtractor(nlp)
    with open(article_path, 'r', encoding='utf-8') as file:
        article_text = file.read()
    # Split the article into chunks
    max_length = 1000000  # spaCy's default max length
    chunks = [article_text[i:i+max_length] for i in range(0, len(article_text), max_length)]
    
    extractor = EnhancedNewsEntityExtractor(nlp)
    combined_summary = {}
    
    for chunk in chunks:
        chunk_summary = extractor.analyze_article(chunk)
        # Combine the summaries
        for label, entities in chunk_summary.items():
            if label in combined_summary:
                for entity, count in entities.items():
                    combined_summary[label][entity] = combined_summary[label].get(entity, 0) + count
            else:
                combined_summary[label] = entities
    
    summary = f"Entities in {os.path.basename(article_path)}:\n"
    for label, entities in combined_summary.items():
        summary += f"{label}:\n"
        for entity, count in entities.items():
            summary += f"  {entity}: {count}\n"
    summary += "============================\n\n"
    return summary

def main():
    directory_path = r'./data/disaster_news/guardian_articles'
    text_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.txt')]
    text_files.sort()
    
    # Use multiprocessing to process articles in parallel
    with Pool(processes=os.cpu_count()) as pool:
        summaries = pool.map(process_article, text_files)
    
    # Write summaries to a single report file
    report_path = os.path.join(directory_path, 'entity_summary_report.txt')
    with open(report_path, 'w', encoding='utf-8') as report_file:
        for summary in summaries:
            report_file.write(summary)
    
    print(f"Report generated and saved to: {report_path}")

if __name__ == "__main__":
    main()