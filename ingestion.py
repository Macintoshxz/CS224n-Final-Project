import os
import pickle
import argparse
from gensim.models import Doc2Vec
from collections import OrderedDict
import numpy as np
import math

def Doc2VecMapping(filename):
    '''
    args: filename is the name of the d2v model as outputted by Doc2Vec. Must
    be the in the same directory as this file. 
    Output: sequence dictionary between ticker and sequences
            list of sequences in alphabetical order of tickers
    '''
    model = Doc2Vec.load(filename)
    d2vdict = {}
    for i in range(len(model.docvecs)):
        doctag = model.docvecs.index_to_doctag(i)
        doctag = doctag.split("_")
        if '.txt' in doctag[-1]:
            ticker = doctag[0]
            year = int(doctag[1].split("-")[0])
            d2vdict[(ticker, year)] = i
            # print doctag

    #sorts by ticker
    orderedd2v = OrderedDict(sorted(d2vdict.items(), key=lambda t: t[0])) 

    #create dict of sequences of 10ks for company. 
    sequenceDict = OrderedDict()
    prevTicker = ""
    for key in orderedd2v:
        currentTicker = key[0]
        if currentTicker == prevTicker:
            sequenceDict[currentTicker].append(orderedd2v[key])
        else:
            sequenceDict[currentTicker] = [orderedd2v[key]]
        prevTicker = currentTicker

    return orderedd2v, sequenceDict.values()

def getMarketCap(path, inflationDict):
    '''
    args: path is the path to the SEC filings
    Output: returns a dictionary mapping (ticker, year) : market capitalization
    '''
    marketCap = {}
    for subdir, dirs, files in os.walk(path):
        for f in files:
            docPath = os.path.join(subdir, f)
            filename, file_extension = os.path.splitext(f)
            if docPath not in marketCap and filename != ".DS_Store":
                infile = open(docPath, 'r')
                lines=infile.readlines()
                # print lines
                mc = lines[2].rstrip()
                filename = filename.split("_")
                ticker = filename[0]
                # print filename
                year = int(filename[1].split("-")[0])
                marketCap[(ticker, year)] = float(mc)*inflationDict[year]
                #print mc
    return marketCap

def createInflationDict(path):
    '''
    Loads the manual-entry inflation_table.txt into a dict to convert
    the market caps to current day currency.
    '''
    f = open(path, 'r')
    lines = f.readlines()
    f.close()
    inflationDict = {}
    for line in lines:
        year, rate =line.split('\t')
        inflationDict[int(year)] = float(rate)
    return inflationDict

def get_glove_for_data():
    '''
    Create "document vectors" by averaging glove vectors
    for words inside 10ks
    '''
def getLabel(change, bins):

    if change >= bins[0] and change < bins[1]:
        return 0
    elif change >= bins[1] and change < bins[2]:
        return 1
    elif change >= bins[2] and change < bins[3]:
        return 2
    elif change >= bins[3] and change < bins[4]:
        return 3
    else:
        return 4

def construct_differential_feedforward_data(filename, embeddingDim, maxClasses):
    ''' For constructing data for FF NN for classificiation into five classes
        based on quitiles of percentage change based on differential input of 
        two consecutive documents from a particular company.

        AAPL 2008 -> (emb_08, emb_09) (MC_change from 09-10) (UUID ordered chronologically)

        Filename refers to the check file. Third column is the percentage change. 
        First column is the ticker. Second column is the year.
    '''

    #dict of change : (ticker, year) mapping
    embeddingBase = 'embeddingDicts/embeddingDict_'
    embeddingFile = embeddingBase + str(embeddingDim) + '.pkl'
    embeddingDict = pickle.load(open(embeddingFile, "rb"))

    '''Track two indices for two input embeddings'''

    company_histories = {}
    changes = []

    with open(filename) as check:
        lines = check.readlines()
        tickers = []
        #get stock tickers in check file
        for line in lines:
            data = line.split("\t")
            if data[0].strip() not in tickers:
                tickers.append(data[0].strip())
            if data[2] != "None":
                changes.append(float(data[2]))
            else:
                changes.append(float(0))

        for ticker in tickers:
            history = []
            for line in lines:
                data = line.split("\t")
                if ticker == data[0].strip():
                    history.append(data)
            company_histories[ticker] = history

    changes.sort()
    listlen = len(changes)
    maxLabel = maxClasses - 1
    div = int(listlen/maxClasses)
    labelsDict = {}
    bins = []
    for i in range(listlen):
        labelsDict[changes[i]] = i/div if i/div <= maxLabel else maxLabel #backloading

    indices = []
    labels = []
    embeddings = []

    index = 0
    for history in company_histories.values():
        if len(history) > 1:
            for year in range(len(history)-1):

                filename_A = history[year][5]
                embeddings.append(list(embeddingDict[filename_A]))

                indices.append([index, index+1])

                key = history[year+1][2]
                if key == "None":
                    key = 0
                key = float(key)
                labels.append(labelsDict[key])

                index += 1

                if year == len(history)-2:
                    embeddings.append(list(embeddingDict[history[year+1][5]]))
                    #indices.append([-1, -1])
                    #labels.append(-1)
                    index += 1

                #diff_ff_data.append([indices, label, embedding, history[year][0], [filename_A, filename_B]])

    return indices, labels, embeddings

def construct_single_input_feedforward_from_manifest(filename, embedding_to_use):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()

    X = []
    Y = []
    # E1 = []
    # E2 = []
    E_master = []
    splits = [line.split(',') for line in lines]
    idx = 0
    n = len(splits)
    count = 0
    for split in splits:
        if count % 1000 == 0:
            print str(count), '/', str(n)
        curY = int(split[1])
        curE1 = np.array([float(e) for e in split[2:52]])
        curE2 = np.array([float(e) for e in split[52:]])

        diff = curE1 - curE2
        diff = list(diff)
        Y.append(curY)
        # if embedding_to_use == 0:
        #     # E_master.append(curE1)
        # if embedding_to_use == 1:
        #     E_master.append(curE2)
        E_master.append(diff)

        X.append([idx])
        idx += 1
        count += 1
    return X, Y, E_master

def construct_dual_input_feedforward_from_manifest(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()

    X = []
    Y = []
    # E1 = []
    # E2 = []
    E_master = []
    splits = [line.split(',') for line in lines]
    idx = 0
    n = len(splits)
    count = 0
    for split in splits:
        if count % 1000 == 0:
            print str(count), '/', str(n)
        curY = int(split[1])
        curE1 = [float(e) for e in split[2:52]]
        curE2 = [float(e) for e in split[52:]]
        Y.append(curY)
        E1_idx = idx
        E2_idx = idx + 1

        # E1.append(curE1)
        E_master.append(curE1)
        # E2.append(curE2)
        E_master.append(curE2)

        X.append([E1_idx, E2_idx])
        idx += 2
        count += 1
    return X, Y, E_master

    


def construct_single_feedforward_data(filename, embeddingDim):
    '''
    For constructing data for feedforward nerual net for classificiation
    on five classes based on quintiles of percentage change. 

    Filename refers to the check file. Third column is the percentage change. 
    First column is the ticker. Second column is the year.

    outDict is now [ticker, year, perChange, mc, date, filename, link, integerMapping]

    '''
    #dict of change : (ticker, year) mapping
    embeddingBase = 'embeddingDicts/embeddingDict_'
    embeddingFile = embeddingBase + str(embeddingDim) + '.pkl'


    dict = {}
    integerToFilename = {}
    with open(filename) as check:
        lines = check.readlines()
        for line in lines:
            data = line.split("\t")
            ticker = data[0].strip()
            year = data[1].strip()
            integer = int(data[-1].strip())
            data_filename = data[-3].strip()
            change = data[2].strip()
            if change == 'None':
                continue
            change = float(change)
            dict[change] = integer
            integerToFilename[integer] = data_filename

    #sort by change
    orderedList = dict.items()
    orderedList = sorted(orderedList, key = lambda t: t[0])

    #dict of (ticker, year) : label where label is from 0 to 4 with 0 being lowest
    #quintile and 4 being the highest quintile
    #will backload up to 4 labels of 4 (consider example if len = 24)
    listlen = len(orderedList)
    fifth = int(listlen/5)
    labelsDict = {}
    for i in range(listlen):
        labelsDict[orderedList[i][1]] = i/fifth if i/fifth <= 4 else 4 #backloading
        if i % fifth == 0:
            print(orderedList[i][0])

    # print len(labelsDict.keys())

    embeddingDict = pickle.load(open(embeddingFile, "rb"))

    embeddings = []
    labels = []
    for curInteger in sorted(labelsDict.keys()):
        curFilename = integerToFilename[curInteger]
        embeddings.append(list(embeddingDict[curFilename]))
        labels.append(labelsDict[curInteger])

    indices = range(len(embeddings))
    # print embeddings
    # print 'Ingested indices: ', indices
    # print indices
    # print X[:5]
    # print Y[:5]
    return indices, labels, embeddings


def construct_data(filename, path):
    '''
    Old: for RNN. But not enough data. 
    '''
    inflationDict = createInflationDict()
    orderedd2v, X = Doc2VecMapping(filename)
    marketCap = getMarketCap(path, inflationDict)

    #sliding window with current fixed window size of 5
    newX = []
    for key in orderedd2v:
        ticker = key[0]
        year = key[1]
        if (ticker, year + 4) in orderedd2v:
            newX.append([[orderedd2v[(ticker, year)],
                        orderedd2v[(ticker, year+1)]],
                        orderedd2v[(ticker, year+2)],
                        orderedd2v[(ticker, year+3)],
                        orderedd2v[(ticker, year+4)]])

    change = {}
    newY = []

    #label data for sliding window with fixed window size 5
    #EX x = (1,2,3,4,5,6,7)
    #EX new_x = ((1,2,3,4,5)
    #             2,3,4,5,6))
    #EX new_y = (y_5, y_6)

    for key in orderedd2v:
        company, year = key
        cap = marketCap[key]
        nextCap = marketCap.get((company, year + 1))
        #Offset of one. Percentage change for FY2015 is (Cap_2016 - Cap_2015)/Cap_2015
        if prevCompany == company and (company, year - 1) in orderedd2v:
            if nextCap is None:
                change[key] = -1 #sentinel to indicate last year
            else:
                percentChange = (cap - nextCap)/cap
                change[key] = percentChange

    for key in orderedd2v:
        ticker = key[0]
        year = key[1]
        if (ticker, year + 4) in orderedd2v:
            percentChange = change[(ticker, year + 4)]
            if percentChange != -1: #last year
                newY.append(change[(ticker, year + 4)])

    return newX, newY

def test_contiguous_data():
    '''
    Make sure that all years in data are adjacent to each other by year per company
    '''
    dict, val = Doc2VecMapping("fleet_model.d2v")
    test = True
    for key in dict:
        ticker, year = key
        if (ticker, year + 1) not in dict and ((ticker, year + 2) in dict or (ticker, year + 3) in dict):
            print key
            test = False
    if not test:
        print "CONTIGUOUS DATA CHECK FAILED!"

def test_check(filename):
    '''
    Fix Contiguous check
    '''
    length = 0
    with open("Data_Test.txt", "w") as output:
        with open(filename) as check:
            lines = check.readlines()
            length = len(lines)
            for line in lines:
                data = line.split("\t")
                year = data[4].split("-")[0]
                if data[1]!= year:
                    # output.write("Year Mismatch" + " " + data[0] + " " + data[1] + "\n")
                    output.write(data[5] + "\n")

                if data[2] != "None" and (float(data[2]) > 5 or float(data[2]) < -2):
                    # output.write("Suspicious Percentage Change" + " " + data[0]  + " " + data[1] + "\n")
                     output.write(data[5] + "\n")

                if data[3] != "None" and float(data[3]) < 100000000.0:
                    # output.write("Suspicious Market Cap" + " " + data[0]  + " " + data[1] + "\n")
                    output.write(data[5] + "\n")

        with open(filename) as check:
            lines = check.readlines()
            curr = []
            company = ""
            for line in lines:
                data = line.split("\t")
                if  data[0] == company:
                    curr.append(int(data[1]))
                else:
                    curr = [int(data[1])]
                if curr[-1] == 2016 and curr[-1] - curr[0] + 1 != len(curr):
                    output.write("Contiguous Data Fail" " " + data[0] + "\n")
                company = data[0]
                    
                
        output.write("File contains" + " " + str(length) + " 10ks" + "\n")

def createCheckFile(path, inflationDict, outPath):
    '''
    args: path is the path to the SEC filings
    Output: returns a dictionary mapping (ticker, year) : market capitalization
    '''
    filingDict = {}
    fileCounter = 0
    for subdir, dirs, files in os.walk(path):
        for f in files:
            if fileCounter % 500 == 0:
                print fileCounter, 'files processed.'
            docPath = os.path.join(subdir, f)
            filename, file_extension = os.path.splitext(f)
            if file_extension == ".txt" and 'embedding' not in filename:     
                infile = open(docPath, 'r')
                #Reading individual lines (so as to not open the entire thing), so ordering matters
                file_html = infile.readline().strip()
                index_html = infile.readline().strip()
                try:
                    mc = float(infile.readline().strip())
                except:
                    print filename
                    return
                ticker = infile.readline().strip()
                filingDate = infile.readline().strip()
                infile.close()
                filingYear = int(filingDate.split("-")[0])
                mc = mc*inflationDict[filingYear]

                if ticker not in filingDict:
                    filingDict[ticker] = {}
                if filingYear in filingDict[ticker]:
                    prevFiling = filingDict[ticker][filingYear]
                    curFiling = [ticker, str(filingYear), str(mc), filingDate, f, file_html]
                    prevDate = prevFiling[3]
                    if filingDate < prevDate:
                        firstData = curFiling
                        secondData = prevFiling
                    else:
                        firstData = prevFiling
                        secondData = curFiling
                        
                    if (filingYear - 1) not in filingDict[ticker]:
                        firstData[1] = str(filingYear - 1)
                        filingDict[ticker][filingYear - 1] = firstData
                        filingDict[ticker][filingYear] = secondData
                    else:
                        secondData[1] = str(filingYear + 1)
                        filingDict[ticker][filingYear] = firstData
                        filingDict[ticker][filingYear + 1] = secondData
                else:
                    filingDict[ticker][filingYear] = [ticker, str(filingYear), str(mc), filingDate, f, file_html]
            fileCounter += 1

    #Reformat every line
    fileCounter = 0
    outDict = {}
    for ticker in sorted(filingDict.keys()):
        outDict[ticker] = {}
        print ticker
        years = sorted(filingDict[ticker].keys())
        
        for yearIdx in range(len(years)):
            year = years[yearIdx]
            filing = filingDict[ticker][year]
            curMC = float(filing[2])

            #Not the last entry
            if curMC != 0:
                if yearIdx != len(filingDict[ticker].keys()) - 1:
                    nextYear = years[yearIdx + 1]
                    nextMC = float(filingDict[ticker][nextYear][2])
                    perChange = (nextMC - curMC) / curMC
                else:
                    perChange = None
            else:
                perChange = None
            outDict[ticker][yearIdx] = filing[:1] + [str(years[0]+yearIdx)] + [str(perChange)] + filing[2:] + [str(fileCounter)]
            fileCounter += 1

    # outDict is now [company, year, perChange, mc, date, filename, link, integerMapping]

    integerToFilenamePerChange = {}
    filenameToInteger = {}
    outFile = open(outPath, 'w+')

    for ticker in sorted(outDict.keys()):
        for yearIdx in sorted(outDict[ticker].keys()):
            line = outDict[ticker][yearIdx]

            integer = line[-1]
            filename = line[-3]
            perChange = line[2]

            integerToFilenamePerChange[integer] = [filename, perChange]
            filenameToInteger[filename] = integer

            outString = '\t'.join(outDict[ticker][yearIdx]) + '\n'
            outFile.write(outString)
    outFile.close()
    pickle.dump(integerToFilename, open('integerToFilenamePerChange.pkl', "wb+" ))
    pickle.dump(filenameToInteger, open('filenameToInteger.pkl', "wb+" ))


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Scrapes Market Cap from SEC db.')
    # parser.add_argument('-d','--directory', help='Directory containing financial documents', required=True)
    # args = vars(parser.parse_args())
    # mc = get_market_cap(args['directory'])
    # print mc
    # pickle.dump(mc, open("market_labels", "w"))
    # X, Y = construct_data("fleet_model.d2v", "data_scraping/SEC-Edgar-data")

    #construct_single_feedforward_data("check.txt", 50)
    X, Y, embed = construct_differential_feedforward_data("check.txt", 50, 5)
    for i in range(20):
        print X[i]
        print Y[i]
        print embed[i]
    # test_check("check.txt")