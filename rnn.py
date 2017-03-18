# -*- coding: utf-8 -*-
"""
LSTM Recurrent Neural Network
"""
import tflearn
from tflearn.data_utils import to_categorical, pad_sequences
from tflearn.datasets import imdb
from ingestion import construct_single_feedforward_data
import random


def feedforward():
    net = tflearn.input_data([None, 1]) #[Batch Size, Sequence Length] Sequence is sliding window length
    net = tflearn.embedding(net, input_dim=len(embedding), output_dim=len(embedding[0]), trainable = False) #Input_Dim = Vocabulary size = #of IDs = #10ks; output_dim = Embedding length
    net = tflearn.fully_connected(net, 200, activation='relu', weights_init = "xavier") #fully_connected is output layer; num units is number of outputs wanted
    net = tflearn.fully_connected(net, 200, activation='relu', weights_init = "xavier") #fully_connected is output layer; num units is number of outputs wanted
    net = tflearn.fully_connected(net, 5, activation='relu', weights_init = "xavier") #fully_connected is output layer; num units is number of outputs wanted
    net = tflearn.regression(net, optimizer='adam', learning_rate=0.001,
                             loss='', metric = 'R2')

# def one_layer_LSTM():
    # net = tflearn.input_data([None, 5]) #[Batch Size, Sequence Length] Sequence is sliding window length
    # net = tflearn.embedding(net, input_dim=len(embedding), output_dim=len(embedding[0]), trainable = False) #Input_Dim = Vocabulary size = #of IDs = #10ks; output_dim = Embedding length
    # net = tflearn.lstm(net, 300, dropout=0.8, weights_init = "xavier") #300 refers to size of h_t = Embedding length
    # net = tflearn.fully_connected(net, 1, activation='linear', weights_init = "xavier") #fully_connected is output layer; num units is number of outputs wanted
    # net = tflearn.regression(net, optimizer='adam', learning_rate=0.001,
    #                          loss='mean_square', metric = 'R2')
#     return net

# def two_layer_LSTM():
#     '''
#     WARNING: CANNOT HAVE MORE THAN ONE DYNAMIC LAYER AT THE LAYER CLOSEST TO THE INPUT
#     '''
#     net = tflearn.input_data([None, 5]) #[Batch Size, Sequence Length] Sequence is sliding window length
#     net = tflearn.embedding(net, input_dim=len(embedding), output_dim=len(embedding[0]), trainable = False) #Input_Dim = Vocabulary size = #of IDs = #10ks; output_dim = Embedding length
#     net = tflearn.lstm(net, 300,  dropout = 0.8, weights_init = "xavier", dynamic = True, return_seq = True)
#     net = tflearn.lstm(net, 300,  dropout = 0.8, weights_init = "xavier") #300 refers to size of h_t = Embedding length
#     net = tflearn.fully_connected(net, 1, activation='linear', weights_init = "xavier") #fully_connected is output layer; num units is number of outputs wanted
#     net = tflearn.regression(net, optimizer='adam', learning_rate=0.001,
#                              loss='mean_square', metric = 'R2')
#     return net

# def three_layer_LSTM():
#     '''
#     WARNING: CANNOT HAVE MORE THAN ONE DYNAMIC LAYER AT THE LAYER CLOSEST TO THE INPUT
#     '''
#     net = tflearn.input_data([None, 5]) #[Batch Size, Sequence Length] Sequence is sliding window length
#     net = tflearn.embedding(net, input_dim=len(embedding), output_dim=len(embedding[0]), trainable = False) #Input_Dim = Vocabulary size = #of IDs = #10ks; output_dim = Embedding length
#     net = tflearn.lstm(net, 300,  dropout = 0.8, weights_init = "xavier", dynamic = True, return_seq = True)
#     net = tflearn.lstm(net, 300,  dropout = 0.8, weights_init = "xavier", return_seq = True) #300 refers to size of h_t = Embedding length
#     net = tflearn.lstm(net, 300,  dropout = 0.8, weights_init = "xavier") #300 refers to size of h_t = Embedding length
#     net = tflearn.fully_connected(net, 1, activation='linear', weights_init = "xavier") #fully_connected is output layer; num units is number of outputs wanted
#     net = tflearn.regression(net, optimizer='adam', learning_rate=0.001,
#                              loss='mean_square', metric = 'R2')
#     return net

# def fat_one_layer_LSTM():
#     net = tflearn.input_data([None, 5]) #[Batch Size, Sequence Length] Sequence is sliding window length
#     net = tflearn.embedding(net, input_dim=len(embedding), output_dim=len(embedding[0]), trainable = False) #Input_Dim = Vocabulary size = #of IDs = #10ks; output_dim = Embedding length
#     net = tflearn.lstm(net, 512, dropout=0.8, weights_init = "xavier") #512 refers to size of h_t
#     net = tflearn.fully_connected(net, 1, activation='linear', weights_init = "xavier") #fully_connected is output layer; num units is number of outputs wanted
#     net = tflearn.regression(net, optimizer='adam', learning_rate=0.001,
#                              loss='mean_square', metric = 'R2')
#     return net

# def one_layer_GRU():
#     net = tflearn.input_data([None, 5]) #[Batch Size, Sequence Length] Sequence is sliding window length
#     net = tflearn.embedding(net, input_dim=len(embedding), output_dim=len(embedding[0]), trainable = False) #Input_Dim = Vocabulary size = #of IDs = #10ks; output_dim = Embedding length
#     net = tflearn.gru(net, 300, dropout=0.8, weights_init = "xavier") #512 refers to size of h_t
#     net = tflearn.fully_connected(net, 1, activation='linear', weights_init = "xavier") #fully_connected is output layer; num units is number of outputs wanted
#     net = tflearn.regression(net, optimizer='adam', learning_rate=0.001,
#                              loss='mean_square', metric = 'R2')

#load data
# X, Y, embedding= construct_data("fleet_model.d2v", "/Users/hoyincheung/Desktop/CS224n-final-project/SEC-Edgar-data")
X, Y, embeddings = construct_single_feedforward_data("check.txt", 50)

# Data preprocessing
# Sequence padding
random.seed(1234)
trainX = pad_sequences(X, maxlen=5, value=0.)
trainY = [[random.uniform(-1, 1)] for i in range(len(X))] #PROOF OF CONCEPT

# Training
net = fat_one_layer_LSTM()
model = tflearn.DNN(net, tensorboard_verbose=3)

#insert our doc2vec embeddings here
embeddingWeights = tflearn.get_layer_variables_by_name('Embedding')[0]
model.set_weights(embeddingWeights, embedding)


model.fit(trainX, trainY, validation_set= (trainX, trainY), show_metric=True,
          batch_size=32, n_epoch = 100)

print(trainY)
print(model.predict(trainX))
# model.save("rnn")
