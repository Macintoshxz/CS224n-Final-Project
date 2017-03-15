import os
import pickle
import logging
from collections import Counter

import numpy as np
from util import read_conll, one_hot, window_iterator, ConfusionMatrix, load_word_vector_mapping
# from defs import LBLS, NONE, LMAP, NUM, UNK, EMBED_SIZE

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def load_embeddings(filename):
	'''
	File must containing document vectors per line, where the order of the document vectors 
	correspond to integer indices
	'''
	embeddings = []
	with open(filename) as embeddings_file:
		for vector in embeddings_file:
			embeddings.append(vector)
	return np.array(embeddings)



