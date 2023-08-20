from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

#PATH imports
import json
import os
import shutil as sh
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import copy
import numpy as np
import sys
import resource
import gc

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

#import deeper as deep
import FileWrittingFunctions as writing
import deeper as deep


#Classes:
class timelineData:
    def __init__(self, Max, Min, Vol):
            self.max = Max
            self.min = Min
            self.vol = Vol

gc.enable()

#Global Variables:
MINS = 10 #number of mins to wait between queries
DATABASE = 'https://storage.googleapis.com/osbuddy-exchange/summary.json'
http = urllib3.PoolManager()
CWD = os.getcwd()
Months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
BACKUPS = os.path.join(CWD,'pastDataBackups')
CURRENT_DATAFILE = os.path.join(CWD,'pastData.dat')
NEW_DATAFILE     = os.path.join(CWD,'newPastData.dat')
OUTPUTS = os.path.join(CWD,'DataFiles')
SCOPES = 'https://www.googleapis.com/auth/drive'

#Global Seed Variables
SEED_NAMES  = ['Magic','Calquat','Palm','Yew','Mahogany','Teak','Papaya','Maple','Curry','Pineapple','Apple','Willow']
SEED_IDS    = [5316,5290,5289,5315,21488,21486,5288,5314,5286,5287,5283,5313]
SAPLING_IDS = [5374,5503,5502,5373,21480,21477,5501,5372,5499,5500,5496,5371]
treeDict    = {}
for i0,i in enumerate(SEED_NAMES):
    treeDict[i] = {'inputId':SEED_IDS[i0],'outputId':SAPLING_IDS[i0]}

#Global Dragonhide variables
HIDE_NAMES  = ['Black','Red','Blue','Green']
HIDE_IDS    = [1747,1749,1751,1753]
LEATHER_IDS = [2509,2507,2505,1745]
hideDict    = {}
for i0,i in enumerate(HIDE_NAMES):
    hideDict[i] = {'inputId':HIDE_IDS[i0],'outputId':LEATHER_IDS[i0]}

#Global Dragonstone Variables
JEWLERY_NAMES = ['Amulet of Glory','Combat Bracelet','Skills Necklace']
UNCHARGED_IDS = [1704,11126,11113]
CHARGED_IDS   = [1712,11118,11105]
jewleryDict   = {}
for i0,i in enumerate(JEWLERY_NAMES):
    jewleryDict[i] = {'inputId':UNCHARGED_IDS[i0],'outputId':CHARGED_IDS[i0]}

#errorStreak
errorStreak = 0

#Approximate RAM usage increase between iterations:

    
    
    
def getData(verbose=False):
    """MAIN FUNCTIION
        returns a list of data to be output to files
    """
    items_list = getOSBuddyData()
    items_list_length = str(len(items_list))
    item_properties = []
    idList = getIdList()
    linesPerChunk = getNumberOfLinesToTake()
    pastData,last,start = getPastDataChunk(0,linesPerChunk,verbose=verbose)
    removals = 0
    additions = 0
    totalLines = file_len()
    with open('newPastData.dat', 'w+') as newData:
        for i0,i in enumerate(items_list):
            #Information declared as variables
            itemId       = str(i[0])
            int_itemId   = int(i[0])
            name         = i[1]['name']
            if verbose == True:
                print(itemId + ':  ' + name)
                print(str(i0+1) + '/' + items_list_length)
            buyPrice     = i[1]['buy_average']
            sellPrice    = i[1]['sell_average']
            buyQuantity  = i[1]['buy_quantity']
            sellQuantity = i[1]['sell_quantity']
            
            #Import the correct line of the old pastData file
            if (i0+removals-additions) > last:
                del pastData
                pastData,last,start = getPastDataChunk(last+1,linesPerChunk,verbose=verbose)
                removals = 0
            line_num = i0 - start
            
            if itemId not in idList:
                additions+=1
                if verbose == True:
                    print()
                    print('Missing Item! ' + str(itemId) + ': ' +str(name))
                    print()
                if (buyPrice!=0) and (sellPrice!=0):
                    pastData.insert(line_num, {str(itemId):{'name':name,'buylimit':'unknown','buyingHistory':{TIME:buyPrice},'sellingHistory':{TIME:sellPrice}}})
                else:
                    pastData.insert(line_num, {str(itemId):{'name':name,'buylimit':'unknown','buyingHistory':{},'sellingHistory':{}}})
            
            try:
                buylimit = pastData[line_num][itemId]['buylimit']
            except KeyError: #If the item is removed or reId'd for some reason it just skips the item (not fool proof, but should work for now)
                for key,val in pastData[line_num].iteritems():
                    realId = key
                    if verbose == True:
                        print('Loggged ID: ' + str(key))
                        print(pastData[line_num][key]['name'])
                if (realId not in idList) and (items_list_length != totalLines):
                    if verbose == True:
                        print('This item was removed from trade, writing all past data to file and skipping')
                    items_list.insert(i0+1,itemId)
                    newData.write(json.dumps(pastData[line_num]))
                    newData.write('\n')
                    continue
                else:
                    if verbose == True:
                        print('Item list out of order!')
                    raise NameError('Item List out of order!')
            
            #Update pastData
            if (buyPrice != 0) and (sellPrice != 0):
                pastData[line_num][itemId]['buyingHistory'][TIME] = buyPrice
                pastData[line_num][itemId]['sellingHistory'][TIME] = sellPrice
            
            #Extract timeline data from pastData
            hourPrices, weekPrices, monthPrices = dataExtractionAndRefinement(1000000,itemId,pastData,line_num)
            weeklyData, monthlyData = getTimelineData(weekPrices,monthPrices)
            
            #timeLine data mins/maxes
            if buyPrice != 0 and weeklyData.min != 0:
                percentOfWeeklyMin  = float(buyPrice)/float(weeklyData.min)
            else:
                percentOfWeeklyMin = 'unknown'
            if buyPrice != 0 and weeklyData.max != 0:
                percentOfWeeklyMax  = float(buyPrice)/float(weeklyData.max)
            else:
                percentOfWeeklyMax = 'unknown'
            weeklyVolatility    = weeklyData.vol
            if buyPrice != 0 and monthlyData.min != 0:
                percentOfMonthlyMin = float(buyPrice)/float(monthlyData.min)
            else:
                percentOfMonthlyMin = 'unknown'
            if buyPrice != 0 and monthlyData.max != 0:
                percentOfMonthlyMax = float(buyPrice)/float(monthlyData.max)
            else:
                percentOfMonthlyMax = 'unknown'
            monthlyVolatility   = monthlyData.vol
            
            #Hourly trend
            hourPrices.sort(key=lambda pair: pair[1])
            num_hourPoints = len(hourPrices)
            if num_hourPoints > 1:
                trend = hourPrices[-1][0] - hourPrices[0][0]
            else:
                trend = 0
            
            #Margin Calculation
            if buyPrice != 0 and sellPrice != 0:
                margin = abs(buyPrice-sellPrice)
            else:
                margin = 0
            #ROI Calculation
            try:
                ROI = float(margin)/float(buyPrice)
            except:
                ROI = 0
            
            #Profit/hr
            if buylimit == 'unknown':
                if sellQuantity < 20000:
                    profitPerHr = sellQuantity*sellPrice
                else:
                    profitPerHr = 0
            else:
                if sellQuantity > buylimit:
                    profitPerHr = buylimit*sellPrice
                else:
                    profitPerHr = sellQuantity*sellPrice
            
            
            #Tree Seeds
            if int_itemId in SEED_IDS:
                seed_index  = SEED_IDS.index(int_itemId)
                seedName    = SEED_NAMES[seed_index]
                quickBuy    = max(buyPrice,sellPrice)
                slowBuy     = min(buyPrice,sellPrice)
                treeDict[seedName]['inputQuick']      = quickBuy
                treeDict[seedName]['inputSlow']       = slowBuy
                treeDict[seedName]['inputWeeklyMin']  = percentOfWeeklyMin
                treeDict[seedName]['inputWeeklyMax']  = percentOfWeeklyMax
                
            if int_itemId in SAPLING_IDS:
                sapling_index  = SAPLING_IDS.index(int_itemId)
                saplingName    = SEED_NAMES[sapling_index]
                quickSell      = min(buyPrice,sellPrice)
                slowSell       = max(buyPrice,sellPrice)
                treeDict[saplingName]['outputQuick']     = quickSell
                treeDict[saplingName]['outputSlow']      = slowSell
                treeDict[saplingName]['outputWeeklyMin'] = percentOfWeeklyMin
                treeDict[saplingName]['outputWeeklyMax'] = percentOfWeeklyMax
            
            #DHides
            if int_itemId in HIDE_IDS:
                hide_index  = HIDE_IDS.index(int_itemId)
                hideName    = HIDE_NAMES[hide_index]
                quickBuy    = max(buyPrice,sellPrice)
                slowBuy     = min(buyPrice,sellPrice)
                hideDict[hideName]['inputQuick']      = quickBuy
                hideDict[hideName]['inputSlow']       = slowBuy
                hideDict[hideName]['inputWeeklyMin']  = percentOfWeeklyMin
                hideDict[hideName]['inputWeeklyMax']  = percentOfWeeklyMax
                
            if int_itemId in LEATHER_IDS:
                leather_index  = LEATHER_IDS.index(int_itemId)
                leatherName    = HIDE_NAMES[leather_index]
                quickSell      = min(buyPrice,sellPrice)
                slowSell       = max(buyPrice,sellPrice)
                hideDict[leatherName]['outputQuick']      = quickSell
                hideDict[leatherName]['outputSlow']       = slowSell
                hideDict[leatherName]['outputWeeklyMin']  = percentOfWeeklyMin
                hideDict[leatherName]['outputWeeklyMax']  = percentOfWeeklyMax
                
            
            #Dragonstone Jewlery
            if int_itemId in UNCHARGED_IDS:
                uncharged_index  = UNCHARGED_IDS.index(int_itemId)
                unchargedName    = JEWLERY_NAMES[uncharged_index]
                quickBuy         = max(buyPrice,sellPrice)
                slowBuy          = min(buyPrice,sellPrice)
                jewleryDict[unchargedName]['inputQuick']      = quickBuy
                jewleryDict[unchargedName]['inputSlow']       = slowBuy
                jewleryDict[unchargedName]['inputWeeklyMin']  = percentOfWeeklyMin
                jewleryDict[unchargedName]['inputWeeklyMax']  = percentOfWeeklyMax
                
            if int_itemId in CHARGED_IDS:
                charged_index  = CHARGED_IDS.index(int_itemId)
                chargedName    = JEWLERY_NAMES[charged_index]
                quickSell      = min(buyPrice,sellPrice)
                slowSell       = max(buyPrice,sellPrice)
                jewleryDict[chargedName]['outputQuick']      = quickBuy
                jewleryDict[chargedName]['outputSlow']       = slowBuy
                jewleryDict[chargedName]['outputWeeklyMin']  = percentOfWeeklyMin
                jewleryDict[chargedName]['outputWeeklyMax']  = percentOfWeeklyMax
                
            #Writes the current line to a new file:
            newData.write(json.dumps(pastData[line_num]))
            newData.write('\n')
            
            #Adds to the list of item properties
            item_properties.append([name,margin,ROI,sellPrice,buyPrice,sellQuantity,buyQuantity,buylimit,profitPerHr,percentOfWeeklyMin,percentOfMonthlyMin,percentOfWeeklyMax,percentOfMonthlyMax,weeklyVolatility,monthlyVolatility,trend])
    
    #Sorts the item properties by ROI
    item_properties.sort(key=lambda pair: pair[2])
    item_properties = list(reversed(copy.deepcopy(item_properties)))
    return item_properties
    
    
def file_len():
    with open('pastData.dat','r+') as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def getNumberOfLinesToTake():
    with open('pastData.dat','r+') as f:
        firstLine = json.loads(f.readline())
    probeSize = deep.deep_getsizeof(firstLine,set())
    linesToTake = int(float(700000000)/float(probeSize))
    return linesToTake

def getIdList():
    """
    """
    idList = []
    with open('pastData.dat', 'r+') as f:
        for i,line in enumerate(f):
            readable_line = json.loads(line)
            for key,value in readable_line.iteritems():
                idList.append(key)
    return idList
    
def getPastDataChunk(start,numberOfLinesToTake,verbose=False):
    gc.collect()
    pastData = []
    with open('pastData.dat', 'r+') as f:
        """
        if numberOfLinesToTake == 0:
            for i0,line in enumerate(f):
                if i0 >= start:
                    pastData.append(json.loads(line))
                #dataSize = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                if dataSize > :
                    if verbose == True:
                        print('\n\n\n')
                        print('(-----------------------------------------------------)')
                        print('Data size: ' + str(dataSize))
                        print('Number of lines in selection: ' + str(i0 - start))
                        print('(-----------------------------------------------------)')
                        print('\n\n\n')
                    break
        else:
        """
        for i0,line in enumerate(f):
            if i0 >= start:
                pastData.append(json.loads(line))
            if (i0 - start) > numberOfLinesToTake:
                break
    last = i0
    return pastData,last,start

def getOSBuddyData():
    """Gets OSBuddyAPI json data, converts it to a dictionary, then converts that to a list of dictionaries.
    """
    items_list = []
    json_items = 0
    while json_items == 0:
        try:
            json_items = http.request('GET',DATABASE)
        except:
            print('Could not connect to OSBuddy-Exchange API')
            json_items = 0
            time.sleep(MINS*60)
    items_dict = json.loads(json_items.data)
    for key,value in items_dict.iteritems():
        items_list.append([int(key),value])
    items_list.sort(key=lambda pair: pair[0])
    return items_list

        
def dataExtractionAndRefinement(MaxNumberOfPriceEntries,item_id,pastData,line_num):
    """Extracts all meaningful data in one fell swoop
    """
    hourPrices = []
    weekPrices = []
    monthPrices = []
    if len(pastData[line_num][item_id]['buyingHistory']) > MaxNumberOfPriceEntries:
            for historyType in ['buyingHistory','sellingHistory']:
                del_keys = []
                for unix_time,price in pastData[line_num][item_id][historyType].iteritems():
                    if int(unix_time) < MONTH_AGO:
                        del_keys.append(unix_time)
                for i in del_keys:
                    del pastData[line_num][item_id][historyType][i]
    else:
        for unix_time,price in pastData[line_num][item_id]['buyingHistory'].iteritems():
            if int(unix_time) > TWO_HOUR_AGO:
                hourPrices.append([price,unix_time])
                weekPrices.append(price)
                monthPrices.append(price)
            elif int(unix_time) > WEEK_AGO:
                weekPrices.append(price)
                monthPrices.append(price)
            else:
                monthPrices.append(price)
    return hourPrices,weekPrices,monthPrices
     
def getTimelineData(weekPrices,monthPrices):
    """Does some numpy operations on the extracted timeline data"""
    if len(weekPrices) != 0:
        weeklyMax  = np.amax(weekPrices)
        weeklyMin  = np.amin(weekPrices)
        weeklyVol  = np.std(weekPrices)
    else:
        weeklyMax  = 0
        weeklyMin  = 0
        weeklyVol  = 0
    if len(monthPrices) != 0:
        monthlyMax = np.amax(monthPrices)
        monthlyMin = np.amin(monthPrices)
        monthlyVol = np.std(monthPrices)
    else:
        monthlyMax = 0
        monthlyMin = 0
        monthlyVol = 0
    weeklyData  = timelineData(weeklyMax,weeklyMin,weeklyVol)
    monthlyData = timelineData(monthlyMax,monthlyMin,monthlyVol)
    return weeklyData,monthlyData


def uploadData():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
    # Create GoogleDrive instance with authenticated GoogleAuth instance.
    drive = GoogleDrive(gauth)
    dataFileNames = os.listdir(OUTPUTS)
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    for file0 in file_list:
        if file0['title'] in dataFileNames:
            file0.Delete()
    for i in dataFileNames: #uses this old output folder as a list of names to upload
        file1 = drive.CreateFile()
        file1.SetContentFile(i)
        file1.Upload() # Upload the file.

def uploadErrorMessage(errorText,streak):
    MONTH = (time.localtime()[1] - 1)
    DAY_OF_MONTH = time.localtime()[2]
    with open('Error.txt', 'w+') as f:
        currentTime = writing.findTime()
        f.write('Date of Error: ' + str(Months[MONTH]) + ' ' + str(DAY_OF_MONTH))
        f.write('\n')
        f.write('Time of Error: ' + str(currentTime))
        f.write('\n')
        f.write('Error: ' + str(errorText))
        f.write('\n')
        f.write('Streak: ' + str(streak))
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
    # Create GoogleDrive instance with authenticated GoogleAuth instance.
    drive = GoogleDrive(gauth)
    badFile = drive.CreateFile()
    badFile.SetContentFile('Error.txt')
    badFile.Upload()

def uploadAPIerrorMessage():
    MONTH = (time.localtime()[1] - 1)
    DAY_OF_MONTH = time.localtime()[2]
    with open('APIError.txt', 'w+') as f:
        currentTime = writing.findTime()
        f.write('Date of Error: ' + str(Months[MONTH]) + ' ' + str(DAY_OF_MONTH))
        f.write('\n')
        f.write('Time of Error: ' + str(currentTime))
        f.write('\n')
        f.write('API is currently not reporting null information')
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
    # Create GoogleDrive instance with authenticated GoogleAuth instance.
    drive = GoogleDrive(gauth)
    badFile = drive.CreateFile()
    badFile.SetContentFile('APIError.txt')
    badFile.Upload()
    
def badInfoTest(items_list):
    newitems = []
    for i in items_list:
        if i[5] > 5000:
            newitems.append(i)
    N = len(newitems)
    if N > 1:
        return True
    else:
        uploadAPIerrorMessage()
        time.sleep(20*60)
        return False


#-----------------------------------------
while True:
    try:
        TIME = int(time.time())
        MONTH_AGO = TIME - 2628000
        WEEK_AGO  = TIME - 604800
        TWO_HOUR_AGO  = TIME - (3600)
        DAY_OF_MONTH = time.localtime()[2]
        MONTH = time.localtime()[1]
        
        start = int(time.time())

        items_list = getData()

        end = int(time.time())

        timeTaken = end-start
        print('Time to Get Item Data: '  + str(timeTaken) + ' s')

        if badInfoTest(items_list):
            writing.bestROI(items_list)
            writing.highVolume(items_list)
            writing.highValue(items_list)
            writing.veryHighValue(items_list)
            writing.medVolume_medValue(items_list)
            writing.bestProfit(items_list)
            writing.bestTrend(items_list)
            writing.bestTrendAndHighPrice(items_list)
            writing.bestTrendAndMedVol(items_list)
            writing.treeSeeds(treeDict,'TreeProfit')
            writing.treeSeeds(hideDict,'HideProfit')
            writing.treeSeeds(jewleryDict,'JewleryProfit')

            uploadStart = int(time.time())
            uploadData()
            uploadEnd = int(time.time())
            uploadTime = uploadEnd-uploadStart
            timeTaken+=uploadTime
            print('Time to Upload Item Data: '  + str(uploadTime) + ' s')
            errorStreak = 0
            os.remove('pastData.dat')
            os.rename('newPastData.dat','pastData.dat')
            if timeTaken < 600:
                time.sleep((11*60)-timeTaken)
            else:
                time.sleep(60)
    except:
        errorStreak += 1
        e = sys.exc_info()[0]
        #If Error Messge upload is failing, additional wait time is added (Bad internet or google API problems)
        try:
            uploadErrorMessage(e,errorStreak)
        except:
            print('Could not connect to google Drive API, check internet connection (Will wait 15 minutes and try again)')
            time.sleep(15*60)
            try:
                uploadErrorMessage(e,errorStreak)
            except:
                print('Could not connect to google Drive API, check internet connection (Will wait an hour before resuming script)')
                time.sleep(3600)
        if errorStreak == 1:
            time.sleep(MINS*60)
        elif errorStreak == 2:
            time.sleep(3600)
        elif errorStreak == 3:
            time.sleep(3600*12)
        else:
            break
print('Failure at UNIX time: '  + str(time.time()))
'''
#Testing
while True:
    TIME = int(time.time())
    MONTH_AGO = TIME - 2628000
    WEEK_AGO  = TIME - 604800
    TWO_HOUR_AGO  = TIME - (3600)
    DAY_OF_MONTH = time.localtime()[2]
    MONTH = time.localtime()[1]
    start = int(time.time())

    print('I started')
    items_list = getData(verbose=True)
    print(len(items_list))

    end = int(time.time())

    timeTaken = end-start
    print('Time to Get Item Data: '  + str(timeTaken) + ' s')

    if badInfoTest(items_list):
        writing.bestROI(items_list)
        print('ROI good')
        writing.highVolume(items_list)
        print('High Volume good')
        writing.highValue(items_list)
        print('High Value good')
        writing.veryHighValue(items_list)
        print('Very High Value good')
        writing.medVolume_medValue(items_list)
        print('medVolume good')
        writing.bestProfit(items_list)
        print('best Profit good')
        writing.bestTrend(items_list)
        print('best Trend good')
        writing.bestTrendAndHighPrice(items_list)
        print('best trend high good')
        writing.bestTrendAndMedVol(items_list)
        print ('best trend med good')
        writing.treeSeeds(treeDict,'TreeProfit')
        print('tree seeds good')
        writing.treeSeeds(hideDict,'HideProfit')
        print('hide good')
        writing.treeSeeds(jewleryDict,'JewleryProfit')
        print('jewlery good')

        uploadStart = int(time.time())
        uploadData()
        uploadEnd = int(time.time())
        uploadTime = uploadEnd-uploadStart
        timeTaken+=uploadTime
        print('Time to Upload Item Data: '  + str(uploadTime) + ' s')
        errorStreak = 0

    os.remove('pastData.dat')
    os.rename('newPastData.dat','pastData.dat')

    if timeTaken < 600:
        time.sleep((11*60)-timeTaken)
    else:
        time.sleep(60)
'''
