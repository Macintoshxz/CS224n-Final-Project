import os
import re

def createLineWindow(lines, lineIdx):
    MAX_LINES_LOOKAHEAD = 3
    MAX_LINES_LOOKBEHIND = 3
    startIdx = max(0, lineIdx - MAX_LINES_LOOKBEHIND)
    endIdx = min(len(lines) - 1, lineIdx + MAX_LINES_LOOKAHEAD)
    return lines[startIdx:endIdx], startIdx

# Allows for custom handling of regexes if we want
def reFind(regex, text):
    m = re.search(regex, text)
    return m.start() if m else False

def isItem7InWindow(window, iteration):
    ITEM_DESC = r'management.?s\s*discussion\s*and\s*analysis\s*of\s*' + \
        r'financial\s*condition\s*and\s*results\s*of\s*operation'
    lowered = window.lower()
    i = '7'
    pos = None
    if iteration == 0:
        if reFind(r'ITEM\s*'+i+r'\.', window) and reFind(r'item\s*' + i + r'\.\s*' + ITEM_DESC, lowered):
            pos = reFind(r'ITEM.\s*' + i, window)
    if iteration == 1:
        if reFind(r'ITEM\s*'+i, window) and reFind(r'item\s*'+i+r'\s*' + ITEM_DESC, lowered):
            pos = reFind(r'ITEM\s*' + i, window)
    if iteration == 2:
        if reFind(r'item\s*'+i+r'\.', lowered) and reFind(r'item\s*'+i+r'\.\s*' + ITEM_DESC, lowered):
            pos = reFind(r'item.\s*'+i, lowered)
    if iteration == 3:
        if reFind(r'item\s*'+i, lowered) and reFind(r'item\s*'+i+r'\s*' + ITEM_DESC, lowered):
            pos = reFind(r'item\s*'+i, lowered)
    if iteration == 4:
        if reFind(r'item\s*'+i, lowered) and reFind(ITEM_DESC, lowered):
            pos = reFind(r'item.\s*'+i, lowered)

    #Things that will always trip false:
    if reFind(r'see\s*item\s*7', lowered):
        pos = None
        # print '1'
    if reFind(r'item\s*7\s*(continued)', lowered):
        pos = None
        # print '2'
    if reFind(r'operation\s*(continued)', lowered):
        pos = None
        # print '3'

    return pos

def isItem8InWindow(window, iteration):
    ITEM_DESC = r'financial\s*statements\s*and\s*supplementary\s*data'
    lowered = window.lower()
    i = '8'
    pos = None
    if iteration == 0:
        if reFind(r'ITEM\s*'+i+r'\.', window) and reFind(r'item\s*' + i + r'\.\s*' + ITEM_DESC, lowered):
            pos = reFind(r'ITEM.\s*' + i, window)
    if iteration == 1:
        if reFind(r'ITEM\s*'+i, window) and reFind(r'item\s*'+i+r'\s*' + ITEM_DESC, lowered):
            pos = reFind(r'ITEM\s*' + i, window)
    if iteration == 2:
        if reFind(r'item\s*'+i+r'\.', lowered) and reFind(r'item\s*'+i+r'\.\s*' + ITEM_DESC, lowered):
            pos = reFind(r'item.\s*'+i, lowered)
    if iteration == 3:
        if reFind(r'item\s*'+i, lowered) and reFind(r'item\s*'+i+r'\s*' + ITEM_DESC, lowered):
            pos = reFind(r'item\s*'+i, lowered)
    if iteration == 4:
        if reFind(r'item\s*'+i, lowered) and reFind(ITEM_DESC, lowered):
            pos = reFind(r'item.\s*'+i, lowered)

    #Things that will always trip false:
    if reFind(r'see\s*item\s*8', lowered):
        pos = None
    if reFind(r'item\s*8\s*(continued)', lowered):
        pos = None

    return pos

def isGeneralItemInWindow(window, iteration, i):
    i = str(i)
    ITEM_DESC = descDict[i]
    lowered = window.lower()
    pos = None
    if iteration == 0:
        if reFind(r'ITEM\s*'+i+r'\.', window) and reFind(r'item\s*' + i + r'\.\s*' + ITEM_DESC, lowered):
            pos = reFind(r'ITEM.\s*' + i, window)
    if iteration == 1:
        if reFind(r'ITEM\s*'+i, window) and reFind(r'item\s*'+i+r'\s*' + ITEM_DESC, lowered):
            pos = reFind(r'ITEM\s*' + i, window)
    if iteration == 2:
        if reFind(r'item\s*'+i+r'\.', lowered) and reFind(r'item\s*'+i+r'\.\s*' + ITEM_DESC, lowered):
            pos = reFind(r'item.\s*'+i, lowered)
    if iteration == 3:
        if reFind(r'item\s*'+i, lowered) and reFind(r'item\s*'+i+r'\s*' + ITEM_DESC, lowered):
            pos = reFind(r'item\s*'+i, lowered)
    if iteration == 4:
        if reFind(r'item\s*'+i, lowered) and reFind(ITEM_DESC, lowered):
            pos = reFind(r'item.\s*'+i, lowered)

    #Things that will always trip false:
    if reFind(r'see\s*item\s*'+i, lowered):
        pos = None
    if reFind(r'item\s*'+i+r'\s*(continued)', lowered):
        pos = None

    return pos

# Global variables that needs to be manuall updated as we modify this code
# this encodes the number of switch cases for each item
switchLengths = {'7': 5, '8': 5}
functionDict = {
    '7': isItem7InWindow,
    '8': isItem8InWindow
}

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


def getPosFromStart(lines, lineIdx, pos):
    priorLines = lines[:lineIdx]
    numPrevChars = len('\n'.join(priorLines))
    return pos + numPrevChars

def isItemInWindow(sectionNum, window, iteration):
    functionDict[sectionNum](window, iteration)

def extractSectionStartPos(lines, sectionNum):
    # for iteration in xrange(switchLengths[sectionNum]):
    for iteration in xrange(5):
        for lineIdx in range(len(lines)):
            line = lines[lineIdx]
            windowLines, windowStartIdx = createLineWindow(lines, lineIdx)
            window = ' '.join(windowLines)
            # pos = functionDict[sectionNum](window, iteration)
            pos = isGeneralItemInWindow(window, iteration, sectionNum)
            if pos:
                return getPosFromStart(lines, windowStartIdx, pos)
    return None

SECTION_NAMES = ['1', '1a', '1b', '2', '3', '5', '6', '7', '7a', '8', '9', '9a', '9b', '10', \
    '11', '12', '13', '14', '15']

def removeMissingLetteredSections(positions):
        n = len(positions)
        newPositions = []
        newNames = []

        letteredIndices = [1, 2, 8, 11, 12, 17]
        for i in xrange(n):
            if positions[i] == None and i in letteredIndices:
                continue
            newPositions.append(positions[i])
            newNames.append(SECTION_NAMES[i])
        return newPositions, newNames

def extractSectionPositions(body, header, targetPath, logFile):
    positions = [extractSectionStartPos(body, section) for section in SECTION_NAMES]
    positions, names = removeMissingLetteredSections(positions)
    print 'Extracting', targetPath, 'positions:\n', str(positions)
    n = len(positions)
    for i in xrange(n):
        curPos = positions[i]
        curName = names[i]
        if curPos == None:
            continue

        sectionFirst = targetPath[:targetPath.rfind('\\')]
        sectionSecond =  targetPath[targetPath.rfind('\\'):].split('.')[0] + '_section_' + curName + '.txt'
        sectionPath = sectionFirst + sectionSecond
        fullString = '\n'.join(body)
        section = None
        if i < n - 1:
            nextPos = positions[i+1]
            if nextPos == None:
                continue
            section = fullString[curPos:nextPos]
        else:
            section = fullString[curPos:]

        if isActualSection(section):
            g = open(sectionPath, 'w+')
            g.write(header)
            g.write(section)
            g.close()
    logFile.write(str(positions) + '\t' + targetPath + '\n')


def extractSection(lines, startSection, endSection):
    # lines = lines[startHeuristic:]
    # inputs = ['a']
    pos7 = extractSectionStartPos(lines, startSection)
    pos8 = extractSectionStartPos(lines, startSection + 1)
    if pos7 is None or pos8 is None:
        return None, pos7, pos8

    fullString = '\n'.join(lines)
    return fullString[pos7:pos8], pos7, pos8

def isActualSection(text):
    if text is None:
        return False
    MIN_CHARS = 2000
    if len(text) < MIN_CHARS:
        return False
    return True

def extractAllSections():
    FIRST_LINE = 8 #Defined by our data structure
    path = "SEC-Edgar-data"
    targetPaths = []
    for subdir, dirs, files in os.walk(path):
        for f in files:
            if 'embedding' not in f:
                docPath = os.path.join(subdir, f)
                targetPaths.append(docPath)

    totalPaths = len(targetPaths)
    # targetPaths = targetPaths[300:]
    count = 0
    numFindErrors = 0
    numRefErrors = 0
    errorFile = open('extractionErrors.txt', 'w+')
    targetSections = [7]

    count = 0
    logFile = open('extractAllLog.txt', 'w+')
    skip = True
    for targetPath in targetPaths:
        if 'section' not in targetPath:
            #Don't overwrite
            # if os.path.isfile(sectionPath):
            #     continue

            if 'STI' in targetPath:
                skip = False

            # if skip:
            #     continue

            f = open(targetPath, 'r')
            lines = f.readlines()
            f.close()
            
            header = ''.join(lines[:FIRST_LINE])
            body = lines[FIRST_LINE:]
            extractSectionPositions(body, header, targetPath, logFile)
    logFile.close()

def test():
    FIRST_LINE = 8 #Defined by our data structure
    path = "SEC-Edgar-data"
    targetPaths = []
    for subdir, dirs, files in os.walk(path):
        for f in files:
            if 'embedding' not in f:
                docPath = os.path.join(subdir, f)
                targetPaths.append(docPath)

    totalPaths = len(targetPaths)
    # targetPaths = targetPaths[300:]
    count = 0
    numFindErrors = 0
    numRefErrors = 0
    errorFile = open('extractionErrors.txt', 'w+')
    targetSections = [7]

    count = 0
    for targetSection in targetSections:
        for targetPath in targetPaths:
            if 'section' not in targetPath:
                sectionFirst = targetPath[:targetPath.rfind('\\')]
                sectionSecond =  targetPath[targetPath.rfind('\\'):].split('.')[0] + '_section_' + str(targetSection) + '.txt'
                sectionPath = sectionFirst + sectionSecond

                #Don't overwrite
                # if os.path.isfile(sectionPath):
                #     continue

                f = open(targetPath, 'r')
                lines = f.readlines()
                f.close()
                
                header = ''.join(lines[:FIRST_LINE])
                body = lines[FIRST_LINE:]
                section, pos7, pos8 = extractSection(targetPath, body, 7)
                statusString = targetPath + ' ' + str(pos7) + ' ' + str(pos8)
                print statusString
                if section is not None and isActualSection(section):
                    g = open(sectionPath, 'w+')
                    g.write(header)
                    g.write(section)
                    g.close()
                else:
                    if not section:
                        numFindErrors +=1
                        print 'findError'
                    elif not isActualSection(section):
                        numRefErrors += 1
                        print 'numRefError'
                    errorFile.write(statusString + '\n')
                if count % 200 == 0:
                    print count, 'files processed'
                count += 1
    errorString = 'Num findErrors: ' + str(numFindErrors) + ', Num refErrors: ' + str(numRefErrors)
    print errorString
    errorFile.write('\n' + errorString + '\nNum completed: ' + str(count))
    errorFile.close()

if __name__ == '__main__':
    # test()
    extractAllSections()