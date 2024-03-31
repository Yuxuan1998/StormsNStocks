import nltk
import contractions
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd


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


def plot_wordcloud(text):
    """
    plot wordcloud graph for given text
    """
    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(
        text
    )
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")  # Remove axis
    plt.title("Word Cloud")
    plt.show()


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
