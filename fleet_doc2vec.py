from gensim import utils
from gensim.models.doc2vec import LabeledSentence
from gensim.models import Doc2Vec
import gensim
import numpy
import argparse
import os
import time
#, encoding="iso-8859-1"

def get_documents(path):
	corpus = open(path+"/corpus.txt", 'w')
	c_dict = {}
	for subdir, dirs, files in os.walk(path):
		for f in files:
			if f != ".DS_Store" and f != "corpus.txt":
				docPath = os.path.join(subdir, f)
				infile = open(docPath, 'r')
				string = ""
				for line in infile:
					string += line.strip() + " "
				c_dict[f] = string
	return c_dict

def read_corpus(c_dict):
    for key in c_dict:
    	print key
    	yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(c_dict[key]), [key])
 

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Reads directory of financial documents and outputs a model with document word bindings.')
	parser.add_argument('-d','--directory', help='Directory containing financial documents', required=True)
	args = vars(parser.parse_args())

	sources = get_documents(args['directory'])
	train_corpus = list(read_corpus(sources))
	#print train_corpus[:2]

	model = gensim.models.doc2vec.Doc2Vec(size=300, min_count=2, iter=15, workers=8)

	t0 = time.time()
	model.build_vocab(train_corpus)
	t1 = time.time()
	print "Time to get vocab: " + str(t1-t0)

	t0 = time.time()
	model.train(train_corpus)
	t1 = time.time()
	print "Time to train: " + str(t1-t0)

	model.save("fleet_model.d2v")




