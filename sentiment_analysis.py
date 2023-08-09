# -*- coding: utf-8 -*-
"""Sentiment_Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10w5zKtyBTQr_KXMBQBVokObDEa1TgsK7
"""

#imprort the lobraries

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('ggplot')

import nltk
nltk.download('punkt') # For word tokenizer
nltk.download('averaged_perceptron_tagger') # For pos-tagger
nltk.download('maxent_ne_chunker') # For Chunks
nltk.download('words') # For chunks
nltk.download('vader_lexicon') # For Vader Sentiment Intensity Analyzer

#read the data of 1000 tuples/rows

d=pd.read_csv('/content/Amazon_Reviews.csv')
print(d.shape)

d.head()

#getting a graph for all the ratings from 1 to 5

ax=d['Score'].value_counts().sort_index().plot(kind='bar',title='Count of reviews by syars',figsize=(8,3))
plt.show()

example=d['Text'][50]
print(example)

#Tokenizing the sentences in to list/array of words

tokens=nltk.word_tokenize(example)
tokens[:10]

#giving parts of speech tagging for each word

tagged=nltk.pos_tag(tokens)
tagged[:10]

# grouping the words and its pos tags into a single chunk

entities=nltk.chunk.ne_chunk(tagged)
entities.pprint()

# Vader Sentiment Scoring
# Importing and creating object for SentimentIntensityAnalyzer

from nltk.sentiment import SentimentIntensityAnalyzer
from tqdm.notebook import tqdm

sia=SentimentIntensityAnalyzer()

# Calculating the polarity scores i.e. calculating positive, neutral and negative scores for each word

sia.polarity_scores('I am so happy!')

sia.polarity_scores('This is the worst thing ever')

sia.polarity_scores(example)

# Run the polarity score on the entire dataset

res={}
for i, row in tqdm(d.iterrows(),total=len(d)):
  text=row['Text']
  myid=row['Id']
  res[myid]=sia.polarity_scores(text)

vaders=pd.DataFrame(res).T
vaders=vaders.reset_index().rename(columns={'index': 'Id'})
vaders=vaders.merge(d,how='left')

vaders.head()

ax=sns.barplot(data=vaders,x='Score',y='compound')
ax.set_title("Compound Score by Amazon Star Review")
plt.show()

# Plot between Positive, Neutral and Negative Scores and stars

fig,axs=plt.subplots(1,3,figsize=(12,3))
sns.barplot(data=vaders,x='Score',y='pos',ax=axs[0])
sns.barplot(data=vaders,x='Score',y='neu',ax=axs[1])
sns.barplot(data=vaders,x='Score',y='neg',ax=axs[2])
axs[0].set_title('Positive')
axs[1].set_title('Neutral')
axs[2].set_title('Negative')

# Using Roberta Pretrained Model

!pip install transformers

# Importing libraries

from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax

# Accessing the pretrained model of roberta

MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

# VADER results on example
print(example)
sia.polarity_scores(example)

# Run for Roberta Model
encoded_text = tokenizer(example, return_tensors='pt')
output = model(**encoded_text)
scores = output[0][0].detach().numpy()
scores = softmax(scores)
scores_dict = {
    'roberta_neg' : scores[0],
    'roberta_neu' : scores[1],
    'roberta_pos' : scores[2]
}
print(scores_dict)

def polarity_scores_roberta(example):
    encoded_text = tokenizer(example, return_tensors='pt')
    output = model(**encoded_text)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    scores_dict = {
        'roberta_neg' : scores[0],
        'roberta_neu' : scores[1],
        'roberta_pos' : scores[2]
    }
    return scores_dict

res = {}
for i, row in tqdm(d.iterrows(), total=len(d)):
    try:
        text = row['Text']
        myid = row['Id']
        vader_result = sia.polarity_scores(text)
        vader_result_rename = {}
        for key, value in vader_result.items():
            vader_result_rename[f"vader_{key}"] = value
        roberta_result = polarity_scores_roberta(text)
        both = {**vader_result_rename, **roberta_result}
        res[myid] = both
    except RuntimeError:
        print(f'Broke for id {myid}')

results_d = pd.DataFrame(res).T
results_d = results_d.reset_index().rename(columns={'index': 'Id'})
results_d = results_d.merge(d, how='left')

results_d.columns

sns.pairplot(data=results_d,
             vars=['vader_neg', 'vader_neu', 'vader_pos',
                  'roberta_neg', 'roberta_neu', 'roberta_pos'],
            hue='Score',
            palette='tab10')
plt.show()

# Positive sentiment 1-Star view
results_d.query('Score == 1') \
    .sort_values('roberta_pos', ascending=False)['Text'].values[0]

results_d.query('Score == 1') \
    .sort_values('vader_pos', ascending=False)['Text'].values[0]

# nevative sentiment 5-Star view
results_d.query('Score == 5') \
    .sort_values('roberta_neg', ascending=False)['Text'].values[0]

results_d.query('Score == 5') \
    .sort_values('vader_neg', ascending=False)['Text'].values[0]