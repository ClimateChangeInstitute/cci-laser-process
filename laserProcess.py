#!/usr/bin/env python

import re
import sys
from fileinput import filename


class LaserFile:
    def __init__(self, fileName, laserTime, startDepth, endDepth, washinTime, washoutTime, header, rows):
        self.fileName = fileName
        self.laserTime = laserTime
        self.startDepth = startDepth
        self.endDepth = endDepth
        self.washinTime = washinTime
        self.washoutTime = washoutTime
        self.header = header 
        self.rows = rows
        self.baseLineAve = [0, 0, 0, 0, 0, 0]  # No average recorded

    def __str__(self):
        return self.fileName
    
    def __repr__(self):
        return self.__str__()

def readFile(fileName, laserTime, startDepth, endDepth, washinTime, washoutTime):
    
    rows = []
    
    linNumber = 1
    for line in open(fileName):
            if linNumber > 6 : 
                rows.append(line.split())
            elif linNumber == 1:
                header = line.split("\t")
                header[0] = "Time"
                for i in range(1, len(header)):
                    header[i] = re.sub("\(.*\)", "", header[i]).strip()
            
            linNumber += 1
                
    return LaserFile(fileName, laserTime, startDepth, endDepth, washinTime, washoutTime, header, rows)

def formatRow(r):
    result = ""
    
    for i in r:
        result += str(i) + "\t" 
        
    return result

def getFiles(inputFile):
    """
    """
    
    result = []
    
    for line in open(inputFile) :
        if not line.startswith("#"):
            columns = line.split()
            result.append(readFile(columns[0], float(columns[1]), float(columns[2]), float(columns[3]), float(columns[4]), float(columns[5])))
    
    return result

def readDepthToAgeFile(fileName) :

    matrix = [[], [], []]

    for line in open(fileName) :
        if not line.startswith("Depth") :
            columns = line.split()
            matrix[0].append(float(columns[0]))
            matrix[1].append(float(columns[1]))
            matrix[2].append(float(columns[2]))
        
    return matrix
    

def averageBaseLists(aveList) :
    """
    Take a matrix and average each column.  
    Return a list that is the average of each column.
    """
    result = [0, 0, 0, 0, 0, 0]
    
    if len(aveList) > 0 :
        for col in range(len(aveList[0])) :
            s = 0
            for row in aveList :
                s = s + row[col]
                
            result[col] = s / len(aveList)
        
    return result

def subtractAveFromColumns(baseLineAve, newRows) :
    """
    Subtract base line average from each value in the new row.
    """
    result = []
    for row in newRows :
        resultRow = [row[0]]
        for col in range(len(baseLineAve)) :
            resultRow.append(row[col] - baseLineAve[col])
        result.append(resultRow)

    return result

def trimBeginning(f, washinTime):
    """
    """
    newRows = []
    aveList = []
    for row in f.rows:
        if float(row[0]) >= washinTime:
            newRows.append([float(i) for i in row])
        else :
            aveList.append([float(i) for i in row])

    if len(aveList) > 0 :
        f.baseLineAve = averageBaseLists(aveList)
    
    f.rows = subtractAveFromColumns(f.baseLineAve, newRows)

def trimEnding(f, laserTime, washoutTime):
    """
    """
    newRows = []
    for row in f.rows:
        if float(row[0]) < laserTime + washoutTime:
            newRows.append(row) 

    f.rows = newRows
    
    

def addDepthColumn(f, startDepth, endDepth):
    """
    """
    
    inc = (endDepth - startDepth) / (len(f.rows) - 1)
    
    curDepth = startDepth
    f.header.insert(0, "Depth")
    for i in range(len(f.rows)) :
        f.rows[i].insert(0, curDepth)
        curDepth += inc
        

def combine(laserFiles):
    """
    """
    result = []
    for f in laserFiles: 
        result.extend(f.rows)
    
    return result

def writeOutputFile(outputFileName, header, rows):
    
    f = open(outputFileName, "w")
    
    for i in range(len(header) - 1):
        f.write(header[i] + "\t")
    f.write(header[len(header) - 1] + "\n")
    
    for r in rows:
        f.write(formatRow(r) + "\n")

    f.close()
    
def findIndex(col, allRows, DepthAbsCM) :
    """
    Return the index of the row of column col in allRows such 
    that allRows[row][col] < DepthAbsCM[row]  
    """
    
    for row in range(len(allRows)) :
        if allRows[row][col] < DepthAbsCM[row] :
            return row
        
    return -1 # Not found; something is weird
    

def processFiles(inputFileName, outputFileName):
    
    print "Using input file '%s'" % (inputFileName)
    print "Writing to file '%s'" % (outputFileName)
     
    files = getFiles(inputFileName)
         
    for f in files:
        print "Processing fileName %s" % (f.fileName)
        trimBeginning(f, f.washinTime)
        trimEnding(f, f.laserTime, f.washoutTime)
        addDepthColumn(f, f.startDepth, f.endDepth)
        print "The base line average times %s " % f.baseLineAve
    
    allRows = combine(files)

    # Setup depth and age data variables    
    matrix = readDepthToAgeFile("DepthtoAge.csv")
    DepthWEqM = matrix[0]
    Age = matrix[1]
    DepthAbsCM = matrix[2]

    # TODO need to finish processing this 
    for i in range(len(allRows)) :
        loc = findIndex(0, allRows, DepthAbsCM)


    
    writeOutputFile(outputFileName, files[0].header, allRows)

if __name__ == '__main__':
    
    if len(sys.argv) != 3 :
        print "Usage: laserProcess.py inputFileName outputFileName"
        sys.exit(-1)
    
    inputFileName = sys.argv[1]
    outputFileName = sys.argv[2]
    
    processFiles(inputFileName, outputFileName)
