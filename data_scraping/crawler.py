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
		decomposeList = ["table"]
		for toDecompose in soup.find_all(decomposeList):
			toDecompose.decompose()
		return soup
	

	def save_in_directory(self, companyCode, cik, priorto, filingURLList, docNameList, filingType):
		# Save every text document into its respective folder
		for i in range(len(filingURLList)):
			t1 = time.time()
			target_url = filingURLList[i]

			r = requests.get(target_url)
			data = r.text
			soup = BeautifulSoup(data, "lxml")

			parsedData = self.parseData(soup)
			parsedData = parsedData.get_text()
			parsedData= parsedData.encode('ascii', 'ignore')
			parsedData = re.sub(r'\n+', ' ', parsedData)

			path = "SEC-Edgar-data/"+str(companyCode)+"/"+str(cik)+"/"+str(filingType)+"/"+str(docNameList[i])
			filename = open(path,"w+")
			filename.write(parsedData)
			t2 = time.time()
			print "Downloaded " + companyCode + "'s " + filingType + "s: " + str(i) + "/" + str(len(filingURLList)) + ". Time: " + str(t2-t1)


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
			print link
			if link.string.split(".")[len(link.string.split("."))-1] == "htm":
				URL+="l"
	    		linkList.append(URL)
		linkListFinal = linkList
		
		numFiles = min(len(linkListFinal), count)
		print "Number of files to download: ", numFiles
		print "Starting download...."

		filingURLList = [] # List of URLs scraped from index.
		docNameList = [] # List of document names
		print linkListFinal


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
			for linkedDoc in newSoup.find_all('a'):
				URL = linkedDoc['href']
				if '/Archives/' in URL and (filingType.lower() + '.htm') in URL:
					filingURLList.append(base_url + URL)

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