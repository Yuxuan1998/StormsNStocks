from src.text_mining_util import text_preprocessing
import fasttext
from sklearn.metrics import f1_score


class FTClassifier:
    def __init__(self, lr, wordNgrams):
        self.lr = lr
        self.wordNgrams = wordNgrams

    def fit(self, df, _=None):
        self.input = "fasttext.train"
        df["label"] = "__label__" + df["label"].astype(str)
        df["label_title"] = df["label"] + " " + df["webTitle"]
        df.to_csv(self.input, columns=["label_title"], index=False, header=False)

        self.model = fasttext.train_supervised(
            input=self.input, lr=self.lr, wordNgrams=self.wordNgrams, verbose=False
        )

    def predict(self, df_test):
        y_pred = df_test.webTitle.map(lambda x: self.model.predict(x)[0][0])
        return y_pred.apply(lambda x: x.split("__")[2])

    def score(self, X, y):
        predictions = self.predict(X)
        return f1_score(y, predictions, average="micro")
