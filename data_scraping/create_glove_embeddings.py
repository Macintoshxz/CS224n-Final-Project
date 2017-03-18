import sys
import re
from multiprocessing.pool import ThreadPool
from multiprocessing import Manager
import time 
import numpy as np
import string
import os
from functools import partial
import pickle

replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
replace_digits = string.maketrans(string.digits, ' '*len(string.digits))


# Actually formats, then converts a string to
# an embedding.
def stringToEmbedding(s):

	s = s.lower()
	s = s.translate(replace_punctuation)
	s = s.translate(replace_digits)
	s = re.sub(r'\s+', ' ', s)

	tokens = s.split(' ')
	numTokens = len(tokens)
	tokenVals = np.array([gloveDict.get(token, 0) for token in tokens])
	tokenAverage = np.mean(tokenVals, axis=0)
	return tokenAverage

# This is top-level to play nice with multiprocessing - 
# pass it a gloveDict to open the file.

def createSingleEmbedding(targetPath):
	filename = targetPath.split('\\')[-1]

	file_10k = open(targetPath, 'r')
	fileString = file_10k.read()
	file_10k.close()

	# embedding = stringToEmbedding(fileString, gloveDict)
	embedding = stringToEmbedding(fileString)

	print 'embedded', filename
	return [filename, embedding]

# def loopEmbeddings(targetPaths):

# 	outputs = []
# 	for targetPath in targetPaths:
# 		output = createSingleEmbedding(targetPath)
# 		# output = createSingleEmbedding(gloveDict, targetPath)
# 		outputs.append(output)
# 	return outputs

class EmbeddingCreator():
	# Class variable to be shared
	global gloveDict

	def __init__(self):
		self.hello = "Let's create some embeddings"

	# def calculateParallel(self, inputs, threads=1):
	# 	pool = ThreadPool(threads)
	# 	inputs = self.chunkLists(inputs, threads)
	# 	# func = partial(createSingleEmbedding, self.gloveDict)
	# 	# func = partial(loopEmbeddings, d)
	# 	results = pool.map(loopEmbeddings, inputs)
	# 	# results = pool.map(func, inputs)
	# 	pool.close()
	# 	pool.join()
	# 	return results

	def chunkLists(self, targetFiles, n):
	    """Yield successive n-sized chunks from l."""
	    for i in range(0, len(targetFiles), n):
	        yield targetFiles[i:i + n]

	# Opens up the given glove file in the path, creates
	# dictionary to be shared as we're doing things.
	def createGloveDict(self, gloveDim='50'):
		glovePath = "glove/glove.6B." + gloveDim + 'd.txt'

		global gloveDict
		if not os.path.isfile('/glovegloveDict_' + gloveDim + '.pkl'):
			print 'Creating new gloveDict'
			newGloveDict = {}
			gloveFile = open(glovePath)
			lines = gloveFile.readlines();
			gloveFile.close()

			for line in lines:
			    split = line.split()
			    word = split[0]
			    embedding = np.float32(split[1:])
			    newGloveDict[word] = embedding

			gloveDict = newGloveDict
			pickle.dump(gloveDict, open('glove/gloveDict_' + gloveDim + '.pkl', "wb+" ) )
		else:
			print 'Loading gloveDict'
			gloveDict = pickle.load(open('glove/gloveDict_' + gloveDim + '.pkl'))

		return gloveDict

	# def makeGloveDirectories(self, companyCodes):
	# 	for companyCode in companyCodes:
	# 		if not os.path.exists("SEC-Edgar-data/"+str(companyCode)+"/glove"):
	# 			os.makedirs("SEC-Edgar-data/"+str(companyCode)+"/glove")


	# Manages calling of other functions.  Gets all appropriate files to embed,
	# then decides which threading format to use to get the embedding dictionary.
	# Saves the output into a pickle.
	def createEmbeddings(self, gloveDim='50', path="SEC-Edgar-data/"):
		startDict = time.time()
		self.gloveDict = self.createGloveDict(gloveDim)
		endDict = time.time()
		print "Creating dict took:", endDict - startDict, "seconds."
		embeddingDict = {}
		targetPaths = []
		start = time.time()
		for subdir, dirs, files in os.walk(path):
			for f in files:
				docPath = os.path.join(subdir, f)
				targetPaths.append(docPath)

		totalPaths = len(targetPaths)
		# targetPaths = targetPaths[:100]
		# print 'total paths: ', str(totalPaths)
		# if num_threads == 1:
		# 	print 'SINGLE THREAD'
		counter = 0
		results = [createSingleEmbedding(targetPath) for targetPath in targetPaths]
		for result in results:
			filename = result[0]
			embedding = result[1]
			embeddingDict[filename] = embedding
			# for targetFile in targetPaths:
			# 	if counter % 50 == 0:
			# 		print '\nFinished', str(counter), '/', str(totalPaths), 'in', str(time.time() - start), '\n'
			# 	# filename, embedding = createSingleEmbedding(self.gloveDict, targetFile)
			# 	filename, embedding = createSingleEmbedding(targetFile)
			# 	counter += 1

			# 	embeddingDict[filename] = embedding
		# else:
		# 	print 'MULTITHREAD'
		# 	results = self.calculateParallel(targetPaths, num_threads)
		# 	for result in results:
		# 		for filename, embedding in result:
		# 			embeddingDict[filename] = embedding

		pickle.dump(embeddingDict, open( "../embeddingDicts/embeddingDict_" + gloveDim + ".pkl", "wb+" ) )
		end = time.time()
		print '\n\n\n FINAL TIME:'
		print end - start

	def testEmbeddings(self, gloveDim):
		self.gloveDict = self.createGloveDict(gloveDim)
		s1 = 'a'
		s2 = 'a a'
		print stringToEmbedding(s1)
		print stringToEmbedding(s2)

	
# argv[1] = gloveDim
if __name__ == '__main__':
	embeddingCreator = EmbeddingCreator()
	embeddingCreator.createEmbeddings(sys.argv[1])
	# embeddingCreator.testEmbeddings()