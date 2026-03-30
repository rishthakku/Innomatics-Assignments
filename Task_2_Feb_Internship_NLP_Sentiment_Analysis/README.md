# Twitter Sentiment Analysis

This assignment implements a complete NLP pipeline to classify the sentiment of tweets. 

It evaluates and compares three machine learning models: Logistic Regression, Naive Bayes, and Decision Tree—using two text vectorization techniques: Bag of Words (BoW) and TF-IDF.

## Features
* Text Preprocessing: Lowercasing, lemmatization, stop-word, URL, and punctuation removal using NLTK.
* Evaluation: Generates classification reports and bar charts comparing model accuracies using scikit-learn and seaborn.

## Usage
1. Install dependencies: pip install pandas scikit-learn nltk matplotlib seaborn
2. Place twitter_training.csv in the same directory.
3. Run the script to train the models and view the comparative results.