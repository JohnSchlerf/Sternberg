#!/usr/bin/python
from helperfunctions import *
from random import shuffle, choice
from Tkinter import *
import copy

WIDTH = -1
HEIGHT = -1
FONTSIZE = 36

yesKey = 'f'
noKey = 'j'

encode_color = "green"
probe_color = "white"

encode_time = 2
probe_timeout = 2

set_size = [4,6]

number_of_sets = 20
probes_per_set = 6

min_delay = 0.6
max_delay = 1.4

set_items = ['B','C','D','F','G','H','J','K','L','M','N','P','Q','R','S','T','V','W','X','Z']
# Having vowels makes this a bit easier, because you can make words:
#set_items = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

def chooseSet(size):
   shuffle(set_items)
   theSet = []
   distractorSet = []
   for item in range(size):
      theSet.append(set_items[item])
      distractorSet.append(set_items[item+size])
   return theSet,distractorSet

def setString(set):
   myString = " "
   for item in set:
      myString+=item
      myString+=" "
   return myString

def GridLabel(Parent,Text,Row,Column):
    """
    This is a helper function which adds a label to a grid.
    This is normally a couple of lines, so multiple labels
    gets a little cumbersome...
    """
    L = Label(Parent,text=Text)
    L.grid(row=Row,column=Column)
    return L

def GridEntry(Parent,DefaultText,Row,Column):
    """
    This is a helper function which adds an Entry widget
    to a grid.  Also sets default text.
    """
    E = Entry(Parent)
    E.insert(0,DefaultText)
    E.grid(row=Row,column=Column)
    return E

class sternbergGUI():

   def __init__(self):
      self.AllData = DataDict()

      self.win = Tk()
      self.win.update()
      nextRow = 0

      self.BlockNumber = 1

      GridLabel(self.win,"Current Block:",nextRow,0)
      GridLabel(self.win,str(self.BlockNumber),0,1)

      nextRow+=1
      GridLabel(self.win,"Yes Key",nextRow,0)
      self.__yesKeyEntry = GridEntry(self.win,yesKey,nextRow,1)
      
      nextRow+=1
      GridLabel(self.win,"No Key",nextRow,0)
      self.__noKeyEntry = GridEntry(self.win,noKey,nextRow,1)
      
      nextRow+=1
      GridLabel(self.win,"",nextRow,0)
      
      nextRow+=1
      GridLabel(self.win,"Set Lengths",nextRow,0)
      self.__setSizeEntry = GridEntry(self.win,str(set_size),nextRow,1)
      
      nextRow+=1
      GridLabel(self.win,"",nextRow,0)
      
      nextRow+=1
      GridLabel(self.win,"Number of Sets",nextRow,0)
      self.__numSetsEntry = GridEntry(self.win,str(number_of_sets),nextRow,1)
      
      nextRow+=1
      GridLabel(self.win,"Probes per Set",nextRow,0)
      self.__numProbesEntry = GridEntry(self.win,str(probes_per_set),nextRow,1)

      nextRow+=1
      GridLabel(self.win,"Encoding time (sec)",nextRow,0)
      self.__encodeTimeEntry = GridEntry(self.win,str(encode_time),nextRow,1)

      nextRow+=1
      GridLabel(self.win,"",nextRow,0)
      
      nextRow+=1
      GridLabel(self.win,"Encoding Color",nextRow,0)
      self.__encodeColorEntry = GridEntry(self.win,encode_color,nextRow,1)
      
      nextRow+=1
      GridLabel(self.win,"Probes Color",nextRow,0)
      self.__probeColorEntry = GridEntry(self.win,probe_color,nextRow,1)

      nextRow+=1
      GridLabel(self.win,"",nextRow,0)
      
      nextRow+=1
      GridLabel(self.win,"Filename",nextRow,0)
      self.__fileNameEntry = GridEntry(self.win,"Subject",nextRow,1)

      nextRow+=1
      self.__runButton = Button(self.win,text="Run Block",
                                command=self.runBlock)
      self.__runButton.grid(row=nextRow,column=1,pady=5,sticky=E+W)
      
      self.__quitButton = Button(self.win,text="Quit",command=self.CleanUp)
      self.__quitButton.grid(row=nextRow,column=0,pady=5,sticky=E+W)
      
      self.win.mainloop()

   def CleanUp(self):
      self.AllData.writeToFile(self.fileName)
      self.win.quit()

   def runBlock(self):
      
      optDic = {}
      optDic['number_of_sets'] = eval(self.__numSetsEntry.get())
      optDic['probes_per_set'] = eval(self.__numProbesEntry.get())

      optDic['set_size'] = eval(self.__setSizeEntry.get())

      optDic['encode_color'] = self.__encodeColorEntry.get()
      optDic['probe_color'] = self.__probeColorEntry.get()

      optDic['yesKey'] = self.__yesKeyEntry.get()
      optDic['noKey'] = self.__noKeyEntry.get()

      optDic['encode_time'] = self.__encodeTimeEntry.get()
      
      if self.BlockNumber == 1:
         self.fileName = SafeFile(self.__fileNameEntry.get(),'.ana')
         
      self.AllData = runSternbergBlock(self.BlockNumber,optDic,self.AllData)
      
      self.__fileNameEntry.delete(0,END)
      self.__fileNameEntry.insert(0,self.fileName)
      self.BlockNumber+=1
      GridLabel(self.win,str(self.BlockNumber),0,1)

def runSternbergBlock(BN,optionDict=None,TrialDict=None):
   if optionDict:
      for key in optionDict.keys():
         exec(key + "=optionDict['" + key + "']")

   myWindow = Display(width=WIDTH,height=HEIGHT)
   myWindow.SetSize(FONTSIZE)

   # Put up brief instructions?
   myWindow.SetText("You will see a list of " + encode_color + " letters, which\n" + \
                    "you must remember. You will then be shown " + probe_color + \
                    "\nletters, which you must compare to the remembered list.\n" + \
                    "If the letter was in the list, press <" + yesKey + ">, otherwise\n" + \
                    "press <" + noKey + ">. Respond as quickly and accurately as\n" + \
                    "possible.\n\nPress any key to begin.")
   
   myWindow.clearKey()
   responseCollected = False
   while not(responseCollected):
      if myWindow[0]:
         myWindow.update()
         if myWindow.keyPress:
            responseCollected = True
      else:
         responseCollected = True
   myWindow.SetText("")
   myWindow.update()
   myClocks=Clock(5)
   TN = 0
   if not(TrialDict):
      TrialDict = DataDict()

   while myClocks[3] < 1:
      myClocks.update()
   myClocks.resetAll()
   # Create my list of sets:
   setList = []
   while len(setList)<number_of_sets:
      for size in set_size:
         setList.append(size)
   shuffle(setList)
   
   emptyOrFullList = []
   while len(emptyOrFullList)<(number_of_sets*probes_per_set):
      emptyOrFullList += ['Empty','Full']
   shuffle(emptyOrFullList)

   for set in range(number_of_sets):
      size = setList.pop()
      Targets,Distractors = chooseSet(size)
      myWindow.SetColor(encode_color)
      myWindow.SetText(setString(Targets))
      myWindow.update()
      myClocks.reset(4)
      if myWindow[0]:
         while myClocks[4] < float(encode_time):
            myClocks.update()
      myWindow.SetText("")
      myWindow.update()
      myWindow.SetColor(probe_color)

      # These help avoid repeats:
      thisProbe,lastProbe = None,None
      
      for probe in range(probes_per_set):
         TN += 1
         EorF = emptyOrFullList.pop()
         pause = float(choice(range(int(min_delay*10),int(max_delay*10))))/10.0
         myClocks.reset(4)
         if myWindow[0]:
            while myClocks[4] < pause:
               myClocks.update()
         
         while thisProbe == lastProbe:
            if EorF=='Full':
               thisProbe = choice(Targets)
            else:
               thisProbe = choice(Distractors)
            if size==1: lastProbe = None # Avoids an infinite loop

         lastProbe = thisProbe

         myWindow.SetText(thisProbe)
         myWindow.clearKey()
         myWindow.update()
         myClocks.reset(1)
         myWindow.clearKey()
         responseCollected = False
         while not(responseCollected):
            if myWindow[0]:
               myClocks.update()
               myWindow.update()
               if myWindow.keyPress:
                  if myWindow.keyPress in [yesKey,noKey]:
                     responseCollected = True
                     response = myWindow.keyPress
                     RT = myClocks[1]
                  elif myClocks[1] > float(probe_timeout):
                     responseCollected = True
                     response = None
                     RT = -1
            else:
               responseCollected = True
               response = None
               RT = -1
         TrialDict.update(BN,TN,set+1,response,RT,size,thisProbe,Targets,myClocks[0],yesKey,noKey)
         myWindow.SetText("")
         myWindow.clearKey()
         myWindow.update()

   myWindow.Close()
   return TrialDict

if __name__ == '__main__':
   sternbergGUI()
