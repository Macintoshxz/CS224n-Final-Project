<<<<<<< HEAD
import sys
from crawler import SecCrawler
from multiprocessing import Pool as ThreadPool
import time 

def getSingleCompanyFiling(inputData):
	date = '20170315' # date from which filings should be downloaded 
	count = '100' # no of filings

	seccrawler = SecCrawler() 
	companyCode, cik = inputData
	t1 = time.time() 
	seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "10-K")
	# seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "10-Q")
	# seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "8-K") 
	t2 = time.time()
	logString = "Total Time taken for " + companyCode + ": " + str(t2-t1)
	print logString
	return logString

def calculateParallel(inputs, threads=1):
    pool = ThreadPool(threads)
    results = pool.map(getSingleCompanyFiling, inputs)
    pool.close()
    pool.join()
    return results

def get_filings(num_threads, path='sp_500.txt'):
	print 'GETTING FILINGS USING ', num_threads, 'THREADS!!!!!'

	start = time.time()
	companyFile = open(path, 'r')
	lines = companyFile.readlines()
	companyFile.close()

	companies = [line.split('\t')[1:3] for line in lines]
	print 'GETTING THESE COMPANIES:' , companies

	companiesToDownload = 10
	curDownloaded = 0
	blocking = True
	scrapeCount = 0
	queries = [[companyCode, cik] for companyCode, cik in companies]

	results = calculateParallel(queries, num_threads)
	end = time.time()
	print '\n\n\n FINAL TIME:'
	print end - start

def nonthreaded_get_filings():
	# create object 
	print 'getting filings using a single lonely execution thread :(s'
	seccrawler = SecCrawler() 
	date = '20170313' # date from which filings should be downloaded 
	# date = '20160922'

	count = '100' # no of filings

	sp_500 = open('missed_companies2.txt')

	# sp_500 = open('sp_500.txt')
	lines = sp_500.readlines()
	sp_500.close()
	companies = [line.split('\t')[1:3] for line in lines]

	# companies = [line.split('\t')[1:3] for line in lines[2:4]]
	companies = [['FITB', 'FITB']]

	companiesToDownload = 10
	curDownloaded = 0
	blocking = True
	scrapeCount = 0
	
	start = time.time()
	for companyCode, cik in companies:
		# if companyCode != 'A' and blocking:
		# 	scrapeCount += 1
		# 	continue
		# print 'madeit'
		# blocking = False
		# if scrapeCount < curDownloaded:
			# scrapeCount += 1
			# continue

		t1 = time.time() 
		seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "10-K")
		# seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "10-Q")
		# seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "8-K") 
		t2 = time.time() 
		print "Total Time taken for ", companyCode, ": ", str(t2-t1)
		# scrapeCount += 1
		# if scrapeCount >= companiesToDownload:
			# break
	end = time.time()
	print '\n\n\n FINAL TIME:'
	print end - start
	
if __name__ == '__main__':
	threading = sys.argv[1]
	if threading == '-t':
		get_filings(int(sys.argv[2]), sys.argv[3])
	elif threading == '-nt':
		nonthreaded_get_filings()
	else:
		print 'Incorrect arguments.  Should have flag (-t, -nt) for threaded vs. nonthreaded, then numThreads\n' + \
=======
import sys
from crawler import SecCrawler
from multiprocessing import Pool as ThreadPool
import time 

def getSingleCompanyFiling(inputData):
	date = '20170315' # date from which filings should be downloaded 
	count = '100' # no of filings

	seccrawler = SecCrawler() 
	companyCode, cik = inputData
	t1 = time.time() 
	seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "10-K")
	# seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "10-Q")
	# seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "8-K") 
	t2 = time.time()
	logString = "Total Time taken for " + companyCode + ": " + str(t2-t1)
	print logString
	return logString

def calculateParallel(inputs, threads=1):
    pool = ThreadPool(threads)
    results = pool.map(getSingleCompanyFiling, inputs)
    pool.close()
    pool.join()
    return results

def get_filings(num_threads, path='sp_500.txt'):
	print 'GETTING FILINGS USING ', num_threads, 'THREADS!!!!!'

	start = time.time()
	companyFile = open(path, 'r')
	lines = companyFile.readlines()
	companyFile.close()

	companies = [line.split('\t')[1:3] for line in lines]
	print 'GETTING THESE COMPANIES:' , companies

	companiesToDownload = 10
	curDownloaded = 0
	blocking = True
	scrapeCount = 0
	queries = [[companyCode, cik] for companyCode, cik in companies]

	results = calculateParallel(queries, num_threads)
	end = time.time()
	print '\n\n\n FINAL TIME:'
	print end - start

def nonthreaded_get_filings():
	# create object 
	print 'getting filings using a single lonely execution thread :(s'
	seccrawler = SecCrawler() 
	date = '20170313' # date from which filings should be downloaded 
	# date = '20160922'

	count = '100' # no of filings

	sp_500 = open('missed_companies2.txt')

	# sp_500 = open('sp_500.txt')
	lines = sp_500.readlines()
	sp_500.close()
	companies = [line.split('\t')[1:3] for line in lines]

	# companies = [line.split('\t')[1:3] for line in lines[2:4]]
	companies = [['AAPL', 'AAPL']]

	companiesToDownload = 10
	curDownloaded = 0
	blocking = True
	scrapeCount = 0
	
	start = time.time()
	for companyCode, cik in companies:
		# if companyCode != 'A' and blocking:
		# 	scrapeCount += 1
		# 	continue
		# print 'madeit'
		# blocking = False
		# if scrapeCount < curDownloaded:
			# scrapeCount += 1
			# continue

		t1 = time.time() 
		seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "10-K")
		# seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "10-Q")
		# seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "8-K") 
		t2 = time.time() 
		print "Total Time taken for ", companyCode, ": ", str(t2-t1)
		# scrapeCount += 1
		# if scrapeCount >= companiesToDownload:
			# break
	end = time.time()
	print '\n\n\n FINAL TIME:'
	print end - start
	
if __name__ == '__main__':
	threading = sys.argv[1]
	if threading == '-t':
		get_filings(int(sys.argv[2]), sys.argv[3])
	elif threading == '-nt':
		nonthreaded_get_filings()
	else:
		print 'Incorrect arguments.  Should have flag (-t, -nt) for threaded vs. nonthreaded, then numThreads\n' + \
>>>>>>> 9e0815e1dd257578496eebc0a3db052f6aa36c64
			'Nonthreaded is test mode and may not pull everything'