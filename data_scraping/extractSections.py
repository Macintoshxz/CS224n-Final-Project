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

# Global variables that needs to be manuall updated as we modify this code
# this encodes the number of switch cases for each item
switchLengths = {7: 5, 8: 5}
functionDict = {
    7: isItem7InWindow,
    8: isItem8InWindow
}


def getPosFromStart(lines, lineIdx, pos):
    priorLines = lines[:lineIdx]
    numPrevChars = len('\n'.join(priorLines))
    # print numPrevChars
    return pos + numPrevChars

def isItemInWindow(sectionNum, window, iteration):
    functionDict[sectionNum](window, iteration)

def extractSectionStartPos(lines, sectionNum):
    for iteration in xrange(switchLengths[sectionNum]):
        for lineIdx in range(len(lines)):
            line = lines[lineIdx]
            windowLines, windowStartIdx = createLineWindow(lines, lineIdx)
            window = ' '.join(windowLines)
            pos = functionDict[sectionNum](window, iteration)
            if pos:
                return getPosFromStart(lines, windowStartIdx, pos)
    return None

def extractSection(path, lines, startSection, startHeuristic=50):
    lines = lines[startHeuristic:]
    # inputs = ['a']
    pos7 = extractSectionStartPos(lines, startSection)
    pos8 = extractSectionStartPos(lines, startSection + 1)
    if pos7 is None or pos8 is None:
        return None, pos7, pos8

    fullString = '\n'.join(lines)
    return fullString[pos7:pos8], pos7, pos8

def isActualSection(text):
    MIN_CHARS = 2000
    if len(text) < MIN_CHARS:
        return False
    return True

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
    test()