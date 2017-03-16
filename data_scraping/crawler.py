# This script will download all the 10-K, 10-Q and 8-K 
# provided that of company symbol and its cik code.

from bs4 import BeautifulSoup
import re
import requests
import os
import time


class SecCrawler():

    REQUEST_SLEEP_TIME = 600
    HTTP_OKAY = 200
    ERROR_FILENAME = 'error_log.txt'

    def __init__(self):
        self.hello = "Welcome to Sec Cralwer!"

    def repeatRequest(self, target_url):
        r = requests.get(target_url)
        acceptable_errors = [404]
        while r.status_code != self.HTTP_OKAY:
            if r.status_code in acceptable_errors:
                print r.status_code, ": ", target_url, ""
                return None
            print r.status_code, ": ", target_url, ".  Sleeping for ", self.REQUEST_SLEEP_TIME, "..."
            time.sleep(self.REQUEST_SLEEP_TIME)
            r = requests.get(target_url)
        print r.status_code, ": ", target_url
        return r

    def make_directory(self, companyCode, cik, priorto, filingType):
        # Making the directory to save comapny filings
        if not os.path.exists("SEC-Edgar-data/"):
            os.makedirs("SEC-Edgar-data/")
        if not os.path.exists("SEC-Edgar-data/"+str(companyCode)):
            os.makedirs("SEC-Edgar-data/"+str(companyCode))
        if not os.path.exists("SEC-Edgar-data/"+str(companyCode)+"/"+str(filingType)):
            os.makedirs("SEC-Edgar-data/"+str(companyCode)+"/"+str(filingType))

    def parseData(self, soup):
        decomposeList = ["table", "a"]
        for toDecompose in soup.findAll(decomposeList):
            toDecompose.decompose()
            toDecompose.extract()
        return soup

    #Takes in an array of strings from BS4 and identifies the sentence with the market cap
    def findMarketCapText(self, strings):
        MAX_DOT_LOOKAHEAD = 10
        MAX_DOT_LOOKBEHIND = 5
        MAX_LINES_LOOKAHEAD = 5
        MAX_LINES_LOOKBEHIND = 3

        def createSnippets(lineParts, strings, i):
            nextLines = ' '.join(strings[min(i + 1, len(strings) - 1): min(i + MAX_LINES_LOOKAHEAD, len(strings) - 1)]).split('.')
            nextLines = nextLines[:min(MAX_DOT_LOOKAHEAD, len(nextLines) - 1)]
            prevLines = ' '.join(strings[max(0, i-MAX_LINES_LOOKBEHIND)]).split('.')
            prevLines = prevLines[min(-MAX_DOT_LOOKBEHIND, -(len(prevLines)-1)):]
            line = ' '.join(prevLines + lineParts + nextLines)
            snippets = self.findPotentialMarketCapSentences(line.lower())
            return snippets, line

        SEARCH_TERMS = [["aggregate market value"], ["common stock", "market value"], \
            ["aggregate", "market", "value", "$"], ["aggregate", "value", "$"], ["aggregate", "value", "$"], \
            ["common stock", "$"],  ["aggregate", "market", "value"], ["common stock"]]

        for searchList in SEARCH_TERMS:
            for i in xrange(len(strings)):
                line = strings[i].lower()
                # print line
                searchFound = True
                for term in searchList:
                    if term not in line:
                        searchFound = False
                        break
                if searchFound:
                    idx = line.find(searchList[0])
                    lineStart = line[:idx]
                    lineEnd = line[idx:]
                    lineParts = [lineStart, lineEnd]
                    marketCapSnippets, searchedLine = createSnippets(lineParts, strings, i)
                    if len(marketCapSnippets) > 0:
                        print "Pulling from searchList:", searchList
                        print searchedLine
                        # print marketCapSnippets
                        return marketCapSnippets
        return None

    def convertTextToAmount(self, text):
        amounts = []
        for textElem in text:
            if not textElem:
                continue
            if isinstance(textElem, list):
                textElem = textElem[0]
            if isinstance(textElem, tuple):
                textElem = textElem[0]
            # print 'TEXTELEM: ', textElems
            amount = re.findall(r'(\d{1,3}(,\d{3})*(\.\d+)?)', textElem)
            if len(amount) == 0:
                continue
            amount = amount[0]
            amount = amount[0].strip().replace(',','')
            amount = amount.strip('.')
            # print 'Amount: ', amount
            multiplier = 1
            if 'billion' in textElem:
                multiplier = 1000000000
            if 'million' in textElem:
                multiplier = 1000000
            finalAmount = float(amount)*multiplier
            amounts.append(finalAmount)
            # print finalAmount
        if len(amounts) == 0:
            return -1
        return max(amounts)

    def findPotentialMarketCapSentences(self, sentence):
        #Consolidate all the likely cases for finding the market cap.
        #If you're wondering why 'illion' is split up - some fuckers put newlines in the middle of
        #the motherfucking goddamn word.
        # potentialMarketCaps = re.findall(r'was\s*\$ *((\d{1,3}(,\d{3})*(\.\d+)?) *[mb]ill?i?o?n?(?i))', sentence)
        # potentialMarketCaps.append(re.findall(r'approximately\s*\$ *((\d{1,3}(,\d{3})*(\.\d+)?) *[mb]ill?i?o?n?(?i))', sentence))
        # potentialMarketCaps.append(re.findall(r':\s*\$ *((\d{1,3}(,\d{3})*(\.\d+)?) *[mb]ill?i?o?n?(?i))', sentence))
        # potentialMarketCaps.append(re.findall(r'was\s*\$ *((\d{1,3}(,\d{3})*(\.\d+)?))', sentence))
        # potentialMarketCaps.append(re.findall(r'approximately\s*\$ *((\d{1,3}(,\d{3})*(\.\d+)?))', sentence))
        # potentialMarketCaps.append(re.findall(r':\s*\$ *((\d{1,3}(,\d{3})*(\.\d+)?))', sentence))
        # potentialMarketCaps.append(re.findall(r'approximately\s*\$ *((\d{1,3}(,\d{3})*(\.\d+)?) *[mb]ill?i?o?n?(?i))', sentence))
        # potentialMarketCaps.append(re.findall(r'\$? *((\d{1,3}(,\d{3})*(\.\d+)?))', sentence))

        #New spacing between dots
        potentialMarketCaps = re.findall(r'was\s*\$ *((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?)\s*[mb]ill?i?o?n?(?i))', sentence)
        potentialMarketCaps.append(re.findall(r'approximately\s*\$ *((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?) *[mb]ill?i?o?n?(?i))', sentence))
        potentialMarketCaps.append(re.findall(r':\s*\$ *((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?)\s*[mb]ill?i?o?n?(?i))', sentence))
        potentialMarketCaps.append(re.findall(r'was\s*\$ *((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?))', sentence))
        potentialMarketCaps.append(re.findall(r'approximately\s*\$ *((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?))', sentence))
        potentialMarketCaps.append(re.findall(r':\s*\$ *((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?))', sentence))
        potentialMarketCaps.append(re.findall(r'approximately\s*\$ *((\d{1,3}(,\d{3})*(\s*\.\s*\d+)?) *[mb]ill?i?o?n?(?i))', sentence))
        potentialMarketCaps.append(re.findall(r'\$? *((\d{1,3}(\s*,\d{3})*(\.\d+)?))', sentence))

        #If we still have nothing, check more unlikely cases
        # if len(potentialMarketCaps) is 0:
        #     potentialMarketCaps = re.findall(r'\$? *((\d{1,3}(,\d{3})*(\.\d+)?) *[mb]ill?i?o?n?(?i))', sentence)
        # if len(potentialMarketCaps) is 0:
        #     potentialMarketCaps = re.findall(r'approximately\s*\$? ((\d{1,3}(,\d{3})*(\.\d+)?))', sentence)
        # if len(potentialMarketCaps) is 0:
        #     potentialMarketCaps = re.findall(r'was\s*\$? *((\d{1,3}(,\d{3})*(\.\d+)?))', sentence)
        # if len(potentialMarketCaps) is 0:
        #     potentialMarketCaps = re.findall(r'\$ *((\d{1,3}(,\d{3})*(\.\d+)?))', sentence)

        #New spacing between dots
        if len(potentialMarketCaps) is 0:
            potentialMarketCaps = re.findall(r'\$? *((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?)\s*[mb]ill?i?o?n?(?i))', sentence)
        if len(potentialMarketCaps) is 0:
            potentialMarketCaps = re.findall(r'approximately\s*\$? ((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?))', sentence)
        if len(potentialMarketCaps) is 0:
            potentialMarketCaps = re.findall(r'was\s*\$? *((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?))', sentence)
        if len(potentialMarketCaps) is 0:
            potentialMarketCaps = re.findall(r'\$ *((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?))', sentence)

        potentialMarketCaps = [item for sublist in potentialMarketCaps for item in sublist]
        return potentialMarketCaps

    def getCombinedLineArray(self, lines, numLines=-1):
        curLine = ""
        outArray= []
        lineCounter = 0
        for line in lines:
            found = re.findall('\.\s*$', line)
            curLine += line.strip() + " "
            if len(found) != 0:                
                curLine = curLine.replace("?", " ")
                curLine = re.sub(r'\s\s+', ' ', curLine)
                curLine = curLine.replace("\n", " ")
                outArray.append(curLine)
                curLine = ""
                lineCounter += 1
                if lineCounter > numLines and numLines != -1:
                    break
        return outArray

    def truncateDocumentData(self, data):
        strings = data.split('\n')
        endIdx = len(strings)
        for i in xrange(len(strings)):
            s = strings[i]
            if '</DOCUMENT>' in s:
                endIdx = i
                break
        strings = strings[:endIdx]
        newData = '\n'.join(strings)

        return newData

    def save_in_directory(self, companyCode, cik, priorto, filingURLList, docNameList, indexURLList, filingType):
        # Save every text document into its respective folder
        for i in range(len(filingURLList)):
            path = "SEC-Edgar-data/"+str(companyCode)+"/"+str(filingType)+"/"+str(docNameList[i])

            # Don't overwrite existing, non-text root files
            # if os.path.isfile(path):
            # #     #Fixing weird .txt downloads
            #     # f = open(path, 'r')
            #     # original_filetype = f.readline().split('.')[-1]
            #     # f.close()
            # #     ##TODO: Remove the following after we actually fix things
            # #     print 'Original filetype:', original_filetype
            #     # if 'txt' not in original_filetype:
            #     print "ALREADY EXISTS: ", path, ', moving on...'
            #     continue

            t1 = time.time()
            target_url = filingURLList[i]
            #Removes interactive XBRL
            target_url = target_url.replace('ix?doc=/', '')
            index_url = indexURLList[i]
            print "Saving", target_url
            print "From index:", index_url

            r = self.repeatRequest(target_url)
            if r is None:
                errorFile = open(self.ERROR_FILENAME, 'a+')
                errorFile.write('404 FROM: ' + target_url + '\n')
                errorFile.close()
                continue
            data = r.text

            #Attempt normal parsing.  If this fails, try truncating and parsing again
            #If this fails AGAIN, just ignore it completely.
            def ingestSoup(data, shouldParse=False):
                soup = None
                rawStrings = None
                parsedStrings = None

                try:
                    soup = BeautifulSoup(data, "lxml")
                    soup = BeautifulSoup(soup.prettify(), "lxml")
                    if '.txt' in target_url:
                        rawStrings = [s.encode('ascii', 'replace') for s in soup.get_text().split('\n') if s.strip() != '']
                    else:
                        rawStrings = [s.encode('ascii', 'replace') for s in soup.strings if s.strip() != '']

                    soup = self.parseData(soup)
                    if '.txt' in target_url:
                        parsedStrings = [s.encode('ascii', 'replace') for s in soup.get_text().split('\n') if s.strip() != '']
                    else:
                        parsedStrings = [s.encode('ascii', 'replace') for s in soup.strings if s.strip() != '']

                except:
                    # print 'Initial soup load failed'
                    errorFile = open(self.ERROR_FILENAME, 'a+')
                    errorFile.write('INITIAL SOUPING FAILED: ' + target_url + ' ' + companyCode + '\n')
                    errorFile.close()
                    try:
                        data = self.truncateDocumentData(data)
                        soup = BeautifulSoup(data, "lxml")
                        soup = BeautifulSoup(soup.prettify(), "lxml")
                        if '.txt' in target_url:
                            rawStrings = [s.encode('ascii', 'replace') for s in soup.get_text().split('\n') if s.strip() != '']
                        else:
                            rawStrings = [s.encode('ascii', 'replace') for s in soup.strings if s.strip() != '']

                        soup = self.parseData(soup)
                        if '.txt' in target_url:
                            parsedStrings = [s.encode('ascii', 'replace') for s in soup.get_text().split('\n') if s.strip() != '']
                        else:
                            parsedStrings = [s.encode('ascii', 'replace') for s in soup.strings if s.strip() != '']
                    except:
                        # print 'Soup conversion failed.  Running as text.'
                        errorFile = open(self.ERROR_FILENAME, 'a+')
                        errorFile.write('SOUP CONVERSION FAILED: ' + target_url + ' ' + companyCode +  '\n')
                        errorFile.close()
                        return None, None, None
                return soup, rawStrings, parsedStrings

            #Use raw (with tables) strings to find the market cap text
            soup, rawStrings, parsedStrings = ingestSoup(data)
            if soup is None or rawStrings is None or parsedStrings is None:
                errorFile = open(self.ERROR_FILENAME, 'a+')
                errorFile.write('SOMETHING PARSE FUCKED: ' + target_url + ' ' + companyCode +  '\n')
                errorFile.close()
                continue
            header = self.getCombinedLineArray(rawStrings, -1)
            marketCapText = self.findMarketCapText(header)

            marketCap = -1
            if marketCapText is not None:
                marketCap = self.convertTextToAmount(marketCapText)
            print 'Market Cap: ', marketCap, companyCode
            if marketCap < 100000000:
                print 'BAD MARKET CAP DETECTED: ', str(marketCap), companyCode, target_url
                errorFile = open(self.ERROR_FILENAME, 'a+')
                errorFile.write('BAD MARKET CAP: ' + str(marketCap) + ' ' + target_url + ' ' + companyCode + '\n')# + 'Market cap text was: ' + str(marketCapText))
                errorFile.close()

            #Use parsed strings (no tables) to create actual output
            outArray = self.getCombinedLineArray(parsedStrings, -1)
            outString = '\n'.join(outArray)
            outString = re.sub(r'(?<!\n)\n', '\n', outString)

            filename = open(path,"w+")
            filename.write(target_url + '\n')
            filename.write(index_url + '\n')
            filename.write(str(float(marketCap)) + '\n')
            infoArray = docNameList[i].strip(".txt").split('_')
            for info in infoArray:
                print info
                filename.write(info + '\n')
            filename.write(str(docNameList[i]) + '\n\n')
            filename.write(outString)
            filename.close()
            t2 = time.time()
            print "Downloaded " + companyCode + "'s " + filingType + "s: " + str(i) + "/" + str(len(filingURLList)) + ". Time: " + str(t2-t1) + "\n"


    #filingType must be "10-K", "10-Q", "8-K", "13F"

    def getFiling(self, companyCode, cik, priorto, count, filingType):
        try:
            self.make_directory(companyCode,cik, priorto, filingType)
        except:
            errorFile = open(self.ERROR_FILENAME, 'a+')
            errorFile.write('DIRERROR: ' + companyCode + '\n' + str(sys.exc_info()[0]))
            errorFile.close()
            print "Not able to create directory"
            return
        
        #generate the url to crawl 
        base_url = "http://www.sec.gov"
        target_url = base_url + "/cgi-bin/browse-edgar?action=getcompany&CIK="+str(companyCode)+"&type="+filingType+"&dateb="+str(priorto)+"&owner=exclude&output=xml&count="+str(count)    
        print "Now trying to download "+ filingType + " forms for " + str(companyCode) + ' from target url:\n' + target_url
        r = self.repeatRequest(target_url)
        data = r.text
        soup = BeautifulSoup(data, "lxml") # Initializing to crawl again
        linkList=[] # List of all links from the CIK page

        # print soup

        # trs = soup.findAll('type')
        # print trs
        # for tr in trs:
        #     tds = tr.findAll('td')
        #     for td in tds:
        #         s = str(td.string).lower().strip()
        #         if '10-k' in s and '10-k/a' not in s and '10-k405' not in s:
        #             URL = str(tr.find('a').string)
        #             extension = URL.split(".")[len(URL.split("."))-1]
        #             if extension == "htm":
        #                 URL+="l"
        #             linkList.append(URL)
        #             break
        # print 'final linklist'
        # print linkList
        # If the link is .htm convert it to .html
        # print "Printing all seen URLs\n\n"
        hrefs = soup.findAll('filinghref')
        types = soup.findAll('type')
        for i in xrange(len(hrefs)):
            link = hrefs[i].string
            curType = types[i].string

            #TOOD: REMOVE THIS WHEN DONE DOWNLOADING 405s
            if curType != '10-K405':
                continue
        # for link in soup.find_all('filinghref')
            URL = link.string
            # print URL
            extension = link.string.split(".")[len(link.string.split("."))-1]
            if extension == "htm":
                URL+="l"
                linkList.append(URL)
                # print URL
            if extension == "html":
                linkList.append(URL)
                # print URL
        linkListFinal = linkList
        
        numFiles = min(len(linkListFinal), count)
        print "Number of files to download: ", numFiles
        print "Starting download...."

        indexURLList = [] # List of index URLs used.
        filingURLList = [] # List of URLs scraped from index.
        docNameList = [] # List of document names

        for link in linkListFinal:
            r = self.repeatRequest(link)
            data = r.text
            newSoup = BeautifulSoup(data, "lxml") # Initializing to crawl again
            linkList=[] # List of all links from the CIK page

            # Finds the filing date for this set of documents
            grouping = newSoup.findAll('div', {'class': 'formGrouping'})[1]
            filingDate = grouping.find('div', {'class': 'info'}).string
            docName = companyCode + "_" + filingDate + "_" + filingType + ".txt"
            docNameList.append(docName)

            # Finds filingType documents from the index page using link checking
            def isFiling(filingType, URL):
                # print URL
                URL = URL.lower()
                filingType = filingType.lower()
                filingTypeFillerRegex = filingType.replace('-', '.')
                filingTypeNoHyphenRegex = filingType.replace('-', '')
                # print 'TESTING URL:', URL
                if '/archives/' in URL:
                    if re.search(filingTypeFillerRegex + '\.htm', URL) != None:
                        return True
                    if re.search(filingTypeNoHyphenRegex + '\.htm', URL) != None:
                        return True
                    if re.search(filingTypeFillerRegex + '\.txt', URL) != None:
                        return True
                    if re.search(filingTypeNoHyphenRegex + '\.txt', URL) != None:
                        return True
                return False

                # if '/archives/' in URL:
                #     if re.search(filingTypeFillerRegex + '\.htm', URL) != None
                #         return True
                #     if (filingType.replace('-', '') + '.htm') in URL:
                #         return True
                #     results = re.search(r'\.', URL)
                #     if (filingType + '.txt') in URL:
                #         return True
                #     if (filingType.replace('-', '') + '.txt') in URL:
                #         return True
                # return False

            foundFiling = False
            #Use the table search method to locate table rows with '10k'
            trs = newSoup.findAll('tr')
            for tr in trs:
                if not foundFiling:
                    tds = tr.findAll('td')
                    # print tds
                    for td in tds:
                        # print td
                        if td.string:
                            s = str((td.string).encode('ascii', 'replace')).lower().strip()
                            #Ignore 10k-ish filingss
                            # print s
                            if '10-k' in s and '10-k/a' not in s and '10-k405/a' not in s:
                                URL = str(tr.find('a')['href'])
                                if URL is not None:
                                    if '.htm' in URL.lower() or '.txt' in URL.lower():
                                        filingURLList.append(base_url + URL)
                                        foundFiling = True
                                        print 'FOUND ROW FILING!!!!: ', base_url + URL
                                break
            
            #If we can't identify, use naive link checking method
            if not foundFiling:
                for linkedDoc in newSoup.find_all('a'):
                    URL = linkedDoc['href']
                    # print URL
                    if isFiling(filingType, URL):
                        filingURLList.append(base_url + URL)
                        print 'FOUND NAIVE FILING: ', URL
                        foundFiling = True
                        break

            #If no filings found, THEN go look for complete submission .txt file
            if not foundFiling:
                linkID = link.split('/')[-1].strip('-index.html')
                for linkedDoc in newSoup.find_all('a'):
                    URL = linkedDoc['href']
                    if linkID in URL.lower() and '.txt' in URL.lower():
                        filingURLList.append(base_url + URL)
                        foundFiling = True
                        print 'FOUND COMPLETE FILING: ', URL
                        break
            

            if foundFiling:
                indexURLList.append(link)

        # try:
        self.save_in_directory(companyCode, cik, priorto, filingURLList, docNameList, indexURLList, filingType)
        # except:
            # print "Not able to save " + filingType + " files for " + companyCode