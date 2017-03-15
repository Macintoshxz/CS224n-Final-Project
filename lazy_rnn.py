import tensorflow as tf
import numpy as np

from ner_model import NERModel

class RNNCell(tf.nn.rnn_cell.RNNCell):
	def __init__(self, input_size, state_size):
		self.input_size = input_size #size of doc vectors
		self._state_size = state_size #size of A1

	def __call__(self, inputs, state, scope=None):
		scope = scope or type(self).__name__
		with tf.variable_scope(scope):
			W_x_initializer = tf.contrib.layers.xavier_initializer()
			W_h_initializer = tf.constant_initializer(np.eye(self.state_size))
			b_initializer = tf.constant_initializer(0)

			W_x = tf.get_variable("W_x", shape=(self.input_size, self.state_size), dtype=np.float32, initializer=W_x_initializer)
			W_h = tf.get_variable("W_h", shape=(self.state_size, self.state_size), dtype=np.float32, initializer=W_h_initializer)
			b = tf.get_variable("b", shape=(self.state_size), dtype=np.float32, initializer=b_initializer)

			Xt_Wx = tf.matmul(inputs,W_x)
			Ht_Wh = tf.matmul(state,W_h)
			new_state = tf.sigmoid(Xt_Wx + Ht_Wh + b)
		# For an RNN , the output and state are the same (N.B. this
		# isn't true for an LSTM, though we aren't using one of those in
		# our assignment)
		output = new_state
		return output, new_state

class Config:
	"""Holds model hyperparams and data information.

	The config class is used to store various hyperparameters and dataset
	information parameters. Model objects are passed a Config() object at
	instantiation.
	"""
	n_word_features = 2 # Number of features for every word in the input.
	window_size = 1
	n_features = (2 * window_size + 1) * n_word_features # Number of features for every word in the input.
	max_length = 83 # SEC begins requiring financial disclosure in 1934, 83 years before present day.
	n_classes = 5
	dropout = 0.5
	embed_size = 300 #from Doc2Vec; will be pulled automatically from pretrained embeddings
	hidden_size = 300 #probs between 300 and 1
	batch_size = 32
	n_epochs = 10
	max_grad_norm = 10.
	lr = 0.001

	def __init__(self, args):
		self.cell = args.cell

		if "output_path" in args:
			# Where to save things.
			self.output_path = args.output_path
		else:
			self.output_path = "results/{}/{:%Y%m%d_%H%M%S}/".format(self.cell, datetime.now())
		self.model_output = self.output_path + "model.weights"
		self.eval_output = self.output_path + "results.txt"
		self.conll_output = self.output_path + "{}_predictions.conll".format(self.cell)
		self.log_output = self.output_path + "log"

def pad_sequences(data, max_length):
	"TODO"


class RNNModel(NERModel):
	"""
	Implements a recursive neural network with an embedding layer and
	single hidden layer.
	This network will predict a sequence of labels (e.g. PER) for a
	given token (e.g. Henry) using a featurized window around the token.
	"""

	def add_placeholders(self):
		"""Generates placeholder variables to represent the input tensors

		These placeholders are used as inputs by the rest of the model building and will be fed
		data during training.  Note that when "None" is in a placeholder's shape, it's flexible
		(so we can use different batch sizes without rebuilding the model).

		Adds following nodes to the computational graph

		input_placeholder: Input placeholder tensor of  shape (None, self.max_length, n_features), type tf.int32
		labels_placeholder: Labels placeholder tensor of shape (None, self.max_length), type tf.int32
		mask_placeholder:  Mask placeholder tensor of shape (None, self.max_length), type tf.bool
		dropout_placeholder: Dropout value placeholder (scalar), type tf.float32

		TODO: Add these placeholders to self as the instance variables
			self.input_placeholder
			self.labels_placeholder
			self.mask_placeholder
			self.dropout_placeholder

		HINTS:
			- Remember to use self.max_length NOT Config.max_length

		(Don't change the variable names)
		"""
		### YOUR CODE HERE (~4-6 lines)
		self.input_placeholder = tf.placeholder(tf.int32, shape=(None, self.max_length)) #int32 because integer tokens to index into word embeddings
		self.labels_placeholder = tf.placeholder(tf.float32, shape=(None, self.max_length))
		self.mask_placeholder = tf.placeholder(tf.bool, shape=(None, self.max_length)) 
		self.dropout_placeholder = tf.placeholder(tf.float32)
		### END YOUR CODE

	def create_feed_dict(self, inputs_batch, labels_batch=None, dropout=1):
		"""Creates the feed_dict for the dependency parser.

		A feed_dict takes the form of:

		feed_dict = {
				<placeholder>: <tensor of values to be passed for placeholder>,
				....
		}

		Hint: The keys for the feed_dict should be a subset of the placeholder
					tensors created in add_placeholders.
		Hint: When an argument is None, don't add it to the feed_dict.

		Args:
			inputs_batch: A batch of input data.
			mask_batch:   A batch of mask data.
			labels_batch: A batch of label data.
			dropout: The dropout rate.
		Returns:
			feed_dict: The feed dictionary mapping from placeholders to values.
		"""
		### YOUR CODE (~6-10 lines)
		feed_dict = {}
		if labels_batch is not None:
			feed_dict[self.labels_placeholder] = labels_batch
		feed_dict[self.input_placeholder] = inputs_batch
		feed_dict[self.mask_placeholder] = mask_batch
		feed_dict[self.dropout_placeholder] = dropout
		### END YOUR CODE
		return feed_dict

	def add_embedding(self):
		"""Adds an embedding layer that maps from input tokens (integers) to vectors and then
		concatenates those vectors:

		TODO:
			- Create an embedding tensor and initialize it with self.pretrained_embeddings.
			- Use the input_placeholder to index into the embeddings tensor, resulting in a
			  tensor of shape (None, max_length, n_features, embed_size).
			- Concatenates the embeddings by reshaping the embeddings tensor to shape
			  (None, max_length, n_features * embed_size).

		HINTS:
			- You might find tf.nn.embedding_lookup useful.
			- You can use tf.reshape to concatenate the vectors. See
			  following link to understand what -1 in a shape means.
			  https://www.tensorflow.org/api_docs/python/array_ops/shapes_and_shaping#reshape.

		Returns:
			embeddings: tf.Tensor of shape (None, max_length, n_features*embed_size)
		"""
		### YOUR CODE HERE (~4-6 lines)
		embeddings = tf.nn.embedding_lookup(tf.Variable(self.pretrained_embeddings), self.input_placeholder)
		m = self.max_length
		n = Config.embed_size
		embeddings = tf.reshape(embeddings, [-1, m, n]) #use -1 to infer the x dimension of embedding tensor
		### END YOUR CODE
		return embeddings

	def add_prediction_op(self):
		"""Adds the unrolled RNN:
			h_0 = 0
			for t in 1 to T:
				o_t, h_t = cell(x_t, h_{t-1})
				o_drop_t = Dropout(o_t, dropout_rate)
				y_t = o_drop_t U + b_2

		TODO: There a quite a few things you'll need to do in this function:
			- Define the variables U, b_2.
			- Define the vector h as a constant and inititalize it with
			  zeros. See tf.zeros and tf.shape for information on how
			  to initialize this variable to be of the right shape.
			  https://www.tensorflow.org/api_docs/python/constant_op/constant_value_tensors#zeros
			  https://www.tensorflow.org/api_docs/python/array_ops/shapes_and_shaping#shape
			- In a for loop, begin to unroll the RNN sequence. Collect
			  the predictions in a list.
			- When unrolling the loop, from the second iteration
			  onwards, you will HAVE to call
			  tf.get_variable_scope().reuse_variables() so that you do
			  not create new variables in the RNN cell.
			  See https://www.tensorflow.org/versions/master/how_tos/variable_scope/
			- Concatenate and reshape the predictions into a predictions
			  tensor.
		Hint: You will find the function tf.pack (similar to np.asarray)
			  useful to assemble a list of tensors into a larger tensor.
			  https://www.tensorflow.org/api_docs/python/array_ops/slicing_and_joining#pack
		Hint: You will find the function tf.transpose and the perms
			  argument useful to shuffle the indices of the tensor.
			  https://www.tensorflow.org/api_docs/python/array_ops/slicing_and_joining#transpose

		Remember:
			* Use the xavier initilization for matrices.
			* Note that tf.nn.dropout takes the keep probability (1 - p_drop) as an argument.
			The keep probability should be set to the value of self.dropout_placeholder

		Returns:
			pred: tf.Tensor of shape (batch_size, max_length, n_classes)
		"""

		x = self.add_embedding()
		dropout_rate = self.dropout_placeholder

		preds = [] # Predicted output at each timestep should go here!

		# Use the cell defined below. For Q2, we will just be using the
		# RNNCell you defined, but for Q3, we will run this code again
		# with a GRU cell!
		if self.config.cell == "rnn":
			cell = RNNCell(Config.embed_size, Config.hidden_size)
		elif self.config.cell == "gru":
			cell = GRUCell(Config.embed_size, Config.hidden_size)
		else:
			raise ValueError("Unsuppported cell type: " + self.config.cell)

		# Define U and b2 as variables.
		# Initialize state as vector of zeros.
		### YOUR CODE HERE (~4-6 lines)
		with tf.variable_scope("LAYER"):
			U_initializer = tf.contrib.layers.xavier_initializer()
			b2_initializer = tf.constant_initializer(0)
			U = tf.get_variable('U', (Config.hidden_size, Config.hidden_size), initializer = U_initializer)	#RxS dimension
			b2 = tf.get_variable('b2', (Config.hidden_size), initializer = b2_initializer)

		h = tf.zeros([1, Config.hidden_size]) #h = state
		### END YOUR CODE

		with tf.variable_scope("RNN"):
			for time_step in range(self.max_length):
				### YOUR CODE HERE (~6-10 lines)
				if time_step > 0:
					tf.get_variable_scope().reuse_variables()
				
				o_t, h = cell(x[:,time_step,:], h, scope="RNN")
				h_dropout = tf.nn.dropout(o_t, dropout_rate)
				output_t = tf.matmul(h_dropout,U) + b2
				preds.append(output_t)
				### END YOUR CODE



		# Make sure to reshape @preds here.
		### YOUR CODE HERE (~2-4 lines)
		'''preds = tf.transpose(tf.pack(preds), perm=[1, 0, 2])'''
		### END YOUR CODE

		#assert preds.get_shape().as_list() == [None, self.max_length, self.config.n_classes], "predictions are not of the right shape. Expected {}, got {}".format([None, self.max_length, self.config.n_classes], preds.get_shape().as_list())
		return preds

	def add_loss_op(self, preds):
		"""Adds Ops for the loss function to the computational graph.

		TODO: Compute averaged cross entropy loss for the predictions.
		Importantly, you must ignore the loss for any masked tokens.

		Hint: You might find tf.boolean_mask useful to mask the losses on masked tokens.
		Hint: You can use tf.nn.sparse_softmax_cross_entropy_with_logits to simplify your
					implementation. You might find tf.reduce_mean useful.
		Args:
			pred: A tensor of shape (batch_size, max_length, n_classes) containing the output of the neural
				  network before the softmax layer.
		Returns:
			loss: A 0-d tensor (scalar)
		"""
		### YOUR CODE HERE (~2-4 lines)
		preds_mask = tf.boolean_mask(preds, self.mask_placeholder)
		labels_mask = tf.boolean_mask(self.labels_placeholder, self.mask_placeholder)
		loss = tf.losses.mean_squared_error(labels_mask, preds, weights = 1.0)
		### END YOUR CODE
		return loss

	def add_training_op(self, loss):
		"""Sets up the training Ops.

		Creates an optimizer and applies the gradients to all trainable variables.
		The Op returned by this function is what must be passed to the
		`sess.run()` call to cause the model to train. See

		https://www.tensorflow.org/versions/r0.7/api_docs/python/train.html#Optimizer

		for more information.

		Use tf.train.AdamOptimizer for this model.
		Calling optimizer.minimize() will return a train_op object.

		Args:
			loss: Loss tensor, from cross_entropy_loss.
		Returns:
			train_op: The Op for training.
		"""
		### YOUR CODE HERE (~1-2 lines)
		train_op = tf.train.AdamOptimizer().minimize(loss)
		### END YOUR CODE
		return train_op

	def __init__(self, helper, config, pretrained_embeddings, report=None):
		super(RNNModel, self).__init__(helper, config, report)
		self.max_length = min(Config.max_length, helper.max_length)
		Config.max_length = self.max_length # Just in case people make a mistake.
		self.pretrained_embeddings = pretrained_embeddings #doc2vecs

		# Defining placeholders.
		self.input_placeholder = None
		self.labels_placeholder = None
		self.mask_placeholder = None
		self.dropout_placeholder = None

		self.build()

def do_train(args):
	# Set up some parameters.
	config = Config(args)
	helper, train, dev, train_raw, dev_raw = load_and_preprocess_data(args)
	embeddings = load_embeddings(args, helper)
	config.embed_size = embeddings.shape[1]
	helper.save(config.output_path)

	handler = logging.FileHandler(config.log_output)
	handler.setLevel(logging.DEBUG)
	handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
	logging.getLogger().addHandler(handler)

	report = None #Report(Config.eval_output)

	with tf.Graph().as_default():
		logger.info("Building model...",)
		start = time.time()
		model = RNNModel(helper, config, embeddings)
		logger.info("took %.2f seconds", time.time() - start)

		init = tf.global_variables_initializer()
		saver = tf.train.Saver()

		with tf.Session() as session:
			session.run(init)
			model.fit(session, saver, train, dev)
			if report:
				report.log_output(model.output(session, dev_raw))
				report.save()
			else:
				# Save predictions in a text file.
				output = model.output(session, dev_raw)
				sentences, labels, predictions = zip(*output)
				predictions = [[LBLS[l] for l in preds] for preds in predictions]
				output = zip(sentences, labels, predictions)

				with open(model.config.conll_output, 'w') as f:
					write_conll(f, output)
				with open(model.config.eval_output, 'w') as f:
					for sentence, labels, predictions in output:
						print_sentence(f, sentence, labels, predictions)


if __name__ == "__main__":
	print "WELCOME TO MODELS AND BOTTLES"
	cell = RNNCell(Config.n_features * Config.embed_size, Config.hidden_size)
	print cell
	config = Config("")
	model = RNNModel(helper, config, embeddings)
	print rnn


