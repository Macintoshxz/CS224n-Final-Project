import sys
from crawler import SecCrawler
from multiprocessing import Pool as ThreadPool
import traceback
import os
import time 

def getSingleCompanyFiling(companyCode, logPath='downloaded_companies.txt'):
    date = '20170315' # date from which filings should be downloaded 
    count = '100' # no of filings

    seccrawler = SecCrawler() 
    t1 = time.time()
    try:
        seccrawler.getFiling(str(companyCode), str(date), str(count), "10-K")
    except:
        raise Exception("".join(traceback.format_exception(*sys.exc_info())))
    # seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "10-Q")
    # seccrawler.getFiling(str(companyCode), str(cik), str(date), str(count), "8-K") 
    t2 = time.time()
    logString = "Total Time taken for " + companyCode + ": " + str(t2-t1)
    f = open(logPath, 'a+')
    f.write(companyCode + '\n')
    f.close()
    return logString

def calculateParallel(inputs, func, threads=1):
    pool = ThreadPool(threads)
    results = pool.map(func, inputs)
    pool.close()
    pool.join()
    return results

def get_filings(num_threads, path='sp_500.txt', logPath='downloaded_companies.txt'):
    print 'GETTING FILINGS USING ', num_threads, 'THREADS!!!!!'   

    start = time.time()
    companyFile = open(path, 'r')
    lines = companyFile.readlines()
    companyFile.close()

    companiesSet = set([line.split('\t')[0].strip() for line in lines])

    downloadedCompanies = set([])    
    if os.path.isfile(logPath):
        downloadedFile = open(logPath, 'r')
        downloadedCompanies = set([line.split('\t')[0].strip() for line in downloadedFile.readlines()])
        downloadedFile.close()

    companiesToGet = companiesSet - downloadedCompanies
    print 'GETTING THESE COMPANIES:' , companiesToGet

    results = calculateParallel(companiesToGet, getSingleCompanyFiling, num_threads)
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

def extractSingleSection(inputs):
    companyCode, filingURLList, docNameList, indexURLList, filingType = inputs
    logString = 'Skipping text file.'
    if '.txt' not in filingURLList[0]:
        t1 = time.time() 
        seccrawler = SecCrawler() 
        try:
            seccrawler.save_in_directory(companyCode, filingURLList, docNameList, indexURLList, filingType)        
            # Put all exception text into an exception and raise that

            t2 = time.time()

            completedFilename = 'extraction_log.txt'
            f = open(completedFilename, 'a+')
            f.write(docNameList[0] + '\n')
            f.close()
            logString = "Total Time taken for " + companyCode + "sections: " + str(t2-t1)

        except:
            raise Exception("".join(traceback.format_exception(*sys.exc_info())))
    return logString

def extractSectionFromExistingFilings(numThreads):
    filename = '../check.txt'
    completedFilename = 'extraction_log.txt'
    f = open(completedFilename, 'r')
    completedLines = f.readlines()
    f.close()
    completed = [line.strip() for line in completedLines]

    with open(filename) as check:
        lines = check.readlines()
        readLines = [[line.split('\t')[0].strip(), [line.split('\t')[6].strip()], \
            [line.split('\t')[5].strip()], [line.split('\t')[6].strip()], '10-K'] for line in lines]

    sectionsToGet = []    
    for line in reversed(readLines):
        companyCode, filingURLList, docNameList, indexURLList, filingType = line
        if docNameList[0] not in completed:
            sectionsToGet.append(line)
        else:
            print 'Already downloaded ', docNameList[0]

    if numThreads > 1:
        print 'THREADED'
        results = calculateParallel(sectionsToGet, extractSingleSection, numThreads)
    else:
        print 'NONTHREADED'
        seccrawler = SecCrawler() 

        for lineElem in sectionsToGet:
            companyCode, filingURLList, docNameList, indexURLList, filingType = lineElem
            if '.txt' not in filingURLList[0]:
                seccrawler.save_in_directory(companyCode, filingURLList, docNameList, indexURLList, filingType)            
                f = open(completedFilename, 'a+')
                f.write(docNameList[0] + '\n')
                f.close()
    
if __name__ == '__main__':
    threading = sys.argv[1]
    if threading == '-t':
        get_filings(int(sys.argv[2]), sys.argv[3])
    elif threading == '-nt':
        nonthreaded_get_filings()
    elif threading == '-es':
        extractSectionFromExistingFilings(int(sys.argv[2]))
    else:
        print 'Incorrect arguments.  Should have flag (-t, -nt) for threaded vs. nonthreaded, then numThreads\n' + \
            'Nonthreaded is test mode and may not pull everything'