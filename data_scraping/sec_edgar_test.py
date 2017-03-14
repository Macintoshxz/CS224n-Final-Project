from crawler import SecCrawler 
import time 

def get_filings(): 
	# create object 
	seccrawler = SecCrawler() 
	date = '20170313' # date from which filings should be downloaded 
	# date = '20160922'

	count = '100' # no of filings

	sp_500 = open('sp_500.txt')
	lines = sp_500.readlines()
	sp_500.close()
	companies = [line.split('\t')[1:3] for line in lines]

	companiesToDownload = 10
	scrapeCount = 0
	for companyCode, cik in companies:
		if scrapeCount < 9:
			scrapeCount += 1
			continue
		t1 = time.time() 
		seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "10-K")
		# seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "10-Q")
		# seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "8-K") 
		t2 = time.time() 
		print "Total Time taken for ", companyCode, ": ", str(t2-t1)
		scrapeCount += 1
		if scrapeCount >= companiesToDownload:
			break

if __name__ == '__main__': 
	get_filings()