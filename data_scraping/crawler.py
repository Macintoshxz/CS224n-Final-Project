# This script will download all the 10-K, 10-Q and 8-K 
# provided that of company symbol and its cik code.

from bs4 import BeautifulSoup
import re
import requests
import os
import time

class SecCrawler():

    def __init__(self):
        self.hello = "Welcome to Sec Cralwer!"

    def make_directory(self, companyCode, cik, priorto, filingType):
        # Making the directory to save comapny filings
        if not os.path.exists("SEC-Edgar-data/"):
            os.makedirs("SEC-Edgar-data/")
        if not os.path.exists("SEC-Edgar-data/"+str(companyCode)):
            os.makedirs("SEC-Edgar-data/"+str(companyCode))
        if not os.path.exists("SEC-Edgar-data/"+str(companyCode)+"/"+str(cik)):
            os.makedirs("SEC-Edgar-data/"+str(companyCode)+"/"+str(cik))
        if not os.path.exists("SEC-Edgar-data/"+str(companyCode)+"/"+str(cik)+"/"+str(filingType)):
            os.makedirs("SEC-Edgar-data/"+str(companyCode)+"/"+str(cik)+"/"+str(filingType))

    def parseData(self, soup):
        decomposeList = ["table", "a"]
        for toDecompose in soup.find_all(decomposeList):
            toDecompose.decompose()
        return soup

    #Takes in an array of strings from BS4 and identifies the sentence with the market cap
    def findMarketCapSentence(self, strings):
        for line in strings:
            if "aggregate" in line and "market" in line and "value" in line:
                idx = line.find('aggregate')
                return line[idx:]
        return None

    def isolateDollarSign(self, sentence):
        dollarSignIdx = sentence.find("$")
        if dollarSignIdx is not -1:
            sentence = sentence[dollarSignIdx:]
        return sentence

    def convertTextToAmount(self, text):
        amount = re.findall('[\d\,*\.*]+', text)[0].replace(',','')
        print amount
        multiplier = 1
        if 'billion' in text:
            multiplier = 1000000000
        if 'million' in text:
            multiplier = 1000000
        return float(amount)*multiplier
            
    def marketCapFromSentence(self, sentence):
        potentialMarketCaps = re.findall(r'was\s*\$?[\d+\,*\.*]+ *[mb]illion(?i)', sentence)
        if len(potentialMarketCaps) is 0:
            potentialMarketCaps = re.findall(r'was\s*\$[\d+\,*\.*]+', sentence)
        if len(potentialMarketCaps) is 0:
            potentialMarketCaps = re.findall(r'was\s*\$?[\d+\,*\.*]+', sentence)
        if len(potentialMarketCaps) is 0:
            potentialMarketCaps = re.findall(r'\$?[\d+\,*\.*]+ *[mb]illion(?i)', sentence)
        if len(potentialMarketCaps) is 0:
            potentialMarketCaps = re.findall(r'\$[\d+\,*\.*]+', sentence)
        

        marketCap = -1
        if len(potentialMarketCaps) is not 0:
            marketCapText = potentialMarketCaps[0]
            marketCap = self.convertTextToAmount(marketCapText)
        return marketCap

    def getCombinedLineArray(self, lines):
        curLine = ""
        outArray= []
        for line in lines:
            found = re.findall('\.\s*$', line)
            curLine += line.strip() + " "
            if len(found) != 0:
                curLine = curLine.replace("\n", " ").strip()
                outArray.append(curLine)
                curLine = ""
        return outArray

    def save_in_directory(self, companyCode, cik, priorto, filingURLList, docNameList, filingType):
        # Save every text document into its respective folder
        for i in range(len(filingURLList)):
            t1 = time.time()
            target_url = filingURLList[i]
            print target_url

            r = requests.get(target_url)
            data = r.text
            soup = BeautifulSoup(data, "lxml")
            soup = BeautifulSoup(soup.prettify(), "lxml")
            # parsedData = self.parseData(soup)
            # parsedData = parsedData.get_text()
            # parsedData= parsedData.encode('ascii', 'ignore')
            # parsedData = re.sub(r'(?<!\n)\n', '\n', parsedData)
            # parsedData = re.sub(r'[0-9]+\n', '\n', parsedData)
            # parsedData = re.sub('(?<![\r\n])(\r?\n|\n?\r)(?![\r\n])', ' ', parsedData)
            # parsedData = re.sub(r'\s*\n\n+\s*', '\n\n', parsedData)
            # parsedData = re.sub(r'\s*\n\n+\s*', '\n\n', parsedData)
            
            path = "SEC-Edgar-data/"+str(companyCode)+"/"+str(cik)+"/"+str(filingType)+"/"+str(docNameList[i])

            filename = open(path,"w+")
            strings = [s.encode('ascii', 'ignore') for s in soup.strings if s.strip() != '']

            outArray = self.getCombinedLineArray(strings)

            header = outArray[0:50]
            # for line in header:
            #     print line + '\n\n'
            marketCapSentence = self.findMarketCapSentence(header)
            print marketCapSentence

            marketCap = -1
            if marketCapSentence is not None:
                marketCap = self.marketCapFromSentence(marketCapSentence)
            print marketCap

            outString = '\n'.join(outArray)
            outString = re.sub(r'(?<!\n)\n', '\n', outString)


            filename.write(target_url + '\n')
            filename.write(str(float(marketCap)) + '\n')
            infoArray = docNameList[i].strip(".txt").split('_')
            for info in infoArray:
                print info
                filename.write(info + '\n')
            filename.write(str(docNameList[i]) + '\n\n')
            filename.write(outString)

            t2 = time.time()
            print "Downloaded " + companyCode + "'s " + filingType + "s: " + str(i) + "/" + str(len(filingURLList)) + ". Time: " + str(t2-t1) + "\n"


    #filingType must be "10-K", "10-Q", "8-K", "13F"

    def getFiling(self, companyCode, cik, priorto, count, filingType):
        try:
            self.make_directory(companyCode,cik, priorto, filingType)
        except:
            print "Not able to create directory"
        
        #generate the url to crawl 
        base_url = "http://www.sec.gov"
        target_url = base_url + "/cgi-bin/browse-edgar?action=getcompany&CIK="+str(cik)+"&type="+filingType+"&dateb="+str(priorto)+"&owner=exclude&output=xml&count="+str(count)    
        print ("Now trying to download "+ filingType + " forms for " + str(companyCode))
        r = requests.get(target_url)
        data = r.text
        soup = BeautifulSoup(data, "lxml") # Initializing to crawl again
        linkList=[] # List of all links from the CIK page

        # If the link is .htm convert it to .html
        for link in soup.find_all('filinghref'):
            URL = link.string
            # print link
            if link.string.split(".")[len(link.string.split("."))-1] == "htm":
                URL+="l"
                linkList.append(URL)
                print URL
        linkListFinal = linkList
        
        numFiles = min(len(linkListFinal), count)
        print "Number of files to download: ", numFiles
        print "Starting download...."

        filingURLList = [] # List of URLs scraped from index.
        docNameList = [] # List of document names
        
        # print linkListFinal


        for link in linkListFinal:
            r = requests.get(link)
            data = r.text
            newSoup = BeautifulSoup(data, "lxml") # Initializing to crawl again
            linkList=[] # List of all links from the CIK page

            # Finds the filing date for this set of documents
            grouping = newSoup.find('div', {'class': 'formGrouping'})
            filingDate = grouping.find('div', {'class': 'info'}).string
            docName = companyCode + "_" + filingDate + "_" + filingType + ".txt"
            docNameList.append(docName)

            # Finds filingType documents from the index page
            def isFiling(filingType, URL):
                # print URL
                if '/Archives/' in URL:
                    if (filingType.lower() + '.htm') in URL:
                        return True
                    if (filingType.replace('-', '').lower() + '.htm') in URL:
                        return True
                return False


            for linkedDoc in newSoup.find_all('a'):
                URL = linkedDoc['href']
                # print URL
                if isFiling(filingType, URL):
                    filingURLList.append(base_url + URL)

        print 'Printing filingURLList'
        for url in filingURLList:
            print url

            # soup = BeautifulSoup(data, "lxml") # Initializing to crawl again
            # requiredURL = str(linkListFinal[i])[0:len(linkListFinal[i])-11]
            # print requiredURL
            # txtdoc = requiredURL+".txt"
            # docname = txtdoc.split("/")[len(txtdoc.split("/"))-1]
            # docList.append(txtdoc)
            # docNameList.append(docname)

        # try:
        self.save_in_directory(companyCode, cik, priorto, filingURLList, docNameList, filingType)
        # except:
            # print "Not able to save " + filingType + " files for " + companyCode