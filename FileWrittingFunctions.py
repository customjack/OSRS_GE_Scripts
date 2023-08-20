import time
import copy
import os
CWD = os.getcwd()
#EXPORT_LOCATION = os.path.join(CWD,'DataFiles')
EXPORT_LOCATION = CWD

def writeToFile(fName,items,num):
   timeStamp = findTime()
   print(len(items))
   with open(fName, 'w+') as f:
       f.write('TIMESTAMP: ' + str(timeStamp) + '\n' + '\n')
       for i in range(num):
            try:
                f.write(str(items[i][0]) + ':' + '\n')
                f.write('Margin: ' + str(items[i][1]))
                N = len(str(items[i][1])) + 7
                M = 40 - N
                f.write(' '*M)
                f.write('ROI: ' + str(items[i][2]) + '\n')
            except:
                print(items)
            
            f.write('Selling: ' + str(items[i][3]))
            N = len(str(items[i][3])) + 8
            M = 40 - N
            f.write(' '*M)
            f.write('Buying ' + str(items[i][4]) + '\n')
            
            f.write('Quantity Sold: ' + str(items[i][5]))
            N = len(str(items[i][5])) + 14
            M = 40 - N
            f.write(' '*M)
            f.write('Quantity Bought: ' + str(items[i][6]) + '\n')
            
            f.write('Buying Limit: ' + str(items[i][7]))
            N = len(str(items[i][7])) + 13
            M = 40 - N
            f.write(' '*M)
            f.write('Expected Profit Per Hour: ' + str(items[i][8]) + '\n')
            
            f.write('% Min (Week): ' + str(items[i][9]))
            N = len(str(items[i][9])) + 13
            M = 40 - N
            f.write(' '*M)
            f.write('% Min (Month): ' + str(items[i][10]) + '\n')
            
            f.write('% Max (Week): ' + str(items[i][11]))
            N = len(str(items[i][11])) + 13
            M = 40 - N
            f.write(' '*M)
            f.write('% Max (Month): ' + str(items[i][12]) + '\n')
            
            f.write('Weekly Volatility: ' + str(items[i][13]))
            N = len(str(items[i][13])) + 18
            M = 40 - N
            f.write(' '*M)
            f.write('Monthly Volatility: ' + str(items[i][14]) + '\n')
            
            if items[i][15] > 0:
                f.write('Trend: ' + '+' + str(items[i][15]))
            else:
                f.write('Trend: ' + str(items[i][15]))
            f.write('\n\n')

def lunarWrite(fName,treeList,num):
    timeStamp = findTime()
    items = copy.deepcopy(treeList)
    if len(treeList) < num:
        num = len(treeList)
    with open(fName, 'w+') as f:
        f.write('TIMESTAMP: ' + str(timeStamp) + '\n' + '\n')
        for i in xrange(num):
            f.write(str(items[i][0]) + ':' + '\n')
            
            firstString = 'Input Quick Buy: ' + str(items[i][1])
            f.write(firstString)
            N = len(firstString)
            M = 40 - N
            f.write(' '*M)
            f.write('Input Slow Buy: ' + str(items[i][2]) + '\n')
            
            firstString = 'Output Quick Sell: ' + str(items[i][3])
            f.write(firstString)
            N = len(firstString)
            M = 40 - N
            f.write(' '*M)
            f.write('Output Slow Sell: ' + str(items[i][4]) + '\n')
            
            firstString = 'Weekly Input Min: ' + str(items[i][5])
            f.write(firstString)
            N = len(firstString)
            M = 40 - N
            f.write(' '*M)
            f.write('Weekly Input Max: ' + str(items[i][6]) + '\n')
            
            firstString = 'Weekly Output Min: ' + str(items[i][7])
            f.write(firstString)
            N = len(firstString)
            M = 40 - N
            f.write(' '*M)
            f.write('Weekly Output Max: ' + str(items[i][8]) + '\n')
            
            firstString = 'Profit/item Quick: ' + str("{:,}".format(items[i][9]))
            f.write(firstString)
            N = len(firstString)
            M = 40 - N
            f.write(' '*M)
            f.write('Profit/item Slow: ' + str("{:,}".format(items[i][10])) + '\n')
            
            firstString = 'Profit/hr Quick: ' + str("{:,}".format(items[i][11]))
            f.write(firstString)
            N = len(firstString)
            M = 40 - N
            f.write(' '*M)
            f.write('Profit/hr Slow: ' + str("{:,}".format(items[i][12])) + '\n')
            
            f.write('\n\n')

def trendSort(items):
    itemsEdit = copy.deepcopy(items)
    newItems = []
    brokenItems = []
    lastBreak = 0
    for i0,i in enumerate(itemsEdit):
        if i0 != 0:
            if itemsEdit[i0-1][9] != itemsEdit[i0][9]:
                brokenItems.append(itemsEdit[lastBreak:i0])
                lastBreak = i0
    if len(brokenItems) == 0:
        brokenItems.append(itemsEdit)
    for i in brokenItems:
        if len(i) != 1:
            i.sort(key=lambda pair: pair[11])
    for i in brokenItems:
        newItems += i
    return newItems
        

def bestROI(items):
    writeToFile(os.path.join(EXPORT_LOCATION,'BestROI.txt'),items,50)

def highVolume(items):
    newitems = []
    for i in items:
        if i[5] > 5000:
            newitems.append(i)
    N = len(newitems)
    if N > 50:
        N = 50
    writeToFile(os.path.join(EXPORT_LOCATION,'HighVolume.txt'),newitems,N)
    
def highValue(items):
    newitems = []
    for i in items:
        if i[3] >= 500000:
            newitems.append(i)
    N = len(newitems)
    if N > 50:
        N = 50
    writeToFile(os.path.join(EXPORT_LOCATION,'HighValue.txt'),newitems,N)
    
def veryHighValue(items):
    newitems = []
    for i in items:
        if i[3] >= 2500000:
            newitems.append(i)
    N = len(newitems)
    if N > 50:
        N = 50
    writeToFile(os.path.join(EXPORT_LOCATION,'VeryHighValue.txt'),newitems,N)
    
def bestProfit(items):
    newitems = copy.deepcopy(items)
    newitems.sort(key=lambda pair: pair[8])
    newitems = list(reversed(newitems))
    N = len(newitems)
    if N > 50:
        N = 50
    writeToFile(os.path.join(EXPORT_LOCATION,'bestProfit.txt'),newitems,N)
    
def medVolume_medValue(items):
    newitems = []
    for i in items:
        if i[3] >= 1000 and (i[5] > 1000 or i[6] > 1000):
            newitems.append(i)
    N = len(newitems)
    if N > 50:
        N = 50
    if N != 0:
        writeToFile(os.path.join(EXPORT_LOCATION,'MidPV.txt'),newitems,N)
    
def bestTrend(items):
    newitems = []
    for i in items:
        if (i[9] != 'unknown'):
            newitems.append(i)
    newitems.sort(key=lambda pair: pair[9])
    newitems = trendSort(newitems)
    N = len(newitems)
    if N > 50:
        N = 50
    if N != 0:
        writeToFile(os.path.join(EXPORT_LOCATION,'BestTrend.txt'),newitems,N)

def bestTrendAndMedVol(items):
    newitems = []
    for i in items:
        if i[3] >= 1000 and (i[5] > 1000 or i[6] > 1000) and (i[9] != 'unknown'):
            newitems.append(i)
    N = len(newitems)
    if N > 50:
        N = 50
    newitems.sort(key=lambda pair: pair[9])
    newitems = trendSort(newitems)
    if N != 0:
        writeToFile(os.path.join(EXPORT_LOCATION,'BestTrendMedVol.txt'),newitems,N)
    
def bestTrendAndHighPrice(items):
    newitems = []
    for i in items:
        if i[3] >= 1000000 and (i[9] != 'unknown'):
            newitems.append(i)
    N = len(newitems)
    if N > 50:
        N = 50
    newitems.sort(key=lambda pair: pair[9])
    newitems = trendSort(newitems)
    print(newitems)
    if N != 0:
        writeToFile(os.path.join(EXPORT_LOCATION,'BestTrendHighPrice.txt'),newitems,N)

def findTime():
    t = time.localtime()
    hour = str(t[3])
    minute = str(t[4])
    second = str(t[5])
    if len(hour) == 1:
        hour = '0' + hour
    if len(minute) == 1:
        minute = '0' + minute
    if len(second) == 1:
        second = '0' + second
    good = hour + ':' + minute + ':' + second
    return good
    
def treeSeeds(treeDict,fname,spellType='tree'):
    """Originally re-organizes tree seed prices, but works for most lunar processesing
    """
    treeList = []
    actionsPerHour = 0
    if spellType == 'tree':
        actionsPerHour = 1700
    elif spellType == 'dhide':
        actionsPerHour = 6000
    elif spellType == 'jewlery':
        actionsPerHour = 20000

    for key,value in treeDict.iteritems():
        name             = key
        seedQuick        = value['inputQuick']
        seedSlow         = value['inputSlow']
        saplingQuick     = value['outputQuick']
        saplingSlow      = value['outputSlow']
        weeklySeedMin    = value['inputWeeklyMin']
        weeklySeedMax    = value['inputWeeklyMax']
        weeklySaplingMin = value['outputWeeklyMin']
        weeklySaplingMax = value['outputWeeklyMax']
        quickProfit      = saplingQuick - seedQuick
        slowProfit       = saplingSlow  - seedSlow
        profitPerHourQuick = actionsPerHour*quickProfit
        profitPerHourSlow  = actionsPerHour*slowProfit
        treeList.append([name,seedQuick,seedSlow,saplingQuick,saplingSlow,weeklySeedMin,weeklySeedMax,weeklySaplingMin,weeklySaplingMax,quickProfit,slowProfit,profitPerHourQuick,profitPerHourSlow])
    quickProfit = copy.deepcopy(treeList)
    slowProfit  = copy.deepcopy(treeList)
    quickProfit.sort(key=lambda pair: pair[11])
    quickProfit = list(reversed(quickProfit))
    slowProfit.sort(key=lambda pair: pair[12])
    slowProfit  = list(reversed(slowProfit))
    lunarWrite('Quick' + fname + '.txt', quickProfit, 8)
    lunarWrite('Slow' + fname + '.txt', slowProfit, 8)
        
