import nltk
import re
import contractions
from nltk import ngrams
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob
import fkscore
import scipy.sparse.linalg

stemmer = PorterStemmer()

with open("src/stopword_list.txt", "r") as file:
    reader = file.readlines()
    stopword_list = [word.strip() for word in reader]


def text_preprocessing(text) -> list:
    """
    preprocess:
        - lowercase
        - remove /
        - tokenization
        - remove stop words (keep not and remove "r")
        - process special words
        - lemmatization
            - different verb forms
            - plural forms to singular
    """
    # expand contraction
    text = contractions.fix(text)

    # remove special characters
    text = re.sub(r"[^\w\s\']", " ", text)

    # Tokenize the text
    tokens = word_tokenize(text)
    tokens = [token.lower() for token in tokens]

    # Remove stopwords
    stop_words = set(stopwords.words("english")) - {"not"}
    # Filter out stop words from the text
    tokens = [token for token in tokens if token not in stop_words]

    # Lemmatize the tokens
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token, pos="v") for token in tokens]

    # Convert plural words to singular
    processed_tokens = [
        lemmatizer.lemmatize(token, pos="n") for token in lemmatized_tokens
    ]

    return processed_tokens


def detect_key_word(key_word, text, tokenized=True) -> bool:
    """
    Detect if key_word is in the text
    """
    if not tokenized:
        tokens = text_preprocessing(text)
    else:
        tokens = text

    return key_word in tokens


def detect_key_word_list(key_word_list, text, tokenized=True, how="any") -> bool:
    """
    Detect if a list of key_word is in the text

    how = "any": at least one key_word is in the text
    how = "all": all key_word are in the text
    """
    if not tokenized:
        tokens = text_preprocessing(text)
    else:
        tokens = text

    if how == "any":
        for key_word in key_word_list:
            if detect_key_word(key_word, tokens, True):
                return True
        return False
    elif how == "all":
        for key_word in key_word_list:
            if not detect_key_word(key_word, tokens, True):
                return False
        return True


def plot_wordcloud(text, ax=None, n_gram=1):
    """
    plot wordcloud graph for given text
    """
    # create n-gram list
    tokenized_ngrams = list(ngrams(text.split(), n_gram))

    # Generate word frequency using Counter
    word_freq = Counter(tokenized_ngrams)
    freq = {}
    for i, v in word_freq.items():
        freq[i[0]] = v

    # Generate word cloud
    wordcloud = WordCloud(
        width=800, height=400, background_color="white"
    ).generate_from_frequencies(freq)

    if ax:
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.set_title("Word Cloud")
    else:
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")  # Remove axis
        plt.title("Word Cloud")
        plt.show()


def basic_feature_extraction(raw_corpus):

    """
    Extract basic statistics of the text
    """

    num_chars = []
    num_nonwhite_chars = []
    num_positive_words = []
    num_negative_words = []
    num_number = []

    for file in raw_corpus:

        num_count = 0
        tem_token = []
        num_chars.append(len(file))

        for word in file.split(" "):
            tem_token.append(stemmer.stem(word.lower()))
            try:
                word = int(word)
                num_count += 1
            except:
                pass

        num_nonwhite_chars.append(len(tem_token))
        num_number.append(num_count)

    return num_chars, num_nonwhite_chars, num_number


def create_tfidf_df(tokens, n_gram):
    """
    create TF-IDF dataframe on given list of tokens
    """

    corpus = tokens.apply(lambda x: " ".join(x)).to_list()

    # Create a TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer(ngram_range=(n_gram, n_gram))

    # Fit and transform the documents to compute TF-IDF matrix
    tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)

    # Get the feature names (terms)
    feature_names = tfidf_vectorizer.get_feature_names_out()

    # Convert TF-IDF matrix to a pandas DataFrame
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)

    return tfidf_df


def top_N_tfidf(tfidf_df, N) -> list:
    """
    Find top N TF-IDF tokens and return in a list
    """
    rank_df = pd.DataFrame(tfidf_df.max(axis=0), columns=["tfidf"]).reset_index(
        names="token"
    )
    tokens = rank_df.sort_values(by="tfidf", ascending=False, ignore_index=True).loc[
        : N - 1, "token"
    ]
    return tokens.tolist()


def tfidf_feature(
    pd_dataset, max_features: int, ngram_range, text_corpus, stopwords=stopword_list
):

    ### row is the document
    ### column is the term
    # max_features=10,    max_df=0.9, min_df=2 If it is an integer, then it is the absolute number of documents containing that word. If it is a decimal, then it is the proportion of documents containing that word.

    vectorizer = TfidfVectorizer(
        max_features=max_features, ngram_range=ngram_range, stop_words=stopwords
    )
    X = vectorizer.fit_transform(text_corpus)
    vectorizer.get_feature_names_out()
    feature_name = vectorizer.get_feature_names_out()
    tfidf = X.toarray()

    for col_idx in range(max_features):

        tem_list = []
        for row_idx in range(len(tfidf)):
            tem_list.append(tfidf[row_idx][col_idx])
        pd_dataset.insert(
            column=f"feature{col_idx}_{feature_name[col_idx]}",
            loc=len(pd_dataset.columns.values),
            value=tem_list,
        )

    return tfidf, pd_dataset, feature_name


def sentiment(pd_dataset):

    # polarity: negative vs. positive -1.0 - 1.0
    # subjectivity: objective vs. subjective 0.0 - 1.0

    polarity_list = []
    subjectivity_list = []
    tokens = list(pd_dataset["tokens"])

    for token in tokens:

        polarity, subjectivity = TextBlob(f"{' '.join(token)}").sentiment
        polarity_list.append(polarity)
        subjectivity_list.append(subjectivity)

        # break

    pd_dataset.insert(
        column="polarity", loc=len(pd_dataset.columns.values), value=polarity_list
    )
    pd_dataset.insert(
        column="subjectivity",
        loc=len(pd_dataset.columns.values),
        value=subjectivity_list,
    )

    return pd_dataset


def readability(pd_dataset):

    ### Flesch Kincaid readability score for text

    ### num_syllables: Number of syllables
    ### num_sentences: Number of sentences
    ### readability: higher scores indicate material that is easier to read
    ### read_grade:Grade level can be permuted from the Flesch Reading Ease score
    ### calc_grade: It can also mean the number of years of education generally required to understand this text, most relevant when the formula results in a number greater than 10.

    num_sentences_list = []
    num_syllables_list = []
    readability_list = []
    read_grade_list = []
    calc_grade_list = []

    raw_text = list(pd_dataset["text"])

    for text in raw_text:

        f = fkscore.fkscore(text)
        stat = f.stats
        score = f.score

        num_sentences_list.append(stat["num_sentences"])
        num_syllables_list.append(stat["num_syllables"])

        readability_list.append(score["readability"])
        read_grade_list.append(score["read_grade"])
        calc_grade_list.append(score["calc_grade"])

        # break

    pd_dataset.insert(
        column="num_sentences",
        loc=len(pd_dataset.columns.values),
        value=num_sentences_list,
    )
    pd_dataset.insert(
        column="num_syllables",
        loc=len(pd_dataset.columns.values),
        value=num_syllables_list,
    )
    pd_dataset.insert(
        column="readability", loc=len(pd_dataset.columns.values), value=readability_list
    )
    pd_dataset.insert(
        column="read_grade", loc=len(pd_dataset.columns.values), value=read_grade_list
    )
    pd_dataset.insert(
        column="calc_grade", loc=len(pd_dataset.columns.values), value=calc_grade_list
    )

    return pd_dataset
