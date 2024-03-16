import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


def text_preprocessing(text) -> list:
    # Tokenize the text
    tokens = word_tokenize(text.lower())

    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    # Filter out stop words from the text
    tokens = [token for token in tokens if token not in stop_words]

    # Lemmatize the tokens
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return lemmatized_tokens


def detect_key_word(key_word, text, tokenized=False):
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
            if key_word[i] != tokens[idx + i]:
                return False
        return True


def detect_key_word_list(key_word_list, text, tokenized=False, how="any"):
    if not tokenized:
        tokens = text_preprocessing(text)
    else:
        tokens = text

    if how == "any":
        for key_word in key_word_list:
            if detect_key_word(key_word, tokens):
                return True
        return False
    elif how == "all":
        for key_word in key_word_list:
            if not detect_key_word(key_word, tokens):
                return False
        return True
