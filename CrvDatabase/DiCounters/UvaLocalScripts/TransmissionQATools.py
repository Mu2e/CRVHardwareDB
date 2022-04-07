##Plotting and data verification tools for transmission QA data
##Written by Ben Barton
##bb6yx@virginia.edu, 99bbarton@gmail.com
##540-355-8918
##10/25/17 - Initial version completed
##02/08/18 - Added function to re-title histogram
##05/22/18 - Added function to plot overlaid histograms
##05/25/18 - Added functionality to handle transmission tester IDs


######## TODO: Add legend to overlaid plots ############################

##Note: UVA has two tranmission tester units. These two units perform differently with the second unit 
##      reading values roughly 4 times lower than the first. As of 05/22/18, the tester used for each
##      measurement is recorded. For plotting, data is therefore divided into three categories:
##      data measured by tester 1, by tester 2, and older data without a tester ID stamp.


import ROOT

##Root canvas for displaying histograms
canvas = None

##Data lists
aChannels = [] ##Data without tester ID stamp
aChannels_t1 = [] ##A-side data from tester 1
aChannels_t2 = [] ##B-side data from tester 2
bChannels = [] ##etc...
bChannels_t1 = []
bChannels_t2 = []
allChannels = []
allChannels_t1 = []
allChannels_t2 = []

##Root histogram objects
aHist = ROOT.TH1F() ##Data without tester ID stamp
aHist_t1 = ROOT.TH1F() ##Data from tester 1
aHist_t2 = ROOT.TH1F() ##Data from tester 2
bHist = ROOT.TH1F() ##As with A-side ...
bHist_t1 = ROOT.TH1F()
bHist_t2 = ROOT.TH1F()
allHist = ROOT.TH1F()
allHist_t1 = ROOT.TH1F()
allHist_t2 = ROOT.TH1F()

#-----------------------------------------------------------------------------------------------------------

##Function to initialize all A-side data lists and histograms
def setASideObjects(t1_data = [], t2_data = [], noID_data = []):

    global aChannels, aChannels_t1, aChannels_t2, aHist, aHist_t1, aHist_t2

    aChannels = noID_data
    aChannels_t1 = t1_data
    aChannels_t2 = t2_data

    if len(aChannels) > 0:
        aHist = ROOT.TH1F("A-side Channels", "Transmission QA: A-Side Channels - Unspecified Tester",int((max(aChannels)-min(aChannels))/50), min(aChannels)-10, max(aChannels)+10)
        
        aHist.SetXTitle("Current")

        for entry in aChannels:
            aHist.Fill(entry) 

    if len(aChannels_t1) > 0:
        aHist_t1 = ROOT.TH1F("A-side Channels - T1", "Transmission QA: A-Side Channels - Tester 1",int((max(aChannels_t1)-min(aChannels_t1))/50), min(aChannels_t1)-10, max(aChannels_t1)+10)
        
        aHist_t1.SetXTitle("Current")

        for entry in aChannels_t1:
            aHist_t1.Fill(entry) 

    
    if len(aChannels_t2) > 0:
        aHist_t2 = ROOT.TH1F("A-side Channels - T2", "Transmission QA: A-Side Channels - Tester 2",int((max(aChannels_t2)-min(aChannels_t2))/50), min(aChannels_t2)-10, max(aChannels_t2)+10)
        
        aHist_t2.SetXTitle("Current")

        for entry in aChannels_t2:
            aHist_t2.Fill(entry) 

#-----------------------------------------------------------------------------------------------------------


#Function to initialize all B-side data lists and histograms
def setBSideObjects(t1_data = [], t2_data = [], noID_data = []):

    global bChannels, bChannels_t1, bChannels_t2, bHist, bHist_t1, bHist_t2

    bChannels = noID_data
    bChannels_t1 = t1_data
    bChannels_t2 = t2_data

    if len(bChannels) > 0:
        bHist = ROOT.TH1F("B-side Channels", "Transmission QA: B-Side Channels - Unspecified Tester",int((max(bChannels)-min(bChannels))/50), min(bChannels)-10, max(bChannels)+10)
        
        bHist.SetXTitle("Current")

        for entry in aChannels:
            bHist.Fill(entry) 

    if len(bChannels_t1) > 0:
        bHist_t1 = ROOT.TH1F("B-side Channels - T1", "Transmission QA: B-Side Channels - Tester 1",int((max(bChannels_t1)-min(bChannels_t1))/50), min(bChannels_t1)-10, max(bChannels_t1)+10)
        
        bHist_t1.SetXTitle("Current")

        for entry in bChannels_t1:
            bHist_t1.Fill(entry) 

    
    if len(bChannels_t2) > 0:
        bHist_t2 = ROOT.TH1F("B-side Channels - T2", "Transmission QA: B-Side Channels - Tester 2",int((max(bChannels_t2)-min(bChannels_t2))/50), min(bChannels_t2)-10, max(bChannels_t2)+10)
        
        bHist_t2.SetXTitle("Current")

        for entry in bChannels_t2:
            bHist_t2.Fill(entry) 

#-----------------------------------------------------------------------------------------------------------

#Function to initialize all all-channel histograms
def setAllChannelsObjects():

    global aChannels, aChannels_t1, aChannels_t2, bChannels, bChannels_t1, bChannels_t2, allHist, allHist_t1, allHist_t2

    allChannels = aChannels + bChannels
    allChannels_t1 = aChannels_t1 + bChannels_t1
    allChannels_t2 = aChannels_t2 + bChannels_t2

    if len(allChannels) > 0:
        allHist = ROOT.TH1F("All Channels", "Transmission QA: All Channels - Unspecified Tester",int((max(allChannels)-min(allChannels))/50), min(allChannels)-10, max(allChannels)+10)
        
        allHist.SetXTitle("Current")

        for entry in allChannels:
            allHist.Fill(entry) 

    if len(allChannels_t1) > 0:
        allHist_t1 = ROOT.TH1F("All Channels - T1", "Transmission QA: All Channels - Tester 1",int((max(allChannels_t1)-min(allChannels_t1))/50), min(allChannels_t1)-10, max(allChannels_t1)+10)
        
        allHist_t1.SetXTitle("Current")

        for entry in allChannels_t1:
            allHist_t1.Fill(entry) 

    
    if len(allChannels_t2) > 0:
        allHist_t2 = ROOT.TH1F("All Channels - T2", "Transmission QA: All Channels - Tester 2",int((max(allChannels_t2)-min(allChannels_t2))/50), min(allChannels_t2)-10, max(allChannels_t2)+10)
        
        allHist_t2.SetXTitle("Current")

        for entry in allChannels_t2:
            allHist_t2.Fill(entry) 

#-----------------------------------------------------------------------------------------------------------

##Function to initialize a new canvas
def initializeCanvas(name, title):
    
    global canvas
    canvas = ROOT.TCanvas(name,title,1)

#-----------------------------------------------------------------------------------------------------------

##Function to plot a single histogram
def plot(hist, canvPad = 1):
    global canvas

    if hist.GetEntries() > 0:
        canvas.cd(canvPad)
        hist.Draw()
        canvas.Update()

#-----------------------------------------------------------------------------------------------------------

##Function to plot up to three histograms overlaid on the same canvas pad - colors: red - blue - magenta
def plotOverlaid(hist1, hist2, hist3, canvPad = 1):
    global canvas

    canvas.cd(canvPad)

    if hist1.GetEntries() > 0:
        hist1.SetLineColor(2) #Red
        hist1.Draw()
    
    if hist2.GetEntries() > 0:
        hist2.SetLineColor(4) #Blue
        hist2.Draw("same")

    if hist3.GetEntries() > 0:
        hist3.SetLineColor(6) #Magenta
        hist3.Draw("same")

    legend = ROOT.TLegend(0.1,0.7,0.48,0.9)
    legend.SetHeader("Testers","C")
    entry = ROOT.TLegendEntry()
    entry = legend.AddEntry(hist1, "Tester 1", "F")
    entry = legend.AddEntry(hist2, "Tester 2", "F")
    entry = legend.AddEntry(hist3, "Unknown Tester", "F")
    legend.Draw("same")

    canvas.cd(1)
    canvas.BuildLegend()

    canvas.Update()

#-----------------------------------------------------------------------------------------------------------

#Function to plot multiple histograms on the same canvas
def plotAll(hist1, hist2, hist3):
    global canvas

    canvas.Divide(3)

    plot(hist1, 1)
    plot(hist2, 2)
    plot(hist3, 3)

#----------------------------------------------------------------------------------------------------------- 

#Function to plot all histograms on a single canvas
def plotAllOverlaid():
    global canvas, aHist, aHist_t1, aHist_t2, bHist, bHist_t1, bHist_t2, allHist, allHist_t1, allHist_t2

    canvas.Divide(3)

    aHist.SetNameTitle("A-Side Channels", "A-side Channels - All Testers")
    bHist.SetNameTitle("B-Side Channels", "B-side Channels - All Testers")
    allHist.SetNameTitle("All Channels", "All Channels - All Testers")

    plotOverlaid(aHist, aHist_t1, aHist_t2, 1)
    plotOverlaid(bHist, bHist_t1, bHist_t2, 2)
    plotOverlaid(allHist, allHist_t1, allHist_t2, 3)

#-----------------------------------------------------------------------------------------------------------

##Function to rename histograms
def renameHistograms():
    global canvas

    while(True):
        print "Would you like to re-title a histogram?"
        print "Note: Histograms on multi-histogram canvasses will not be re-titled"
        print 'Enter "A", "A1", "A2", "B", "B1", "B2", "All", "All1", "All2", or hit "Enter" to skip'
        choice = raw_input();
    
        if choice == "":
            break
    
        print 'Enter a new title for ' + choice
        title = raw_input();

        if choice.upper() == "A":
            aHist.SetNameTitle("A-side Channels", title)
        elif choice.upper() == "A1":
            aHist_t1.SetNameTitle("A-side Channels - T1", title)
        elif choice.upper() == "A2":
            aHist_t2.SetNameTitle("A-side Channels - T2", title)
        elif choice.upper() == "B":
            bHist.SetNameTitle("B-side Channels", title)
        elif choice.upper() == "B1":
            bHist_t1.SetNameTitle("B-side Channels - T1", title)
        elif choice.upper() == "B2":
            bHist_t2.SetNameTitle("A-side Channels - T2", title)
        elif choice.upper() == "ALL":
            allHist.SetNameTitle("All Channels", title)
        elif choice.upper() == "ALL1":
            allHist_t1.SetNameTitle("All Channels - T1", title)
        elif choice.upper() == "ALL2":
            allHist_t2.SetNameTitle("All Channels - T2", title)
        else:
            print "Unrecognized choice - Using default titles"
        
        canvas.Update()

#-----------------------------------------------------------------------------

##Function to destroy/close Root histogram and canvas objects
def cleanRootObjects():
    global aHist, aHist_t1, aHist_t2, bHist, bHist_t1, bHist_t2, allHist, allHist_t1, allHist_t2, canvas

    del(aHist)
    del(aHist_t1)
    del(aHist_t2)
    del(bHist)
    del(bHist_t1)
    del(bHist_t2)
    del(allHist)
    del(allHist_t1)
    del(allHist_t2)

    canvas.Close()
  
#-----------------------------------------------------------------------------




#-----------------------------------------------------------------------------------------------------------
############################################################################################################
## Code below this point was used with data prior to the inclusion of tester ID
############################################################################################################
#-----------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------

##Function to assign data to aChannels and format and fill aHist
def setASideObjects_old(data = []):
    global aChannels, aHist

    aChannels = data

    if len(aChannels) > 0:
        aHist = ROOT.TH1F("A-side Channels", "Transmission QA: A-Side Channels",int((max(aChannels)-min(aChannels))/50), min(aChannels)-10, max(aChannels)+10)
        
        aHist.SetXTitle("Current")

        for entry in aChannels:
            aHist.Fill(entry)

#-----------------------------------------------------------------------------

##Function to assign data to bChannels and format and fill bHist
def setBSideObjects_old(data = []):
    global bChannels, bHist

    bChannels = data

    if len(aChannels) > 0:
        bHist = ROOT.TH1F("B-side Channels", "Transmission QA: B-Side Channels",int((max(bChannels)-min(bChannels))/50), min(bChannels)-10, max(bChannels)+10)

        bHist.SetXTitle("Current")

        for entry in bChannels:
            bHist.Fill(entry)

#-----------------------------------------------------------------------------

##Function to assign data to allChannels and format allHist    
def setAllChannelsObjects_old():
    global aChannels, bChannels, allChannels, allHist

    allChannels = aChannels + bChannels

    if len(allChannels) > 0:
        allHist = ROOT.TH1F("All Channels", "Transmission QA: All Channels",int((max(allChannels)-min(allChannels))/50), min(allChannels)-10, max(allChannels)+10)

        allHist.SetXTitle("Current")

        for entry in allChannels:
            allHist.Fill(entry)

#-----------------------------------------------------------------------------

##Function to plot all transmisstion QA histograms to a single canvas
def plotAllTransmissionQAData():
    global aHist, bHist, allHist, canvas

    canvas.Divide(3)

    plotTransmissionQAData(allHist, 1)
    plotTransmissionQAData(aHist, 2)
    plotTransmissionQAData(bHist, 3)

#-----------------------------------------------------------------------------

##Plots A and B histograms overlaid on the same pad
def plotAllTransmissionQAData_ABOverlaid():
    global canvas, aHist, bHist

    aHist.SetLineColor(2)
    bHist.SetLineColor(4)

    aHist.Draw()
    bHist.Draw("same")
    
    canvas.Update()


#-----------------------------------------------------------------------------

  
