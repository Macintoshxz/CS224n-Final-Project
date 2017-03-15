from gensim import utils
from gensim.models.doc2vec import LabeledSentence
from gensim.models import Doc2Vec
import numpy
from random import shuffle
#from sklearn.linear_model import LogisticRegression
import argparse
import os
from os import listdir
from os.path import isfile, join
from split import split_into_sentences
import nltk.data
import string
from nltk.tokenize import word_tokenize
#nltk.download()
import time
import re
from multiprocessing import Pool as ThreadPool
import time 


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
            print "Iter over " + prefix
            with utils.smart_open(source) as fin:
                for item_no, line in enumerate(fin):
                	yield LabeledSentence(word_tokenize(line.strip()), [prefix]) #prefix + '_%s' % item_no
    
    def to_array(self):
        self.sentences = []
        count = 0
        for source, prefix in self.sources.items():
            count = count+1
            print "Extracting vocabulary from: " + prefix + " ::: Document " + str(count) + " of " + str(len(self.sources.items())) 
            with utils.smart_open(source) as fin:
                for item_no, line in enumerate(fin):
                    self.sentences.append(LabeledSentence(word_tokenize(line.strip()), [prefix])) #prefix + '_%s' % item_no
        return self.sentences
    
    def sentences_perm(self):
        shuffle(self.sentences)
        return self.sentences

def get_documents(path):
	documents = {}
	for subdir, dirs, files in os.walk(path):
		for f in files:
			docPath = os.path.join(subdir, f)
			filename, file_extension = os.path.splitext(f)
			if docPath not in documents and filename != ".DS_Store":
				documents[docPath] = filename
				print "Added file " + str(filename) + " to document list."
	return documents
	
def sqeaky_clean(path, squeakypath):
	replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
	replace_digits = string.maketrans(string.digits, ' '*len(string.digits))
	for subdir, dirs, files in os.walk(path):
		for f in files:
			docPath = os.path.join(subdir, f)
			newDocPath = os.path.join(squeakypath, f)
			infile = open(docPath, 'r')
			print newDocPath
			if f != ".DS_Store":
				with open(newDocPath+".tmp", 'w') as tmpfile:
					for line in infile:
						sentences = line.split(". ")
						for s in sentences:
							newline = s.translate(replace_punctuation)
							newline = newline.translate(replace_digits)
							newline = newline.lower()
							#print tmpfile
							tmpfile.write(newline + '\n')
					#filename, file_extension = os.path.splitext(f)	
					os.rename(newDocPath+".tmp", newDocPath)

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Reads directory of financial documents and outputs a model with document word bindings.')
	parser.add_argument('-d','--directory', help='Directory containing financial documents', required=True)
	parser.add_argument('-m','--model', help='Name of Model to train', required=True)
	parser.add_argument('-t','--type', help='10K, 8K, or 10Q', required=True)
	parser.add_argument('-e','--epochs', help='Number of Training Epochs', required=True)
	parser.add_argument('-w','--workers', help='Number of Threads to use when training d2v', required=True)
	parser.add_argument('-c','--company', help='Name of Company associate with documents', required=False)
	parser.add_argument('-s','--squeaky', help="Path to directory to create squeaky clean files.", required=False)
	
	args = vars(parser.parse_args())
	#superfile_path = "/Users/kaikuspa/tensorflow/final/CS224n-Final-Project/Superfiles/" + "_" + args['company'] + '_' + args['type']
	if args['squeaky']:
		sqeaky_clean(args['directory'], args['squeaky'])

	#concatenateFiles(args['directory'], args['company'], args['type'])
	t0 = time.time()
	if args['squeaky']:
		sources = get_documents(args['squeaky'])
	else:
		sources = get_documents(args['directory'])
	t1 = time.time()
	print "Time to get documents: " + str(t1-t0)

	t0 = time.time()
	sentences = LabeledLineSentence(sources)
	t1 = time.time()
	print "Time to get sentences: " + str(t1-t0)

	t0 = time.time()
	model = Doc2Vec(min_count=1, window=5, size=300, sample=1e-4, negative=5, workers=16)	#dm=1
	t1 = time.time()
	print "Time to build model: " + str(t1-t0)

	t0 = time.time()
	#print sentences.to_array()
	model.build_vocab(sentences.to_array())
	t1 = time.time()
	print "Time to build vocab: " + str(t1-t0)

	#print sentences.'''



	for epoch in range(int(args['epochs'])):
		print "Training Model on Epoch " + str(epoch) + " out of " + args['epochs']
		t0 = time.time()
		#print sentences.sentences
		model.train(sentences.sentences_perm())
		t1 = time.time()
		print "Epoch time: " + str(t1-t0)
	model.save(args['model'])



'''
	with open("/Users/kaikuspa/tensorflow/final/CS224n-Final-Project/SP500_vocab.txt", 'w') as outfile:
		for word in model.wv.vocab:
			outfile.write(word)


	with open("/Users/kaikuspa/tensorflow/final/CS224n-Final-Project/SP500_wordvecs.txt", 'w') as outfile:
		for word in model.wv.vocab:
			outfile.write(model[word])

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


'''




