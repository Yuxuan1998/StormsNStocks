import pandas as pd
import os
from tqdm import tqdm
from nltk.stem import PorterStemmer
import wordcloud
import pylab
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
from numpy import matrix
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
import fkscore

def draw_stackplot(data,xlabels,ylabels):

    # X标签 行，即章节
    # Y标签 列，即词汇
    # 数据 即词频，需要转置后才能应用
    #data= [[0, 3, 3, 3, 0, 0, 3, 0, 3], [0, 3, 0, 3, 0, 6, 3, 0, 3], [3, 0, 0, 0, 3, 0, 3, 3, 0], [0, 3, 3, 3, 0, 0, 3, 0, 3]]
    #xlablels= range(0, 4)
    #ylablels= ['and', 'document', 'first', 'is', 'one', 'second', 'the', 'third', 'this']
    pylab.mpl.rcParams['font.sans-serif'] = ['SimHei']
    pylab.mpl.rcParams['axes.unicode_minus'] = False
    fig, ax = plt.subplots()
    ax.stackplot(xlabels, data, labels=ylabels, baseline='wiggle')
    #ax.axes.set_yticks(range(len(ylabels)))
    #ax.axes.set_yticklabels(ylabels)
    #ax.axes.set_xticks(range(len(xlabels)))
    #ax.axes.set_xticklabels(xlabels)
    ax.set_xlabel('News index')
    ax.legend(loc='best')
    ax.set_title('Interesting Graph\nCheck it out')
    plt.show()

#文本词频可视化图表heatmap风格
def draw_heatmap(data, xlabels, ylabels):
    pylab.mpl.rcParams['font.sans-serif'] = ['SimHei']
    pylab.mpl.rcParams['axes.unicode_minus'] = False
    vmin=np.amin(matrix(data))
    vmax = np.amax(matrix(data))
    cmap = cm.Blues
    figure = plt.figure(facecolor='w')
    ax = figure.add_subplot(2, 1, 1, position=[0.1, 0.15, 0.8, 0.8])
    #ax.set_yticks(range(len(ylabels)))
    #ax.set_yticklabels(ylabels)
    ax.set_xlabel('Word frequency')
    ax.set_ylabel('News index')
    ax.set_xticks(range(len(xlabels)))
    ax.set_xticklabels(xlabels)
    map = ax.imshow(data, interpolation='nearest', cmap=cmap, aspect='auto', vmin=vmin, vmax=vmax)
    cb = plt.colorbar(mappable=map, cax=None, ax=None, shrink=0.5)
    plt.xticks(rotation=90)
    plt.yticks(rotation=360)
    plt.show()

def tokenization(raw_corpus, stoplist):

    ### generate token
    ### delete stopwords
    ### case folding
    ### stemming
    ### lemmatization

    token = []
    all_unique_token = []
    for file in tqdm(raw_corpus):

        tem_token = [stemmer.stem(word.lower()) for word in file.split(' ') if word not in stoplist]
        token.append(tem_token)
        all_unique_token = all_unique_token + tem_token
        all_unique_token = list(set(all_unique_token))

        #break

    return token, all_unique_token

def basic_feature_extraction(raw_corpus):

    ### 没有找到积极消极词分类的字典

    num_chars = []
    num_nonwhite_chars = []
    num_positive_words = []
    num_negative_words = []
    num_number = []

    for file in tqdm(raw_corpus):

        num_count = 0
        tem_token = []
        num_chars.append(len(file))

        #tem_token = [stemmer.stem(word.lower()) for word in file.split(' ')]
        for word in file.split(' '):
            tem_token.append(stemmer.stem(word.lower()))
            try:
                word = int(word)
                num_count += 1
            except:
                pass

        num_nonwhite_chars.append(len(tem_token))
        num_number.append(num_count)

        #break

    return num_chars, num_nonwhite_chars, num_number, num_positive_words, num_negative_words

def tfidf_feature(pd_dataset, max_features:int, ngram_range, text_corpus, stopwords):

    ### row is the document
    ### column is the term
    #max_features=10,    max_df=0.9, min_df=2 If it is an integer, then it is the absolute number of documents containing that word. If it is a decimal, then it is the proportion of documents containing that word.

    vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=ngram_range, stop_words=stopwords)
    X = vectorizer.fit_transform(text_corpus)
    vectorizer.get_feature_names_out()
    feature_name = vectorizer.get_feature_names_out()
    tfidf = X.toarray()

    for col_idx in range(max_features):

        tem_list = []
        for row_idx in range(len(tfidf)):
            tem_list.append(tfidf[row_idx][col_idx])
        pd_dataset.insert(column=f"feature{col_idx}_{feature_name[col_idx]}", loc=len(pd_dataset.columns.values), value=tem_list)

    return tfidf, pd_dataset, feature_name

def sentiment(pd_dataset):

    # polarity: negative vs. positive -1.0 - 1.0
    # subjectivity: objective vs. subjective 0.0 - 1.0

    polarity_list = []
    subjectivity_list = []
    tokens = list(pd_dataset["token"])

    for token in tqdm(tokens):

        polarity, subjectivity = TextBlob(f"{' '.join(token)}").sentiment
        polarity_list.append(polarity)
        subjectivity_list.append(subjectivity)

        #break

    pd_dataset.insert(column="polarity", loc=len(pd_dataset.columns.values), value=polarity_list)
    pd_dataset.insert(column="subjectivity", loc=len(pd_dataset.columns.values), value=subjectivity_list)

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

    for text in tqdm(raw_text):

        f = fkscore.fkscore(text)
        stat = f.stats
        score = f.score

        num_sentences_list.append(stat["num_sentences"])
        num_syllables_list.append(stat["num_syllables"])

        readability_list.append(score["readability"])
        read_grade_list.append(score["read_grade"])
        calc_grade_list.append(score["calc_grade"])

        #break

    pd_dataset.insert(column="num_sentences", loc=len(pd_dataset.columns.values), value=num_sentences_list)
    pd_dataset.insert(column="num_syllables", loc=len(pd_dataset.columns.values), value=num_syllables_list)
    pd_dataset.insert(column="readability", loc=len(pd_dataset.columns.values), value=readability_list)
    pd_dataset.insert(column="read_grade", loc=len(pd_dataset.columns.values), value=read_grade_list)
    pd_dataset.insert(column="calc_grade", loc=len(pd_dataset.columns.values), value=calc_grade_list)

    return pd_dataset

with open(r"src/stopword_list.txt", "r") as file:
    reader = file.readlines()
    stopword_list = [word.strip() for word in reader]

'''
read guardian metadata
'''

disaster_dataset = pd.read_csv(r"data\news\news_metadata.csv", sep=',', lineterminator='\n')

###
### read guardian text data and match it to guardian metatdata
###

article_path = list(disaster_dataset["path"])

text_content = []
for path in tqdm(article_path):

    with open(f"{path}", "r", encoding='utf-8') as tem_file:
        reader = tem_file.read()
        text_content.append(reader)

disaster_dataset.insert(column="text", loc=len(disaster_dataset.columns.values), value=text_content)
disaster_dataset.columns = ['pub_date', 'title', 'url', 'type', 'title_tokens', 'path', 'text']

'''
    preliminary processing
    word_based tokenization
'''

stemmer = PorterStemmer()

tokens, all_unique_token = tokenization(text_content, stopword_list)
disaster_dataset.insert(column="token", loc=len(disaster_dataset.columns.values), value=tokens)

'''
    Feature extraction
'''

#### basic feature of corpus
num_chars, num_nonwhite_chars, num_number, num_positive_words, num_negative_words = basic_feature_extraction(text_content)
disaster_dataset.insert(column="num_chars", loc=len(disaster_dataset.columns.values), value=num_chars)
disaster_dataset.insert(column="num_nonwhite_chars", loc=len(disaster_dataset.columns.values), value=num_nonwhite_chars)
disaster_dataset.insert(column="num_number", loc=len(disaster_dataset.columns.values), value=num_number)

### tfidf feature
tfidf_matrix, disaster_dataset, feature_name = tfidf_feature(pd_dataset=disaster_dataset, max_features=20, ngram_range=(1, 5), text_corpus=text_content, stopwords=stopword_list)

### sentiment analysis
disaster_dataset = sentiment(pd_dataset=disaster_dataset)

### readability analysis
disaster_dataset = readability(pd_dataset=disaster_dataset)

disaster_dataset.to_csv("feature_dataset.csv", index=False)

'''
    visulization 
'''

xlabels = feature_name[:20]
ylabels = range(len(text_content))
data = tfidf_matrix.tolist()

# 热力图
draw_heatmap(data, xlabels, ylabels)

# 转置数据
transposed_data = tfidf_matrix.T.tolist()

# 堆叠图
draw_stackplot(transposed_data, ylabels, xlabels)

#xlabels=feature_name
#ylabels=list(range(len(text_content)))
#data=X.toarray().tolist()
#draw_heatmap(data, xlabels, ylabels)
#转置维stackflow的格式要求，y轴为字符，x轴为章节
#stackplt方式
#data=X.T.toarray().tolist()
#draw_stackplot(data, ylabels, xlabels



#词云图


from wordcloud import WordCloud

all_text = []
# 将文本内容合并成一个字符串
for token_each_news in list(disaster_dataset["token"]):
    for token in token_each_news:
        all_text.append(token)

all_text = " ".join(all_text)

# 生成词云图
wordcloud = WordCloud(
    background_color="white", 
        width=1500,         
        height=960,             
        margin=10,              
        stopwords=stopword_list
        ).generate(all_text)

# 显示词云图
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()
wordcloud.to_file('disaster_wordcloud.png')

