# -*- coding: utf-8 -*-
"""
Simple example using LSTM recurrent neural network to classify IMDB
sentiment dataset.
References:
    - Long Short Term Memory, Sepp Hochreiter & Jurgen Schmidhuber, Neural
    Computation 9(8): 1735-1780, 1997.
    - Andrew L. Maas, Raymond E. Daly, Peter T. Pham, Dan Huang, Andrew Y. Ng,
    and Christopher Potts. (2011). Learning Word Vectors for Sentiment
    Analysis. The 49th Annual Meeting of the Association for Computational
    Linguistics (ACL 2011).
Links:
    - http://deeplearning.cs.cmu.edu/pdfs/Hochreiter97_lstm.pdf
    - http://ai.stanford.edu/~amaas/data/sentiment/
"""
from __future__ import division, print_function, absolute_import

import tflearn
from tflearn.data_utils import to_categorical, pad_sequences
from tflearn.datasets import imdb
from ingestion import construct_data
import numpy as np

#load data
X, Y, embedding= construct_data("fleet_model.d2v", "/Users/hoyincheung/Desktop/CS224n-final-project/SEC-Edgar-data")

# Data preprocessing
# Sequence padding
trainX = pad_sequences(X, maxlen=20, value=0.)

# Converting labels to binary vectors
trainY = Y


# Network building
net = tflearn.input_data([None, 20])
net = tflearn.embedding(net, input_dim=len(embedding), output_dim=len(embedding[0]))
net = tflearn.lstm(net, 300, dropout=0.8)
net = tflearn.fully_connected(net, 1, activation='linear')
net = tflearn.regression(net, optimizer='adam', learning_rate=0.001,
                         loss='mean_square', metric = 'R2')

# Training
model = tflearn.DNN(net, tensorboard_verbose=3)

# embeddingWeights = tflearn.get_layer_variables_by_name('Embedding')[0]
# # Assign your own weights (for example, a numpy array [input_dim, output_dim])
# model.set_weights(embeddingWeights, embedding)


# model.fit(trainX, trainY, show_metric=True,
#           batch_size=32, n_epoch = 10)
# model.save("rnn")

model.load("rnn")
a = [1,2,3,4,5,6,7,8,9,10,0,0,0,0,0,0,0,0,0,0]
a = np.array(a)
a = a.reshape((-1,20))
print(model.predict(a))
