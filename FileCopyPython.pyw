#Version 1.0.1

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import re
import shutil
import threading

# Tutorial for this tkinter: https://tkdocs.com/tutorial/

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class FileCopyUI:
    
    def __init__(self, root):
        self.directoryPath = "" #the parent directory string supplied from the OS directory selection window.
        self.subfolder = "" #the subfolder path
        self.fileListText = "" #a user-input string containing linebreak separated file numbers
        self.fileList = [] #a list of individual file names, as retrieved by the OS.
        self.replaceDuplicatePhotos = BooleanVar(value=False) #option to overwrite files already in the destination folder instead of skipping; defaults to false.
        self.copyOrMove = StringVar(value='copy') #option to choose whether files are copied or moved.
        self.moveProgressCount = StringVar(value="") #to show progress as 'Moving x of y files.'
        self.moveProgressPercent = StringVar(value="") #to show progress as 'x%'
        self.progressBarValue = DoubleVar(value=0) #float to control progress bar; 100.0 is full.
        
        root.minsize(600,300)
        root.title("File Copy v2.0") #TODO: Put an easter egg "I Love You Dad" here.
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        self.mainframe = ttk.Frame(root, padding="3")
        self.mainframe.grid(column=0, row=0, sticky=(N,S,E,W))
        self.mainframe.columnconfigure(1,weight=1)
        self.mainframe.columnconfigure(2,weight=1)
        self.mainframe.rowconfigure(1,weight=0,minsize=120)
        self.mainframe.rowconfigure(2,weight=1)
        
        
        self.optionsFrame = self.createOptionsFrame(self.mainframe)
        self.optionsFrame.grid(column=1,row=1,sticky=(N,W,S,E))
        self.textboxFrame = self.createTextboxFrame(self.mainframe)
        self.textboxFrame.grid(column=1,row=2,columnspan=2,sticky=(N,W,S,E))
        self.moveButtonFrame = self.createMoveButtonFrame(self.mainframe)
        self.moveButtonFrame.grid(column=2,row=1,sticky=(N,E))
        
    def createOptionsFrame(self, parent):
        # Create the frame
        oFrame = Frame(parent, width=300, height=100)
        #oFrame['bg'] = 'red' 
        
        #Create the Directory Select Button & bind it to directory select logic
        directoryButton = ttk.Button(oFrame, text="Select\nFolder", command=self.selectDirectory)
        directoryButton.grid(column=1,row=1,sticky=(N,W))
        
        #Create the Directory Label, set to update with directory path
        self.directoryLabelVar = StringVar(value="Selected Folder:\n"+self.directoryPath)
        self.directoryLabel = ttk.Label(oFrame, textvariable=self.directoryLabelVar)
        self.directoryLabel.grid(column=2,row=1,sticky=(N,E,W))

        
        #Create the "Replace Duplicate Photos" checkbox, bind to logic that changes operating mode
        self.rdpCheckbox = ttk.Checkbutton(oFrame, text = "Replace Duplicate Photos", variable=self.replaceDuplicatePhotos, onvalue=True, offvalue=False, command=lambda: print(self.replaceDuplicatePhotos.get()))
        self.rdpCheckbox.grid(column=1,row=2,columnspan=2,sticky=(W))
        
        #Create the Copy and Move Radiobuttons, bind to logic that changes operating mode
        self.copyRadio = ttk.Radiobutton(oFrame, text="Copy Photos", variable=self.copyOrMove,value='copy',command=lambda: print(self.copyOrMove.get()))
        self.copyRadio.grid(column=1,row=3,columnspan=2,sticky=(W))
        self.moveRadio = ttk.Radiobutton(oFrame, text="Move Photos", variable=self.copyOrMove,value='move',command=lambda: print(self.copyOrMove.get()))
        self.moveRadio.grid(column=1,row=4,columnspan=2,sticky=(W))
        
        return oFrame
        
    def createTextboxFrame(self, parent):
        tbFrame = Frame(parent)
        #tbFrame['bg'] = 'green'
        tbFrame.columnconfigure(1,weight=1)
        tbFrame.rowconfigure(1,weight=1)
        # Create the Labelframe labeled as "Photo Numbers (Separated by Line)"
        labelFrame = ttk.Labelframe(tbFrame,text="Photo Numbers (Separated by Line)")
        labelFrame.grid(column=1,row=1,sticky=(N,S,E,W))
        labelFrame.columnconfigure(1,weight=1)
        labelFrame.rowconfigure(1,weight=1,minsize=100)
        
        
        
        #Inside Labelframe, create text widget. Also create a specific StringVar for files.
        self.textBox = Text(labelFrame,height=10)
        self.textBox.grid(column=1,row=1,sticky=(N,S,E,W))
        self.menu = Menu(self.textBox,tearoff=False)
        
        def cut():
            if self.textBox.selection_get():
                self.textBox.clipboard_clear()
                self.textBox.clipboard_append(self.textBox.selection_get())
                #print(self.textBox.clipboard_get())
                self.textBox.delete("sel.first","sel.last")
            
            
        def copy():
            if self.textBox.selection_get():
                self.textBox.clipboard_clear()
                self.textBox.clipboard_append(self.textBox.selection_get())
                #print(self.textBox.clipboard_get())
            
        def paste():
            position = self.textBox.index(INSERT)
            self.textBox.insert(position, self.textBox.clipboard_get())
            #print("paste")
        
        self.menu.add_command(label="Copy",command=copy)
        self.menu.add_command(label="Cut",command=cut)
        self.menu.add_separator()
        self.menu.add_command(label="Paste",command=paste)
        self.textBox.bind("<Button-3>",lambda event: self.menu.post(event.x_root, event.y_root))
        
        #TODO Inside Labelframe, create scrollbar & bind scrollbar to text widget
        scrollbar = ttk.Scrollbar(labelFrame, orient=VERTICAL,command=self.textBox.yview)
        self.textBox['yscrollcommand'] = scrollbar.set
        scrollbar.grid(column=2,row=1,sticky=(N,S,W))
        
        return tbFrame
        
    def createMoveButtonFrame(self, parent):
        mbFrame = Frame(parent,width=300, height=100)
        #mbFrame['bg'] = 'blue'
        
        #Create button to move files (compound, with arrow image + text).
        
        self.buttonImage = Image.open(resource_path('image/Arrow.png'))
        self.buttonPhoto = ImageTk.PhotoImage(self.buttonImage)
        
        self.runButton = ttk.Button(mbFrame, text="Run", command=self.runFilecopy, compound="top", image=self.buttonPhoto)
        self.runButton.grid(column=2,row=1,columnspan=2,sticky=(S))
        self.runButton.state(['disabled'])
        #Create label that dynamically shows the number of files to move.
        moveLabel = ttk.Label(mbFrame, textvariable=self.moveProgressCount)
        moveLabel.grid(column=1,row=2,columnspan=3,sticky=(E,W,S))
        
        
        #Create progress bar and label that shows the progress. Label should be bound to a virtual event produced by the daemon threads in order to update and should call updateProgressBar().
        progressBar = ttk.Progressbar(mbFrame,orient=HORIZONTAL,length=200,mode='determinate',variable=self.progressBarValue)
        progressBar.grid(column=1,row=3,columnspan=2,sticky=(N,W,E))
        
        pbLabel = ttk.Label(mbFrame,textvariable=self.moveProgressPercent)
        pbLabel.grid(column=3,row=3,sticky=(N,W))
        
        return mbFrame
    
        
    def selectDirectory(self):
        #logic for getting the directory path.
        print("selectDirectory called.")
        
        self.directoryPath = filedialog.askdirectory()
        print(self.directoryPath)
        self.directoryLabelVar.set("Selected Folder:\n" + self.directoryPath)
        self.runButton.state(['!disabled']) #enables the run button
        return self.directoryPath 
        
    def runFilecopy(self):
        #TODO: Master method for the background process
        print("beginning file copy method")
        if self.directoryPath == "":
            print("no directory path selected.")
            return
        self.createSubDirectory()
        filenameList = self.locateFilesByRegex(self.parseTextToItemList())
        noDuplicate, duplicate = self.identifyDuplicateFiles(filenameList)
        self.manageFiles(noDuplicate,duplicate)
        
        #print("Textbox contents:\n" + self.textBox.get(1.0,END)[:-1])
        
    def createSubDirectory(self):
        #logic for creating the subdirectory "/Selected Photos" if it doesn't already exist.
        print('checking for /Selected Pictures directory')
        self.subfolder = self.directoryPath + "/Selected Photos"
        if not os.path.exists(self.subfolder):
            print('creating /Selected Pictures directory')
            os.makedirs(self.subfolder)
        else:
            print('/Selected Pictures already exists')
        return
        
    def parseTextToItemList(self):
        #Turn the string in the textbox into an array of strings for the regex queries.
        print("Parsing textbox to list")
        textboxContents = self.textBox.get(1.0,END)[:-1]
        itemList = textboxContents.split("\n")
        if itemList == ['']:
            itemList.pop()
        print("Item List: ", itemList)
        return itemList
        
        
    def locateFilesByRegex(self, itemList):
        #return an array of matching filenames by regex, using the item list array generated by parseTextToItemList()
        print("Finding all Filenames in directory")
        onlyfiles = self.getFilesInDir(self.directoryPath)
        print(onlyfiles)
        
        fileNames = []
        
        print("Selecting files by regex", fileNames)
        for i in itemList:
            #print("looking for",i)
            if i == '' or i == "\n":
                #print("skipping empty line")
                continue
            for f in onlyfiles:
                #print("comparing to",f)
                if re.search(i,f) is not None: #file f contains string i
                    #print("found",i,f)
                    fileNames.append(f)
        
        #print("after regex file names:",fileNames)
        return fileNames
        
    def getFilesInDir(self,path):
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f))]
        
    def identifyDuplicateFiles(self, filenameList):
        #return a tuple of two arrays: an array of filenames without duplicates, and an array with duplicates found in the subdirectory
        subdirFiles = self.getFilesInDir(self.subfolder)
        print("Filename List:",filenameList)
        print("Subdir List:",subdirFiles)
        noDuplicate = []
        duplicate = []
        for f in filenameList:
            if f in subdirFiles:
                duplicate.append(f)
            else:
                noDuplicate.append(f)
        print("No Dupe:",noDuplicate)
        print("Dupe:",duplicate)
        return (noDuplicate, duplicate)
        
    def manageFiles(self, files, duplicateFiles):
        #TODO do the actual moving of files, with multitheading to ensure the the UI doesn't freeze up.
        print("Managing files:",files,duplicateFiles)
        
        if self.replaceDuplicatePhotos.get():
            files += duplicateFiles
            print("Replacing Duplicate Files using list:",files)

        childProcess = threading.Thread(target = self.fileDaemon, args=(files,self.copyOrMove.get() == 'copy',))
        childProcess.start()
        
        return
        
    def fileDaemon(self, files,copyMode):
        #TODO thread process that actually moves the files in the lists. Generates a virtual event that prompts the main thread to update the progress bar and puts the current progress percentage into the pipeIn. mode is "copy" or "move".
        print("Daemon thread",files,copyMode)
        for i in range(len(files)):
            src = os.path.join(self.directoryPath,files[i])
            try:
                if copyMode:
                    shutil.copy2(src,self.subfolder)
                else:
                    shutil.move(src,self.subfolder)
            except:
                print("file already exists.")
            self.updateProgressBar(len(files),i+1)
        return
        
    def updateProgressBar(self, toCopyTotal,hasCopied):
        #Used by daemon to update the progress bar and label.
        percent = (100*hasCopied)/toCopyTotal
        self.progressBarValue.set(percent)
        self.moveProgressPercent.set(str(percent) + "%")
        self.moveProgressCount.set("Moved %s out of %s files."%(hasCopied,toCopyTotal))
        return
        
        '''
        TODO:
            Required UI Elements:
                - Button to select source directory
                
                - Checkbox to "Replace Duplicate Photos," default to unchecked (skip copying if files with same name exist)
                - Mode radiobutton for "Copy Photos" or "Move Photos" (default to copy)
                - Large text box for pasting numbers and/or filenames
                    - Label for text box, including a count for the number of files to move/copy.
                - Button to trigger move/copy to subdirectory "/Selected Pictures" (create subdirectory if needed)
                - (Optional) Help button
                
            Required Logic:
                - Selecting initial directory
                - Creating subdirectory if it doesn't exist
                - Parsing list of numbers/filenames into discreet items (line separated, remove end whitespace)
                    - Updating count of files to move.
                - Regex for filenames in parent directory
                - See if files already exist in child directory
                - Moving files
        '''


root = Tk() #Create the root element of the UI tree
FCUI = FileCopyUI(root) #Initiate the UI tree
root.mainloop() #Start the application window