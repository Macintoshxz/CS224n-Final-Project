from gensim import utils
from gensim.models.doc2vec import LabeledSentence
from gensim.models import Doc2Vec
import numpy
from random import shuffle
#from sklearn.linear_model import LogisticRegression
import argparse
from os import listdir
from os.path import isfile, join
from split import split_into_sentences
import nltk.data
import string
from nltk.tokenize import word_tokenize
#nltk.download()
import time




def concatenateFiles(path, company, secType):
	filenames = [f for f in listdir(path) if isfile(join(path, f))]
	superfile = str(path + "/_" + company + '_' + secType)
	superfname = str("_" + company + '_' + secType)
	if superfname in filenames:
		filenames.remove(superfname)
	print filenames

	with open(path + "/_" + company + '_' + secType, 'w') as outfile:
	    for fname in filenames:
	        with open(path + "/" + fname) as infile:
	            for line in infile:
	                outfile.write(line)
	formatSuperfile(superfile, superfname)



def formatSuperfile(superfile, superfname):
	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	fp = open(superfile)
	data = fp.read()
	with open("/Users/kaikuspa/tensorflow/final/CS224n-Final-Project/Superfiles/" + superfname, 'w') as outfile:
		formatted = []
		for sentence in tokenizer.tokenize(data):		
			formatted.append(sentence.translate(None, string.punctuation).lower())
		outfile.write('\n'.join(formatted))

	fp.close()


class LabeledLineSentence(object):
    def __init__(self, sources):
        self.sources = sources
        
        flipped = {}
        
        # make sure that keys are unique
        for key, value in sources.items():
            if value not in flipped:
                flipped[value] = [key]
            '''else:
                raise Exception('Non-unique prefix encountered')'''
    
    def __iter__(self):
        for source, prefix in self.sources.items():
            with utils.smart_open(source) as fin:
                for item_no, line in enumerate(fin):
                	print line
                	yield LabeledSentence(word_tokenize(line.strip()), [source]) #prefix + '_%s' % item_no
    
    def to_array(self):
        self.sentences = []
        for source, prefix in self.sources.items():
            with utils.smart_open(source) as fin:
                for item_no, line in enumerate(fin):
                    self.sentences.append(LabeledSentence(word_tokenize(line.strip()), [source])) #prefix + '_%s' % item_no
        return self.sentences
    
    def sentences_perm(self):
        shuffle(self.sentences)
        return self.sentences


	

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Reads directory of financial documents and outputs a model with document word bindings.')
	parser.add_argument('-d','--directory', help='Directory containing financial documents', required=True)
	parser.add_argument('-c','--company', help='Name of Company associate with documents', required=True)
	parser.add_argument('-t','--type', help='10K, 8K, or 10Q', required=True)
	args = vars(parser.parse_args())
	superfile_path = "/Users/kaikuspa/tensorflow/final/CS224n-Final-Project/Superfiles/" + "_" + args['company'] + '_' + args['type']

	#concatenateFiles(args['directory'], args['company'], args['type'])
	sources = {superfile_path: "TEST" } #fill with one superfile per company, gives us word embeddings in the context of particular company.
	sentences = LabeledLineSentence(sources)

	model = Doc2Vec(min_count=1, window=10, size=300, sample=1e-4, negative=5, workers=8, dm = 1)
	t0 = time.time()
	#print sentences.to_array()
	model.build_vocab(sentences.to_array())
	t1 = time.time()
	print "Time is " + str(t1-t0)

	#print sentences.'''

	for epoch in range(20):
		print "Training Model"
		t0 = time.time()
		#print sentences.sentences
		model.train(sentences.sentences_perm())
		t1 = time.time()
		print "Epoch time: " + str(t1-t0)
	model.save('./SP500.d2v')

	with open("/Users/kaikuspa/tensorflow/final/CS224n-Final-Project/SP500_vocab.txt", 'w') as outfile:
		for word in model.wv.vocab:
			outfile.write(word)


	with open("/Users/kaikuspa/tensorflow/final/CS224n-Final-Project/SP500_wordvecs.txt", 'w') as outfile:
		for word in model.wv.vocab:
			outfile.write(model[word])










