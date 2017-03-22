
import tflearn
from tflearn.data_utils import to_categorical, pad_sequences
from tflearn.datasets import imdb
from ingestion import construct_single_input_feedforward_from_manifest
from ingestion import construct_dual_input_feedforward_from_manifest
import random
import numpy as np

def splitData(arr, valPercentage, testPercentage):
    n = len(arr)
    valIdx = int(n*valPercentage)
    testIdx = int(n*(1-testPercentage))
    return arr[:valIdx], arr[valIdx:testIdx], arr[testIdx:]


# def feedforward(embedding):
#     net = tflearn.input_data([None, 2]) #[Batch Size, Sequence Length] Sequence is sliding window length
#     net = tflearn.embedding(net, input_dim=len(embedding), output_dim=len(embedding[0]), trainable = True) #Input_Dim = Vocabulary size = #of IDs = #10ks; output_dim = Embedding length
#     net = tflearn.fully_connected(net, 100, activation='relu', weights_init = "xavier", regularizer='L2') #fully_connected is output layer; num units is number of outputs wanted
#     # net = tflearn.fully_connected(net, 30, activation='sigmoid', weights_init = "xavier", regularizer='L2') #fully_connected is output layer; num units is number of outputs wanted

#     # net = tflearn.layers.core.dropout(net, keep_prob=0.9)
#     net = tflearn.fully_connected(net, 100, activation='relu', weights_init = "xavier", regularizer='L2') #fully_connected is output layer; num units is number of outputs wanted
#     net = tflearn.fully_connected(net, 2, activation='softmax', weights_init = "xavier", regularizer='L2') #fully_connected is output layer; num units is number of outputs wanted
#     net = tflearn.regression(net, optimizer='adam', learning_rate=1e-5,
#                              # loss='softmax', metric = 'Accuracy')
#                              loss='categorical_crossentropy', metric = 'Accuracy')

#     return net

def feedforward(embedding):
    net = tflearn.input_data([None, 2]) #[Batch Size, Sequence Length] Sequence is sliding window length
    net = tflearn.embedding(net, input_dim=len(embedding), output_dim=len(embedding[0]), trainable = True) #Input_Dim = Vocabulary size = #of IDs = #10ks; output_dim = Embedding length
    net = tflearn.fully_connected(net, 50, activation='relu', weights_init = "xavier")#, regularizer='L2') #fully_connected is output layer; num units is number of outputs wanted
    # net = tflearn.fully_connected(net, 30, activation='sigmoid', weights_init = "xavier", regularizer='L2') #fully_connected is output layer; num units is number of outputs wanted

    # net = tflearn.layers.core.dropout(net, keep_prob=0.5)
    # net = tflearn.fully_connected(net, 50, activation='relu', weights_init = "xavier", regularizer='L2') #fully_connected is output layer; num units is number of outputs wanted
    net = tflearn.fully_connected(net, 2, activation='softmax', weights_init = "xavier", regularizer='L2') #fully_connected is output layer; num units is number of outputs wanted
    net = tflearn.regression(net, optimizer='adam', learning_rate=1e-5,
                             # loss='softmax', metric = 'Accuracy')
                             loss='categorical_crossentropy', metric = 'Accuracy')

                             # loss='categorical_crossentropy', metric = 'Accuracy')

    return net

if __name__ == '__main__':
	# X, Y, embedding = construct_single_input_feedforward_from_manifest("manifest_50_sign.txt", 0)
	# X, Y, embedding = construct_dual_input_feedforward_from_manifest("manifest_50_embedded.txt")
	X, Y, embedding = construct_dual_input_feedforward_from_manifest("manifest_50_large_median.txt")


	# X, Y, embedding = construct_dual_input_feedforward_from_manifest("manifest_50_21k.txt")

	Y = tflearn.data_utils.to_categorical(Y, max(Y) + 1)
	#X = [[x] for x in X]

	# splitIdx = len(X)/5
	trainX, valX, testX = splitData(X, 0.7, 0.15)
	trainY, valY, testY = splitData(Y, 0.7, 0.15)

	net = feedforward(embedding)
	model = tflearn.DNN(net)

	embeddingWeights = tflearn.get_layer_variables_by_name('Embedding')[0]
	model.set_weights(embeddingWeights, embedding)
	model.fit(trainX, trainY, validation_set= (valX, valY), show_metric=True, batch_size=32, n_epoch = 10)

	print(trainY)
	print()

	pred = model.predict(testX) 

	testLen = len(testX)
	right = 0.0
	for i in xrange(testLen):
		predArr = np.round(pred[i])
		if predArr[0] == testY[i][0]:
			right += 1
	print right / testLen