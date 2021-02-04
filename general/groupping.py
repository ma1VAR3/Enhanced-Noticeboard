from time import time
# import pandas as pd
import numpy as np
from gensim.models import KeyedVectors
import re
from nltk.corpus import stopwords
# from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, LSTM, Lambda
from tensorflow.keras.optimizers import Adadelta
import tensorflow.keras.backend as K
from tensorflow.keras.callbacks import ModelCheckpoint
import json



stops = set(stopwords.words('english'))
inverse_vocabulary = ['<unk>']

import nltk
# nltk.download('stopwords')

def text_to_word_list(text):
    ''' Pre process and convert texts to a list of words '''
    text = str(text)
    text = text.lower()

    # Clean the text
    text = re.sub(r"[^A-Za-z0-9^,!.\/'+-=]", " ", text)
    text = re.sub(r"what's", "what is ", text)
    text = re.sub(r"\'s", " ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "cannot ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r",", " ", text)
    text = re.sub(r"\.", " ", text)
    text = re.sub(r"!", " ! ", text)
    text = re.sub(r"\/", " ", text)
    text = re.sub(r"\^", " ^ ", text)
    text = re.sub(r"\+", " + ", text)
    text = re.sub(r"\-", " - ", text)
    text = re.sub(r"\=", " = ", text)
    text = re.sub(r"'", " ", text)
    text = re.sub(r"(\d+)(k)", r"\g<1>000", text)
    text = re.sub(r":", " : ", text)
    text = re.sub(r" e g ", " eg ", text)
    text = re.sub(r" b g ", " bg ", text)
    text = re.sub(r" u s ", " american ", text)
    text = re.sub(r"\0s", "0", text)
    text = re.sub(r" 9 11 ", "911", text)
    text = re.sub(r"e - mail", "email", text)
    text = re.sub(r"j k", "jk", text)
    text = re.sub(r"\s{2,}", " ", text)

    text = text.split()
    return text


res = []
def inference(questions):
    with open('general/vocab.json') as f:
        vocabulary = json.load(f)
    stops = set(stopwords.words('english'))
    inverse_vocabulary = ['<unk>']
    for question in questions:
        q2n = []  # q2n -> question numbers representation
        for word in text_to_word_list(question):
        # Check for unwanted word
        #if word in stops and word not in word2vec.vocab:
        # continue
            if word not in vocabulary:
                vocabulary[word] = len(inverse_vocabulary)
                q2n.append(len(inverse_vocabulary))
                inverse_vocabulary.append(word)
            else:
                q2n.append(vocabulary[word])
        print(q2n)
        res.append(q2n)
    return res


def pad(arr):
  arr = np.asarray(arr, np.int32)
  pad = np.zeros((213,))
  shape = arr.shape[0]
  pad[-shape:] = arr
  return pad


def pad_questions(user_question):
    result = []
    for i in range(len(res)):
        temp = pad(res[i])
        result.append(temp)
    return result

def exponent_neg_manhattan_distance(left, right):
    ''' Helper function for the similarity estimate of the LSTMs outputs'''
    return K.exp(-K.sum(K.abs(left-right), axis=1, keepdims=True))

def get_embeddings():
    embed = np.load('general\data.npy')
    return embed

def create_model(embeddings):
    n_hidden = 50
    gradient_clipping_norm = 1.25
    batch_size = 64
    n_epoch = 25
    max_seq_length = 213
    embedding_dim = 300

    # The visible layer
    left_input = Input(shape=(max_seq_length,), dtype='int32')
    right_input = Input(shape=(max_seq_length,), dtype='int32')

    embedding_layer = Embedding(len(embeddings), embedding_dim, weights=[embeddings], input_length=max_seq_length, trainable=False)

    # Embedded version of the inputs
    encoded_left = embedding_layer(left_input)
    encoded_right = embedding_layer(right_input)

    # Since this is a siamese network, both sides share the same LSTM
    shared_lstm = LSTM(n_hidden)

    left_output = shared_lstm(encoded_left)
    right_output = shared_lstm(encoded_right)

    # Calculates the distance as defined by the MaLSTM model
    malstm_distance = Lambda(function=lambda x: exponent_neg_manhattan_distance(x[0], x[1]),output_shape=lambda x: (x[0][0], 1))([left_output, right_output])

    optimizer = Adadelta(clipnorm=gradient_clipping_norm)
    # Pack it all up into a model
    malstm = Model([left_input, right_input], [malstm_distance])
    malstm.compile(loss='mean_squared_error', optimizer=optimizer, metrics=['accuracy'], run_eagerly = True)

    return malstm

def load_pretrained(embeddings):
  model = create_model(embeddings)
  model.load_weights('general\model.h5')
  return model



def checkSemantics(question1, question2):
    questions = []
    res =[]
    questions.append(question1)
    questions.append(question2)
    op_len =  max([len(i.split(' ')) for i in questions])
    print(op_len)
    res = inference(questions)
    print(res)
    result = pad_questions(res)
    return result,op_len

def formatOutput(prediction,op_len):
    final_score = np.sum(prediction[-op_len:]) / op_len
    isSimilar = False
    if(final_score > 0.4):
        isSimilar = True
    return isSimilar
