import os
import re

def createLineWindow(lines, lineIdx):
    MAX_LINES_LOOKAHEAD = 3
    MAX_LINES_LOOKBEHIND = 3

    return lines[max(0, lineIdx - MAX_LINES_LOOKBEHIND): \
        min(len(lines) - 1, lineIdx + MAX_LINES_LOOKAHEAD)]

def reFind(regex, text):
    found = re.findall(regex, text)
    if len(found) == 0:
        return False
    return True

def isItem7InWindow(window, iteration):
    ITEM_7_DESC = r'management.?s\s*discussion\s*and\s*analysis\s*of\s*' + \
        r'financial\s*condition\s*and\s*results\s*of\s*operation'
    lowered = window.lower()

    found = False
    if iteration == 0:
        if reFind(r'ITEM\s*7', window) and reFind(ITEM_7_DESC, lowered):
            print window + '\n\n'
            found = True
    elif iteration == 1:
        if 'ITEM 7.' in window:
            print 'WOO2\n'

    #Things that will always trip false:
    if reFind(r'see\s*item\s*7', lowered):
        found = False
    if reFind(r'item\s*7\s*(continued)', lowered):
        found = False
    if reFind(r'operation\s*(continued)', lowered):
        found = False

    return found


# Global variables that needs to be manuall updated as we modify this code
# this encodes the number of switch cases for each item
switchLengths = {7: 2, 8: 5}
functionDict = {
    7: isItem7InWindow
}


def isItemInWindow(sectionNum, window, iteration):
    functionDict[sectionNum](window, iteration)

def extractSection(lines, inputs, sectionNum):
    for iteration in xrange(switchLengths[sectionNum]):
        for lineIdx in range(len(lines)):
            line = lines[lineIdx]
            windowLines = createLineWindow(lines, lineIdx)
            window = ' '.join(windowLines)
            found = functionDict[sectionNum](window, iteration)
            if found:
                print 'FOUND!'
                return
        return

def processLines(lines):
    startHeuristic = 50
    lines = lines[startHeuristic:]
    inputs = ['a']
    extractSection(lines, inputs, 7)

def test():
    path = "SEC-Edgar-data"
    targetPaths = []
    for subdir, dirs, files in os.walk(path):
        for f in files:
            if 'embedding' not in f:
                docPath = os.path.join(subdir, f)
                targetPaths.append(docPath)

    totalPaths = len(targetPaths)
    for targetPath in targetPaths:
        f = open(targetPath, 'r')
        lines = f.readlines()
        f.close()
        print targetPath
        processLines(lines)
        # print lines[:20]
        break

if __name__ == '__main__':
    test()