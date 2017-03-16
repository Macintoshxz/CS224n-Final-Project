import os
import pickle
import argparse
from gensim.models import Doc2Vec
from collections import OrderedDict

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
                print ticker
                year = int(filename[1].split("-")[0])
                marketCap[(ticker, year)] = float(mc)*inflationDict[year]
                #print mc
    return marketCap

def createInflationDict():
    '''
    Loads the manual-entry inflation_table.txt into a dict to convert
    the market caps to current day currency.
    '''
    path = 'inflation_table.txt'
    f = open(path, 'r')
    lines = f.readlines()
    f.close()
    inflationDict = {}
    for line in lines:
        year, rate =line.split('\t')
        inflationDict[int(year)] = float(rate)
    return inflationDict

def construct_data(filename, path):
    '''
    Constructs data in the format requried by TFLearn
    '''
    inflationDict = createInflationDict()
    orderedd2v, X = Doc2VecMapping(filename)
    marketCap = getMarketCap(path, inflationDict)
    print len(marketCap)
    Y = []
    prevCompany = ''
    prevCap = 1
    for key in orderedd2v:
        print key
        company, year = key

        cap = marketCap[key] if key in marketCap else 1

        #Make sure we offset one for predictions - we don't add until the next year
        if prevCompany == company:
            if key in marketCap:
                percentChange = (cap - prevCap)/prevCap
                Y.append(percentChange)
            else:
                Y.append(None)
        prevCap = cap
        prevCompany = company
    return X, Y



if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Scrapes Market Cap from SEC db.')
    # parser.add_argument('-d','--directory', help='Directory containing financial documents', required=True)
    # args = vars(parser.parse_args())
    # mc = get_market_cap(args['directory'])
    # print mc
    # pickle.dump(mc, open("market_labels", "w"))
    X, Y = construct_data("fleet_model.d2v", "data_scraping/SEC-Edgar-data")
    print Y
    import pdb; pdb.set_trace()



