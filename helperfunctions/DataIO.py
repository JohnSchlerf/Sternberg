from SummaryStats import *
import copy

# Can make this a comma if that would be easier
DELIMITER = '\t'

def SafeFile(fileName,fileType):
    # Assures that datafiles are unique.
    if not(fileType[0]=='.'):
        fileType = '.'+fileType
    if fileType in fileName:
        fileName = fileName.strip(fileType)
    theFile = fileName + fileType
    tries = 0
    safeFile = False
    while not safeFile:
        try: 
            junk = open(theFile,'r')
            junk.close()
            tries += 1
            theFile = fileName + str(tries) + fileType
        except:
            safeFile = True
    return theFile

class DataDict():
    keyOrder = ['BlockNumber','TrialNumber','SetNumber',\
                    'Correct','ReactionTime','SetSize',\
                    'Probe','Response','ResponseKey',\
                    'ProbeIsTarget','RealTime','TargetSet']

    def __init__(self,keyOrder=None):
        if keyOrder: self.keyOrder = keyOrder
        self.Data = {}
        for key in self.keyOrder:
            self.Data[key] = []
      
    def update(self,BN,TN,SetNum,Resp,RT,SetSize,Probe,TargetSet,Time,yesKey,noKey):
        self.Data['BlockNumber'].append(BN)
        self.Data['TrialNumber'].append(TN)
        self.Data['SetNumber'].append(SetNum)
        self.Data['ResponseKey'].append(Resp)
        if Resp==yesKey: self.Data['Response'].append(1)
        elif Resp==noKey: self.Data['Response'].append(0)
        else: self.Data['Response'].append(None)
        self.Data['ReactionTime'].append(int(RT*1000))
        self.Data['SetSize'].append(SetSize)
        self.Data['Probe'].append(Probe)
        self.Data['RealTime'].append(Time)
        if Probe in TargetSet: ProbeIsTarget = 1
        else: ProbeIsTarget = 0
        self.Data['ProbeIsTarget'].append(ProbeIsTarget)
        TS = ''
        for target in TargetSet: TS += target
        self.Data['TargetSet'].append(TS)
        if (Resp==yesKey) == (Probe in TargetSet): Correct = 1
        else: Correct = 0
        self.Data['Correct'].append(Correct)
        self.anaFile = None
        self.summaryFile = None

    def getFile(self,fileName='Default'):
        if not('.ana' in fileName): fileName += '.ana'
        summName = fileName.replace('.ana','.sum')
        self.anaFile = open(fileName,'a')
        self.summaryFile = open(summName,'a')

    def writeSummaryFile(self,FileObject=None):
        if FileObject: 
            if type(FileObject) == str:
                self.getFile(FileObject)
            else:
                self.summaryFile = FileObject

        allBlocks = list(set(self.Data['BlockNumber']))
        allBlocks.sort()

        allSizes = list(set(self.Data['SetSize']))
        allSizes.sort()
        
        summaryKeyOrder = ['BlockNumber','SetSize','NumTrials','NumCorrect','MeanReactionTime','stdReactionTime', \
                               'MeanReactionTime_CorrectTrials','stdReactionTime_CorrectTrials', \
                               'dPrime','HitRate','FalseAlarmRate']

        SummaryDict = {}
        for key in summaryKeyOrder:
            SummaryDict[key] = []

        numGoodTrials = 0
        for trial in range(len(self.Data[self.keyOrder[0]])):
            if self.Data['ReactionTime'][trial] > 0:
                numGoodTrials += 1
        
        which = 0
        for block in allBlocks:

            for size in allSizes:
                RT_0,RT_1,RT_2 = 0.0,0.0,0.0
                RTC_0,RTC_1,RTC_2 = 0.0,0.0,0.0
                Responses,Signal = [],[]
                for row in range(len(self.Data[self.keyOrder[0]])):
                    if self.Data['BlockNumber'][row] == block and \
                            self.Data['SetSize'][row] == size and \
                            self.Data['ReactionTime'][row] > 0:
                        RT_0 += 1.0
                        RT_1 += float(self.Data['ReactionTime'][row])
                        RT_2 += float(self.Data['ReactionTime'][row])**2
                        Responses.append(self.Data['Response'][row])
                        Signal.append(self.Data['ProbeIsTarget'][row])
                        if self.Data['Correct'][row] == 1:
                            RTC_0 += 1.0
                            RTC_1 += float(self.Data['ReactionTime'][row])
                            RTC_2 += float(self.Data['ReactionTime'][row])**2

                SummaryDict['BlockNumber'].append(block)
                SummaryDict['SetSize'].append(size)
                SummaryDict['NumTrials'].append(RT_0)
                SummaryDict['NumCorrect'].append(RTC_0)
                SummaryDict['MeanReactionTime'].append(computeMean(RT_0,RT_1))
                SummaryDict['stdReactionTime'].append(computeSTD(RT_0,RT_1,RT_2))
                SummaryDict['MeanReactionTime_CorrectTrials'].append(computeMean(RTC_0,RTC_1))
                SummaryDict['stdReactionTime_CorrectTrials'].append(computeSTD(RTC_0,RTC_1,RTC_2))

                dp,HitRate,FARate = dprime(Responses,Signal)

                SummaryDict['dPrime'].append(dp)
                SummaryDict['HitRate'].append(HitRate)
                SummaryDict['FalseAlarmRate'].append(FARate)

        #self.writeHeader(self.summaryFile,summaryKeyOrder)
        self.writeFile(self.summaryFile,summaryKeyOrder,SummaryDict)

    def writeFile(self,FileObject='USE_DEFAULT',thisKeyOrder='USE_DEFAULT',dataDict='USE_DEFAULT'):
        if type(FileObject) == str:
            if not(FileObject=='USE_DEFAULT'):
                self.getFile(FileObject)
            FileObject = self.anaFile

        # Write a quick header:
        if thisKeyOrder=='USE_DEFAULT':
            thisKeyOrder = self.keyOrder
        if dataDict=='USE_DEFAULT':
            dataDict = self.Data

        for key in thisKeyOrder:
            FileObject.write(key+DELIMITER)
        FileObject.write('\n')

        for row in range(len(dataDict[thisKeyOrder[0]])):
            for key in thisKeyOrder:
                FileObject.write(str(dataDict[key][row])+DELIMITER)
            FileObject.write('\n')

    def writeAnaFile(self):
        #self.writeHeader()
        self.writeFile()

    def writeToFile(self,FileObject=None):
        if FileObject: 
            if type(FileObject) == str:
                self.getFile(FileObject)
            else:
                self.fileObject = FileObject
        
        self.writeAnaFile()
        self.writeSummaryFile()
