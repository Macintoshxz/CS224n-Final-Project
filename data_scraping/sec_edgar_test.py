from crawler import SecCrawler 
import time 

def get_filings(): 
	# create object 
	seccrawler = SecCrawler() 
	date = '20170307' # date from which filings should be downloaded 
	date = '20160922'

	count = '1' # no of filings

	sp_500 = open('sp_500.txt')
	lines = sp_500.readlines()
	sp_500.close()
	companies = [line.split('\t')[1:3] for line in lines]

	for companyCode, cik in companies:
		t1 = time.time() 
		seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "10-K")
		# seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "10-Q")
		# seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "8-K") 
		t2 = time.time() 
		print "Total Time taken for ", companyCode, ": ", str(t2-t1)
		break

if __name__ == '__main__': 
	get_filings()