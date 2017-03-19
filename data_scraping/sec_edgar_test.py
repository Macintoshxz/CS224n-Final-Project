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
    print 'getting filings using a single lonely execution thread :('
    seccrawler = SecCrawler() 
    date = '20170313' # date from which filings should be downloaded 
    # date = '20160922' 

    count = '100' # no of filings

    # sp_500 = open('missed_companies2.txt')

    sp_500 = open('sp_500.txt')
    lines = sp_500.readlines()
    sp_500.close()
    companies = [line.split('\t')[1:3] for line in lines[100:]]

    # OVERRIDES FOR TESTING
    # companies = [line.split('\t')[1:3] for line in lines[2:4]]
    # companies = [['AMZN', 'AMZN']]
    
    start = time.time()
    for companyCode, cik in companies:
        t1 = time.time() 
        seccrawler.getFiling(str(companyCode), str(date), str(count), "10-K")
        # seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "10-Q")
        # seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "8-K") 
        t2 = time.time() 
        print "Total Time taken for ", companyCode, ": ", str(t2-t1)
    end = time.time()
    print '\n\n\n FINAL TIME:'
    print end - start


def extractSectionFromExistingFilings():
    filename = '../check.txt'
    seccrawler = SecCrawler() 
    with open(filename) as check:
        lines = check.readlines()
        lineElems = [[line.split('\t')[0].strip(), [line.split('\t')[6].strip()], \
            [line.split('\t')[5].strip()], [line.split('\t')[6].strip()], '10-K'] for line in lines]

    count = 0
    for lineElem in lineElems:
        companyCode, filingURLList, docNameList, indexURLList, filingType = lineElem
        if '.txt' not in filingURLList[0]:
            seccrawler.save_in_directory(companyCode, filingURLList, docNameList, indexURLList, filingType)
            
            if count >= 10:
                break
            count += 1

    
if __name__ == '__main__':
    threading = sys.argv[1]
    if threading == '-t':
        get_filings(int(sys.argv[2]), sys.argv[3])
    elif threading == '-nt':
        nonthreaded_get_filings()
    elif threading == '-es':
        extractSectionFromExistingFilings()
    else:
        print 'Incorrect arguments.  Should have flag (-t, -nt) for threaded vs. nonthreaded, then numThreads\n' + \
            'Nonthreaded is test mode and may not pull everything'