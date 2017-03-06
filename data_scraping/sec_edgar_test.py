from crawler import SecCrawler 
import time 

def get_filings(): 
	t1 = time.time() 

	# create object 
	seccrawler = SecCrawler() 

	companyCode = 'AAPL' # company code for apple 
	cik = '0000320193' # cik code for apple 
	date = '20010227' # date from which filings should be downloaded 
	count = '1' # no of filings 

	seccrawler.filing_10Q(str(companyCode), str(cik), str(date), str(count))
	seccrawler.filing_10K(str(companyCode), str(cik), str(date), str(count))
	# seccrawler.filing_8K(str(companyCode), str(cik), str(date), str(count)) 
	# seccrawler.filing_13F(str(companyCode), str(cik), str(date), str(count)) 

	t2 = time.time() 
	print "Total Time taken: ", 
	print (t2-t1) 

if __name__ == '__main__': 
	get_filings()