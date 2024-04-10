import pandas as pd
import os
from tqdm import tqdm
from nltk.stem import PorterStemmer
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
from numpy import matrix
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer

stock_data = pd.read_csv(r"data\tel_return\tel_return.csv", sep=',', lineterminator='\n', dtype={"date": str})
#print(stock_data)

feature_date = pd.read_csv(r"feature_dataset.csv", sep=',', lineterminator='\n')
feature_date["date"] = feature_date["pub_date"].str[0:4] + feature_date["pub_date"].str[5:7] + feature_date["pub_date"].str[8:10]
#print(feature_date)

merged_data = pd.merge(stock_data, feature_date, on="date")
merged_data.to_csv(r"data\merged_date.csv", index=False)
print(merged_data)