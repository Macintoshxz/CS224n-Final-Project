# This script will download all the 10-K, 10-Q and 8-K 
# provided that of company symbol and its cik code.

from bs4 import BeautifulSoup
import re
import requests
import os
import time
import string
from collections import OrderedDict

class SecCrawler():

    REQUEST_SLEEP_TIME = 300
    HTTP_OKAY = 200
    ERROR_FILENAME = 'error_log.txt'

    def __init__(self):
        self.hello = "Welcome to Sec Cralwer!"

    def repeatRequest(self, target_url):
        r = requests.get(target_url)
        acceptable_errors = [404]
        REQUEST_THRESHOLD = 5
        requestCounter = 0
        while r.status_code != self.HTTP_OKAY:
            if requestCounter >= REQUEST_THRESHOLD:
                if r.status_code in acceptable_errors:
                    print r.status_code, ": ", target_url, ""
                    return None
                print r.status_code, ": ", target_url, ".  Sleeping for ", self.REQUEST_SLEEP_TIME, "..."
                time.sleep(self.REQUEST_SLEEP_TIME)
                requestCounter =0
            try:
                r = requests.get(target_url)
            except:
                pass
            requestCounter += 1
        print r.status_code, ": ", target_url
        return r

    def make_directory(self, companyCode, filingType):
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
            prevLines = ''.join(strings[max(0, i-MAX_LINES_LOOKBEHIND)]).split('.')
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
            if isinstance(textElem, list) or isinstance(textElem, tuple):
                textElem = textElem[0]

            amount = re.findall(r'(\d{1,3}(\s*,\s*\d{3})*(\s*\.\s*\d+)?)', textElem)
            if len(amount) == 0:
                continue
            amount = amount[0]
            replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
            amount = amount[0].translate(replace_punctuation)
            amount = re.sub(r'\s*', '', amount)
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

        #New spacing between dots
        potentialMarketCaps = re.findall(r'was\s*\$\s*((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?)\s*[mb]ill?i?o?n?(?i))', sentence)
        potentialMarketCaps.append(re.findall(r'approximately\s*\$\s*((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?) *[mb]ill?i?o?n?(?i))', sentence))
        potentialMarketCaps.append(re.findall(r':\s*\$\s*((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?)\s*[mb]ill?i?o?n?(?i))', sentence))
        potentialMarketCaps.append(re.findall(r'was\s*\$\s*((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?))', sentence))
        potentialMarketCaps.append(re.findall(r'approximately\s*\$\s*((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?))', sentence))
        potentialMarketCaps.append(re.findall(r':\s*\$\s*((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?))', sentence))
        potentialMarketCaps.append(re.findall(r'approximately\s*\$ \s*((\d{1,3}(\s*,\s*\d{3})*(\s*\.\s*\d+)?) *[mb]ill?i?o?n?(?i))', sentence))
        potentialMarketCaps.append(re.findall(r'\$?\s*((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?))', sentence))
        potentialMarketCaps.append(re.findall(r'\$?\s*((\d{1,3}(\s*,\d{3})*(\s*\.\s*\d+)?)\s*[mb]ill?i?o?n?(?i))', sentence))

        #If we still have nothing, check more unlikely cases
        if len(potentialMarketCaps) is 0:
            potentialMarketCaps = re.findall(r'approximately\s*\$?\s*((\d{1,3}(\s*,\s*\d{3})*(\s*\.\s*\d+)?))', sentence)
        if len(potentialMarketCaps) is 0:
            potentialMarketCaps = re.findall(r'was\s*\$?\s*((\d{1,3}(\s*,\s*\d{3})*(\s*\.\s*\d+)?))', sentence)
        if len(potentialMarketCaps) is 0:
            potentialMarketCaps = re.findall(r'\$\s*((\d{1,3}(\s*,\s*\d{3})*(\s*\.\s*\d+)?))', sentence)

        potentialMarketCaps = [item for sublist in potentialMarketCaps for item in sublist]
        return potentialMarketCaps

    def getCombinedLineArray(self, lines, numLines=-1):
        curLine = ""
        outArray= []
        lineCounter = 0
        for line in lines:
            found = re.findall(r'\.\s*$', line)
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

    # def truncateDocumentData(self, data):
    #     strings = data.split('\n')
    #     endIdx = len(strings)
    #     for i in xrange(len(strings)):
    #         s = strings[i]
    #         if '</DOCUMENT>' in s:
    #             endIdx = i
    #             break
    #     strings = strings[:endIdx]
    #     newData = '\n'.join(strings)
    #     return newData

    def truncateDocumentData(self, data):
        m = re.search('</DOCUMENT>', data)
        end = m.end()
        return data[:end]

    ITEM_STRINGS = [r'item.?\s*1', r'item.?\s*1a', r'item.?\s*1b',r'item.?\s*2', r'item.?\s*3', r'item.?\s*5', \
                    r'item.?\s*6', r'item.?\s*7', r'item.?\s*7a', r'item.?\s*8', r'item.?\s*9', r'item.?\s*9a', \
                    r'item.?\s*9B', r'item.?\s*10', r'item.?\s*11', r'item.?\s*12', r'item.?\s*13', r'item.?\s*14', r'item\s*15']
    SECTION_NAMES = ['1', '1a', '1b', '2', '3', '5', '6', '7', '7a', '8', '9', '9a', '9b', '10', \
        '11', '12', '13', '14', '15']
    descDict = {
        '1': r'business',
        '1a': r'risk\s*factors',
        '1b': r'unresolved\s*staff\s*comments',
        '2': r'properties',
        '3': r'legal\s*proceedings',
        '5': r'market\s*for\s*registrant.?\s*s\s*common\s*equity.?\s*related\s*stockholder' + \
            r'matters\s*and\s*issuer\s*purchases\s*of\s*equity\s*securities',
        '6': r'selected\s*financial\s*data',
        '7': r'management.?\s*s\s*discussion\s*and\s*analysis\s*of\s*' + \
            r'financial\s*condition\s*and\s*results\s*of\s*operation',
        '7a': r'quantitative\s*and\s*qualitative\s*disclosures\s*about\s*market\s*risk',
        '8': r'financial\s*statements\s*and\s*supplementary\s*data',
        '9': r'changes\s*in\s*and\s*disageements\s*with\s*accountants\s*on\s*accounting\s*and' + \
            r'financial\s*disclosure',
        '9a': r'controls\s*and\s*procedures',
        '9b': r'other\s*information',
        '10': r'directors.?\s*executive\s*officers\s*and\s*corporate\s*governance',
        '11': r'executive\s*compensation',
        '12': r'security\s*ownership\s*of\s*certain\s*beneficial\s*owners\s*and\s*management' + \
            r'and\s*related\s*stockholder\s*matters',
        '13': r'certain\s*relationships\s*and\s*related\s*transactions.?\s*and\s*director\s*independence',
        '14': r'principal\s*accountant\s*fees\s*and\s*services',
        '15': r'exhibits.?\s*financial\s*statement\s*schedules'
    }

    ITEM_THRESHOLD = 10
    SECTION_DESCS = [descDict[name] for name in SECTION_NAMES]

    def getTableSoup(self, soup, ITEM_STRINGS, ITEM_THRESHOLD):
        tableList = soup.findAll('table')
        for t in tableList:
            tsoup = BeautifulSoup(str(t), 'lxml')
            sstrings = tsoup.stripped_strings
            joined_sstrings = ' '.join(sstrings).encode('ascii', 'replace').replace('?', ' ').lower()
            truthArray = [1*bool(re.search(item, joined_sstrings)) for item in ITEM_STRINGS]
            if sum(truthArray) >= ITEM_THRESHOLD:
                toc = t
                print truthArray
                return tsoup
        return None

    def getLinkMapping(self, tsoup, ITEM_STRINGS, ITEM_NAMES):
        trs = tsoup.findAll('tr')
        linkArray = [None]*len(ITEM_NAMES)
        hasElem = False
        for tr in trs:
            tds = tr.findAll('td')
            tdsString = ''.join([unicode(td) for td in tds])
            # tdsString = ''.join([unicode(td) if td.string != None else '' for td in tds])

            tdsString = tdsString.encode('ascii', 'replace').lower()
            # print tdsString
            thisItem = -1
            curI = -1
            for i in reversed(range(len(ITEM_STRINGS))):
                item = ITEM_STRINGS[i]
                if re.search(item, tdsString):
                    thisItem = ITEM_NAMES[i]
                    curI = i
                    break
            if thisItem != -1:
                for td in tds:
                    found = td.find('a', href=True)
                    if found:
                        # linkMapping[thisItem] = found['href']
                        linkArray[curI] = found['href'].encode('ascii', 'replace').replace('?', ' ')
                        hasElem = True
                        break
        print "linkarray:"
        print linkArray
        # print linkMapping
        # return linkMapping
        return linkArray if hasElem else None

    def getLinkMappingFromLinkTexts(self, soup, ITEM_STRINGS):
        print 'Trying to get mapping from link texts'
        links = soup.findAll('a', href=True)
        linkArray = [None]*len(ITEM_STRINGS)

        for link in links:
            try:
                linkString = link.encode('ascii', 'replace').replace('?', ' ')
            except:
                try:
                    linkString = str(link).encode('ascii', 'replace').replace('?', ' ')
                except:
                    continue
            for i in reversed(range(len(ITEM_STRINGS))):
                item = ITEM_STRINGS[i]
                if re.search(item, linkString):
                    linkArray[i] = link['href'].encode('ascii', 'replace').replace('?', ' ')
        return linkArray

    def removeMissingLetteredSections(self, sectionList, sectionIdxList):
        n = len(sectionList)
        newSectionList = []
        newSectionIdxList = []

        letteredIndices = [1, 2, 8, 11, 12, 17]
        for i in xrange(n):
            if sectionList[i] == None and i in letteredIndices:
                continue
            newSectionList.append(sectionList[i])
            newSectionIdxList.append(sectionIdxList[i])
        return newSectionList, newSectionIdxList

    def getLinkRawIndices(self, linkMapping, data):
        def isValidLink(link):
            if '.htm' in link:
                return False
            if '(' in link or ')' in link:
                return False
            return True
        def findStart(link, text):
            res = None
            try:
                link = link.encode('ascii', 'replace').replace('?', ' ').lower()
                # print text.lower()
                if not isValidLink(link):
                    return None
                regexString = r'name=.?' + link
                res = re.search(regexString, text.encode('ascii', 'replace').replace('?', ' ').lower())
            except UnicodeEncodeError:
                print 'ERRORED?'
                pass
            return res.start() if res else None
        sectionList = [None]*len(linkMapping)
        sectionIdxList = [None]*len(linkMapping)

        for i in range(len(linkMapping)):
            key = self.SECTION_NAMES[i]
            val = linkMapping[i]
            if val != None:
                idx = findStart(val.strip('#'), data)
                if idx == None:
                    continue
                idx += data[idx:].find('</A>') + 4 #4 is the length of the closing tag
                sectionIdxList[i] = idx
                sectionList[i] = key
        return sectionList, sectionIdxList

    def writeFile(self, parsedStrings, docName, target_url, index_url, marketCap, path):
        def isActualSection(text):
            if text is None:
                return False
            MIN_CHARS = 1000
            if len(text) < MIN_CHARS:
                return False
            return True
        outArray = self.getCombinedLineArray(parsedStrings, -1)
        outString = '\n'.join(outArray)
        outString = re.sub(r'(?<!\n)\n', '\n', outString)

        if not isActualSection(outString):
            return False

        filename = open(path,"w+")
        filename.write(target_url + '\n')
        filename.write(index_url + '\n')
        filename.write(str(float(marketCap)) + '\n')
        infoArray = docName.strip(".txt").split('_')
        for info in infoArray:
            print info
            filename.write(info + '\n')
        filename.write(str(docName) + '\n\n')
        filename.write(outString)
        filename.close()
        return True

    def save_in_directory(self, companyCode, filingURLList, docNameList, indexURLList, filingType):
        #Attempt normal parsing.  If this fails, try truncating and parsing again
        #If this fails AGAIN, just ignore it completely.

        def getSource(target_url, savedTargetPath):
            data = None
            oldSavedTargetPath = savedTargetPath.replace('_filing', '')
            # If its saved, load saved file instead of requesting
            if os.path.isfile(savedTargetPath):
                f = open(savedTargetPath, 'r')
                data = f.read()
                f.close()
                
                print 'READ FROM CACHED SOURCE FILE\n'
            elif os.path.isfile(oldSavedTargetPath) and '.txt' not in oldSavedTargetPath:
                f = open(oldSavedTargetPath, 'r')
                data = f.read()
                f.close()

                os.remove(oldSavedTargetPath)
                data = data.encode('ascii', 'replace')

                g = open(savedTargetPath, 'w+')
                g.write(data)
                g.close()
                print 'REPLACED SOURCE FILE!\n'
                print savedTargetPath
            else: # Make the request and say fuck the SEC.
                r = self.repeatRequest(target_url)
                if r is None:
                    errorFile = open(self.ERROR_FILENAME, 'a+')
                    errorFile.write('404 FROM: ' + target_url + '\n')
                    errorFile.close()
                    return None
                data = r.text
                dataLength = len(r.content)

                data = data.encode('ascii', 'replace')
                # Don't cache if too large (> 5 MB)
                if dataLength < 5000000:
                    g = open(savedTargetPath, 'w+')
                    g.write(data)
                    g.close()
                    print 'CACHED SOURCE FILE!\n'
                    print savedTargetPath
                else:
                    print 'DID NOT CACHE, FILE SIZE WAS ', str(dataLength), savedTargetPath
            
            data = data.encode('ascii', 'replace')    
            return data


        def ingestSoup(data, shouldParse=False):
            soup = None
            rawSoup = None
            rawStrings = None
            parsedStrings = None

            try:
                data = self.truncateDocumentData(data)
                soup = BeautifulSoup(data, "lxml")
                rawSoup = soup
                soup = BeautifulSoup(soup.prettify(), "lxml")
                if '.txt' in target_url:
                    rawStrings = [s.encode('ascii', 'replace') for s in soup.get_text().split('\n') if s.strip() != '']
                else:
                    rawStrings = [s.encode('ascii', 'replace') for s in soup.strings if s.strip() != '']

                parsedSoup = self.parseData(soup)
                if '.txt' in target_url:
                    parsedStrings = [s.encode('ascii', 'replace') for s in parsedSoup.get_text().split('\n') if s.strip() != '']
                else:
                    parsedStrings = [s.encode('ascii', 'replace') for s in parsedSoup.strings if s.strip() != '']
                    # print 'parsedHere'
                    # print parsedSoup

            except:
                # print 'Initial soup load failed'
                errorFile = open(self.ERROR_FILENAME, 'a+')
                errorFile.write('INITIAL SOUPING FAILED: ' + target_url + ' ' + companyCode + '\n')
                errorFile.close()
                try:
                    soup = BeautifulSoup(data, "lxml")
                    soup = BeautifulSoup(soup.prettify(), "lxml")
                    if '.txt' in target_url:
                        rawStrings = [s.encode('ascii', 'replace') for s in soup.get_text().split('\n') if s.strip() != '']
                    else:
                        rawStrings = [s.encode('ascii', 'replace') for s in soup.strings if s.strip() != '']

                    parsedSoup = self.parseData(soup)
                    if '.txt' in target_url:
                        parsedStrings = [s.encode('ascii', 'replace') for s in parsedSoup.get_text().split('\n') if s.strip() != '']
                    else:
                        parsedStrings = [s.encode('ascii', 'replace') for s in parsedSoup.strings if s.strip() != '']
                except:
                    # print 'Soup conversion failed.  Running as text.'
                    errorFile = open(self.ERROR_FILENAME, 'a+')
                    errorFile.write('SOUP CONVERSION FAILED: ' + target_url + ' ' + companyCode +  '\n')
                    errorFile.close()
                    return None, None, None, None
            return parsedSoup, rawStrings, parsedStrings, rawSoup
        # Save every text document into its respective folder
        for i in range(len(filingURLList)):
            #splits the section based on file existence
            t1 = time.time()
            target_url = filingURLList[i]
            #Removes interactive XBRL
            target_url = target_url.replace('ix?doc=/', '')
            target_extension = target_url.split('.')[-1]

            curDocName = str(docNameList[i])
            basePath = "SEC-Edgar-data/"+str(companyCode)+"/"+str(filingType)+"/"
            curDocBase = curDocName.split('.')[0]
            path = basePath + curDocName
            savedTargetPath = basePath + curDocBase + '_filing.' + target_extension

            # Don't overwrite existing, non-text root files - TEMPORARILY DEPRECATED - MAY USE LATER
            fileExists = os.path.isfile(path)
            fileExists = False
            # if os.path.isfile(path):
            #     print "ALREADY EXISTS: ", path, ', moving on...'
            #     continue

            index_url = indexURLList[i]
            print "Saving", target_url
            print "From index:", index_url

            data = getSource(target_url, savedTargetPath)
            if data == None:
                continue

            #Use raw (with tables) strings to find the market cap text
            soup, rawStrings, parsedStrings, rawSoup = ingestSoup(data)
            if soup is None or rawStrings is None or parsedStrings is None or rawSoup is None:
                errorFile = open(self.ERROR_FILENAME, 'a+')
                errorFile.write('SOMETHING PARSE FUCKED: ' + target_url + ' ' + companyCode +  '\n')
                errorFile.close()
                continue

            #REMOVING ALL MARKET CAP PARSING
            # header = self.getCombinedLineArray(rawStrings, -1)
            # marketCapText = self.findMarketCapText(header)

            # marketCap = -1
            # if marketCapText is not None:
            #     marketCap = self.convertTextToAmount(marketCapText)
            # print 'Market Cap: ', marketCap, companyCode
            # if marketCap < 100000000:
            #     print 'BAD MARKET CAP DETECTED: ', str(marketCap), companyCode, target_url
            #     errorFile = open(self.ERROR_FILENAME, 'a+')
            #     errorFile.write('BAD MARKET CAP: ' + str(marketCap) + ' ' + target_url + ' ' + companyCode + '\n')# + 'Market cap text was: ' + str(marketCapText))
            #     errorFile.close()

            marketCap = -1

            if not fileExists:
                #Use parsed strings (no tables) to create actual output
                self.writeFile(parsedStrings, curDocName, target_url, index_url, marketCap, path)
                t2 = time.time()
                print "Downloaded " + companyCode + "'s " + filingType + "s: " + str(i+1) + "/" + str(len(filingURLList)) + ". Time: " + str(t2-t1) + "\n"
            
            ##Now we write the sections.
            print "Now writing sections for ", companyCode
            #Only writing sections 
            if '.txt' not in target_url:
                sectionStart = time.time()
                sectionSoup = rawSoup
                # sectionSoup = BeautifulSoup(data, 'lxml')
                tsoup = None
                searchList = None
                linkMapping = None
                for possibleSearchList in [self.ITEM_STRINGS, self.SECTION_DESCS, self.SECTION_NAMES]:
                    searchList = possibleSearchList
                    tsoup = self.getTableSoup(sectionSoup, searchList, self.ITEM_THRESHOLD)
                    if tsoup != None:
                        print 'Used searchList:', searchList
                        break
                if tsoup != None:
                    linkMapping = self.getLinkMapping(tsoup, searchList, self.SECTION_NAMES)

                #If we fucked up the table somehow, look through the links
                if linkMapping == None:
                    for possibleSearchList in [self.ITEM_STRINGS, self.SECTION_DESCS, self.SECTION_NAMES]:
                        searchList = possibleSearchList
                        linkMapping = self.getLinkMappingFromLinkTexts(sectionSoup, searchList)
                        if linkMapping != None:
                            print 'Used searchList:', searchList
                            break

                #Still couldn't find anything
                if linkMapping == None:
                    continue

                sectionList, sectionIdxList = self.getLinkRawIndices(linkMapping, data)
                sectionList, sectionIdxList = self.removeMissingLetteredSections(sectionList, sectionIdxList)
                print sectionList
                print sectionIdxList
                n = len(sectionList)

                for i in range(n):
                    curSectionName = sectionList[i]
                    curIdx = sectionIdxList[i]
                    
                    # If already written, skip
                    sectionPath = basePath + curDocName.split('.')[0] + '_html_section_' + str(curSectionName) + '.txt'
                    if os.path.isfile(sectionPath):
                        print 'Section ', curSectionName, 'for ', companyCode, 'already extracted!'
                        continue

                    if curIdx == None:
                        continue
                    if i < n - 1:
                        nextIdx = sectionIdxList[i + 1]
                        if nextIdx == None:
                            continue
                        sectionData = '<html><body>' + data[curIdx:nextIdx] + '</body></html/>'
                    else:
                        sectionData = '<html><body>' + data[curIdx:] + '</body></html/>'
                    # print sectionData
                    sectionParsedSoup, sectionRawStrings, sectionParsedStrings, sectionRawSoup = ingestSoup(sectionData)
                    status = self.writeFile(sectionParsedStrings, curDocName, target_url, index_url, marketCap, sectionPath)
                    if not status:
                        print 'Error with section ', curSectionName, 'for ', companyCode, target_url
                    else:
                        print 'Writing section ', curSectionName, 'for ', companyCode, target_url

                print "Done writing sections for ", companyCode, "Time: ", str(time.time() - sectionStart)
            else:
                print 'Target was a .txt, so no sections could be extracted'


    #filingType must be "10-K", "10-Q", "8-K", "13F"

    def getFiling(self, companyCode, priorto, count, filingType):
        try:
            self.make_directory(companyCode, filingType)
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
        if r == None:
            print 'Did not download forms for ', str(companyCode), "Bad request of some kind :("
            return
        data = r.text
        soup = BeautifulSoup(data, "lxml") # Initializing to crawl again
        linkList=[] # List of all links from the CIK page

        # print "Printing all seen URLs\n\n"
        hrefs = soup.findAll('filinghref')
        types = soup.findAll('type')
        for i in xrange(len(hrefs)):
            link = hrefs[i].string
            curType = types[i].string

            if curType != '10-K405' and curType != '10-K' and curType != '10-KT':
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
            if r == None:
                print 'Did not download forms for ', str(companyCode), "Bad request of some kind :("
                return
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
                            try:
                                s = str((td.string).encode('ascii', 'replace')).lower().strip()
                            except UnicodeEncodeError:
                                continue
                            #Ignore 10k-ish filingss
                            # print s
                            if '10-k' in s and '10-k/a' not in s and '10-k405/a' not in s:
                                link = tr.find('a', href=True)
                                if link:
                                    try:
                                        URL = str(tr.find('a')['href'])
                                    except UnicodeEncodeError:
                                        pass
                                else:
                                    URL = None
                                if URL is not None:
                                    if '.htm' in URL.lower() or '.txt' in URL.lower():
                                        filingURLList.append(base_url + URL)
                                        foundFiling = True
                                        print 'FOUND ROW FILING!!!!: ', filingDate, base_url + URL
                                break
            
            #If we can't identify, use naive link checking method
            if not foundFiling:
                for linkedDoc in newSoup.find_all('a', href=True):
                    URL = linkedDoc['href']
                    # print URL
                    if isFiling(filingType, URL):
                        filingURLList.append(base_url + URL)
                        print 'FOUND NAIVE FILING: ', filingDate, base_url + URL
                        foundFiling = True
                        break

            #If no filings found, THEN go look for complete submission .txt file
            if not foundFiling:
                if link:

                    ending = str(link).split('/')
                    linkID = ending[-1].strip('-index.html')
                    for linkedDoc in newSoup.find_all('a', href=True):
                        URL = linkedDoc['href']
                        if linkID in URL.lower() and '.txt' in URL.lower():
                            filingURLList.append(base_url + URL)
                            foundFiling = True
                            print 'FOUND COMPLETE FILING: ', filingDate, base_url + URL
                            break
            

            if foundFiling:
                indexURLList.append(str(link))

        # try:
        self.save_in_directory(companyCode, filingURLList, docNameList, indexURLList, filingType)
        # except:
            # print "Not able to save " + filingType + " files for " + companyCode