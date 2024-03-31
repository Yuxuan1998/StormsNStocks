from src.text_mining_util import text_preprocessing
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import f1_score


class NBClassifier:
    def __init__(self, n_gram):
        self.n_gram = n_gram
        self.model = MultinomialNB()

    def create_tokens(self, df):
        df = df[["webTitle"]]
        df["tokens"] = df.webTitle.apply(text_preprocessing)
        return df

    def prepare_data(self, df):
        # flatten corpus
        flattened_corpus = df["tokens"].apply(lambda x: " ".join(x)).tolist()

        # Create CountVectorizer to convert text into a term frequency matrix
        self.vectorizer = CountVectorizer(ngram_range=(1, self.n_gram))
        frequency_matrix = self.vectorizer.fit_transform(flattened_corpus)

        return frequency_matrix

    def fit(self, df, y):
        self.X = self.create_tokens(df)
        self.y = y
        self.train()

    def train(self):
        frequency_matrix = self.prepare_data(self.X)
        self.model.fit(frequency_matrix, self.y)

    def predict(self, test_df):
        test_df = self.create_tokens(test_df)
        flattened_corpus = test_df["tokens"].apply(lambda x: " ".join(x)).tolist()
        X_test = self.vectorizer.transform(flattened_corpus)

        y_pred = self.model.predict(X_test)
        return y_pred

    def score(self, X, y):
        predictions = self.predict(X)
        return f1_score(y, predictions, average="micro")
