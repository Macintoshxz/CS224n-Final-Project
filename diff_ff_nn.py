
import tflearn
from tflearn.data_utils import to_categorical, pad_sequences
from tflearn.datasets import imdb
from ingestion import construct_single_feedforward_data
import random
import numpy as np

def splitData(arr, valPercentage, testPercentage):
    n = len(arr)
    valIdx = int(n*valPercentage)
    testIdx = int(n*(1-testPercentage))
    return arr[:valIdx], arr[valIdx:testIdx], arr[testIdx:]


def feedforward(embedding):
    net = tflearn.input_data([None, 2]) #[Batch Size, Sequence Length] Sequence is sliding window length
    net = tflearn.embedding(net, input_dim=len(embedding), output_dim=len(embedding[0]), trainable = True) #Input_Dim = Vocabulary size = #of IDs = #10ks; output_dim = Embedding length
    net = tflearn.fully_connected(net, 200, activation='relu', weights_init = "xavier") #fully_connected is output layer; num units is number of outputs wanted
    net = tflearn.fully_connected(net, 200, activation='relu', weights_init = "xavier") #fully_connected is output layer; num units is number of outputs wanted
    net = tflearn.fully_connected(net, 5, activation='relu', weights_init = "xavier") #fully_connected is output layer; num units is number of outputs wanted
    net = tflearn.regression(net, optimizer='adam', learning_rate=1e-8,
                             loss='categorical_crossentropy', metric = 'Accuracy')
    return net



if __name__ == '__main__':
	X, Y, embedding = construct_single_feedforward_data("check.txt", 50, 2)
	Y = tflearn.data_utils.to_categorical (Y, max(Y) + 1)
	#X = [[x] for x in X]

	# splitIdx = len(X)/5
	trainX, valX, testX = splitData(X, 0.7, 0.1)
	trainY, valY, testY = splitData(Y, 0.7, 0.1)

	net = feedforward(embedding)
	model = tflearn.DNN(net)

	embeddingWeights = tflearn.get_layer_variables_by_name('Embedding')[0]
	model.set_weights(embeddingWeights, embedding)
	model.fit(trainX, trainY, validation_set= (valX, valY), show_metric=True, batch_size=32, n_epoch = 100)

	print(trainY)
	print(model.predict(testX))