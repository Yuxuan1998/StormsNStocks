import nltk
import contractions
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


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

    keyword = key_word.split(" ")
    if len(keyword) == 1:
        return key_word in tokens
    else:
        try:
            idx = tokens.index(keyword[0])
        except ValueError:
            return False

        for i in range(1, len(keyword)):
            if idx + i >= len(tokens):
                return False
            if keyword[i] != tokens[idx + i]:
                return False
        return True


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
