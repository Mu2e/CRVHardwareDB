##Updated functions for analyzing and plotting source QA data
##Based in part of SourceQATools.py
##Written by Ben Barton
##bb6yx@virginia.edu, 99bbarton@gmail.com
##540-355-8918
##08/20/18 - Debugged initial version complete

import ROOT

canvas = None #Canvas to plot histograms on
histograms = [] #List of all ROOT TH1F histograms used

#------------------------------------------------------------------------------------------------------------

##Function to initialize a new canvas
def initializeCanvas(name, title, plotParams):
    global canvas
    canvas = ROOT.TCanvas(name,title,1)

    if plotParams[0] == "ALL":
        canvas.Divide(2,2)

#------------------------------------------------------------------------------------------------------------

##Function to look for and flag obviously false data values (e.g. negative current) in the lines of
##read from a file in the database upload format
##Returns a list of lines which contain bad data
def flagData(fileLines, minThresh = 0, maxThresh = 1.5):
    badDataLines = []


    for lnNum in range(len(fileLines)):
        data = fileLines[lnNum].split(",")[7:15]

        for val in data:
            if float(val) < minThresh or float(val) > maxThresh:
                badDataLines.append(lnNum)

    return badDataLines
            
#-------------------------------------------------------------------------------

##Function to prompt user for what to plot
##Returns a list of 8 strings with the selected parameters
def getPlotParameters():
    params = []

    #Side
    print "\nSelect which data you would like plotted:"
    print 'Enter "A" for A-side channels'
    print 'Enter "B" for B-side channels'
    print 'Enter "both" for all non-dark values'
    print 'Enter "dark" for dark current'
    print 'Hit "Enter" for all of the above plots'
    inp = raw_input()
    if inp.upper() == "A":
        params.append("A")
    elif inp.upper() == "B":
        params.append("B")
    elif inp.upper() == "DARK":
        params.append("DARK")
    elif inp.upper() == "BOTH":
        params.append("BOTH")
    else:
        params.append("ALL")

    #Source Proximity
    print "\nSelect which portion of the data you would like plotted:"
    print 'Enter "0" to plot all data'
    print 'Enter "1" to plot only data from the side closest to the source (strong-side)'
    print 'Enter "2" to plot only data from the side farthest away from the source (weak-side)'
    inp = raw_input()
    if inp == "1":
        params.append("STRONG")
    elif inp == "2":
        params.append("WEAK")
    else:
        params.append("ALL")

    #By channel?
    print "\nWould you like data plotted by channel?"
    print 'Enter "y" or "n":'
    inp = raw_input()
    if inp.upper() == "Y":
        print 'Enter which channels you wish to be plotted as a combination of the numbers 1-4'
        print '(e.g. "13" plots channels 1 & 3)'
        inp = raw_input()
        params.append(inp)
    else:
        params.append("N")

    #Subtract dark current?
    if params[0] != "DARK":
        print "\nWould you like dark current to be subtracted from current values?"
        print 'Enter "y" or "n":'
        inp = raw_input()
        if inp.upper() == "Y":
            params.append("Y")
        else:
            params.append("N")
    else:
        params.append("N")

    #Correct to crystals?
    print "\nWould you like values corrected to crystals?"
    print 'Enter "y" or "n":'
    inp = raw_input()
    if inp.upper() == "Y":
        params.append("Y")
        params.append("N") #No temp correction if correcting to crystals
    else:
        params.append("N")

        #Correct to temperature?
        print "\nWould you like values corrected only for temperature?"
        print 'Enter "y" or "n":'
        inp = raw_input()
        if inp.upper() == "Y":
            params.append("Y")
            print "\nNOT CURRENTLY IMPLEMENTED\n"
        else:
            params.append("N")

    #Plot ratio to golden counter?
    print "\nWould you like ratios to the golden counter plotted instead of currents?"
    print 'Enter "y" or "n":'
    inp = raw_input()
    if inp.upper() == "Y":
        params.append("Y")
    else:
        params.append("N")

    #Normalize by channel?
    print "\nWould you like data to be normalized by channel?"
    print 'Enter "y" or "n":'
    inp = raw_input()
    if inp.upper() == "Y":
        params.append("Y")
    else:
        params.append("N")

    return params

#------------------------------------------------------------------------------------------------------------

##Helper function to initialize ROOT histograms
def initializeHist(title, name, data, plotParams):
    
    if len(data) > 0:
        if plotParams[7] == "Y": #If normalized
            hist = ROOT.TH1F(name, title, 50 , 0.5, 1.5)
            hist.SetXTitle("Current (normalized by channel)")
        elif plotParams[6] == "Y":
            hist = ROOT.TH1F(name, title, 40 , 0, 2)
            hist.SetXTitle("Ratio to golden dicounter")
        else:
            hist = ROOT.TH1F(name, title, int((max(data) - min(data)) / 0.005), min(data) - 0.05, max(data) + 0.05)
            hist.SetXTitle("Current (mA)")     

        for val in data:
            if val > 0:
                hist.Fill(val)

        return hist
    return None
    
#------------------------------------------------------------------------------------------------------------

##Function to plot a histogram
def plot(hist, canvPad = 1):
    global canvas

    canvas.cd(canvPad)
    
    if hist == None:
        return -1

    hist.Draw()
    canvas.Update()

#------------------------------------------------------------------------------------------------------------

##Function to plot up to 4 histograms overlaid on the same canvas pad
def plotOverlaid(hists, pad = 1):
    global canvas

    canvas.cd(pad)
    
    if len(hists) >= 1:
        if hists[0].GetEntries() > 0:
            hists[0].SetLineColor(2) #Red
            hists[0].Draw()
    if len(hists) >= 2:
        if hists[1].GetEntries() > 0:
            hists[1].SetLineColor(4) #Blue
            hists[1].Draw("same")
    if len(hists) >= 3:
        if hists[2].GetEntries() > 0:
            hists[2].SetLineColor(6) #Magenta
            hists[2].Draw("same")
    if len(hists) >= 4:
        if hists[3].GetEntries() > 0:
            hists[3].SetLineColor(5) #Yellow
            hists[3].Draw("same")

    #Add in legend ##################################################################################

    canvas.Update()

#------------------------------------------------------------------------------------------------------------

##Function to plot desired source test data
def plotSourceData(params, sns, data, goldens):
    global histograms #List of histograms
    #Arrays to store processed values
    a1s = []
    a2s = []
    a3s = []
    a4s = []
    b1s = []
    b2s = []
    b3s = []
    b4s = []
    d1s = []
    d2s = []
    d3s = []
    d4s = [] 
    #Temporary arrays for processing
    vals = []
    golds = []
    crysts = [] 
    hists = [] #Histograms to plot on any particular pad


    #Process and plot data
    for sn in sns:    
        if params[0] == "A" or params[0] == "BOTH" or params[0] == "ALL": #Need side-A data
            if params[1] == "STRONG": #Source 1m from side-A
                if data[sn][0][0] < 0:
                    print "WARNING: Missing strong A-side data for " + str(sn) + " - skipping"
                    continue
                for i in range(0,4):
                    vals.append(data[sn][0][i])
                    crysts.append(data[sn][2][i])
                

                if params[3] == "Y": #Subtract out dark current
                    if data[sn][0][12] == -1:
                        print "WARNING: No dark current for " + str(sn) + " - skipping"
                        continue                        
                        
                    for i in range(0,4):
                        vals[i] = vals[i] - data[sn][0][12 + i]
                        crysts[i] = crysts[i] - data[sn][2][12 + i]

                    if params[4] == "Y": #Correct using crystals
                        cFctr = sum(crysts)
                        if cFctr < 0:
                            print "WARNING: No crystal data for " + str(sn) + " - skipping"
                            continue
                        for i in range(0,4):
                            vals[i] = vals[i] / cFctr

                    elif params[6] == "Y": #Plot ratio to golden dicounter, not current
                        date = data[sn][0][5].date()
                        if date not in goldens.keys():
                            print "WARNING: No golden measurement on " + str(date) + " - skipping " + sn
                            continue
                        for i in range(0,4):
                            golds.append(goldens[date][0][i] - goldens[date][0][12 + i])
                            vals[i] = vals[i] / golds[i]

                else: #Don't subtract dark current
                    if params[4] == "Y": #Correct using crystals
                        cFctr = sum(crysts)
                        if cFctr < 0:
                            print "WARNING: No crystal data for " + str(sn) + " - skipping"
                            continue
                        for i in range(0,4):
                            vals[i] = vals[i] / cFctr

                    elif params[6] == "Y": #Plot ratio to golden dicounter, not current
                        date = data[sn][0][5].date()
                        if date not in goldens.keys():
                            print "WARNING: No golden measurement on " + str(date) + " - skipping " + sn
                            continue
                        for i in range(0,4):
                            golds.append(goldens[date][0][i])
                            vals[i] = vals[i] / golds[i]

            elif params[1] == "WEAK": #Source 1m from side-B
                if data[sn][0][6] < 0:
                    print "WARNING: Missing weak A-side data for " + str(sn) + " - skipping"
                    continue
                for i in range(0,4):
                    vals.append(data[sn][0][6 + i])
                    crysts.append(data[sn][2][6 + i])
                

                if params[3] == "Y": #Subtract out dark current
                    if data[sn][0][12] == -1:
                        print "WARNING: No dark current for " + str(sn) + " - skipping"
                        continue                        
                        
                    for i in range(0,4):
                        vals[i] = vals[i] - data[sn][0][12 + i]
                        crysts[i] = crysts[i] - data[sn][2][12 + i]

                    if params[4] == "Y": #Correct using crystals
                        cFctr = sum(crysts)
                        if cFctr < 0:
                            print "WARNING: No crystal data for " + str(sn) + " - skipping"
                            continue
                        for i in range(0,4):
                            vals[i] = vals[i] / cFctr

                    elif params[6] == "Y": #Plot ratio to golden dicounter, not current
                        date = data[sn][0][11].date()
                        if date not in goldens.keys():
                            print "WARNING: No golden measurement on " + str(date) + " - skipping " + sn
                            continue
                        for i in range(0,4):
                            golds.append(goldens[date][0][i] - goldens[date][0][12 + i])
                            vals[i] = vals[i] / golds[i]

                else: #Don't subtract dark current
                    if params[4] == "Y": #Correct using crystals
                        cFctr = sum(crysts)
                        if cFctor < 0:
                            print "WARNING: No crystal data for " + str(sn) + " - skipping"
                            continue
                        for i in range(0,4):
                            vals[i] = vals[i] / cFctr

                    elif params[6] == "Y": #Plot ratio to golden dicounter, not current
                        date = data[sn][0][11].date()
                        if date not in goldens.keys():
                            print "WARNING: No golden measurement on " + str(date) + " - skipping " + sn
                            continue
                        for i in range(0,4):
                            golds.append(goldens[date][0][i])
                            vals[i] = vals[i] / golds[i]

            else: #All source positions
                if data[sn][0][0] < 0:
                    print "WARNING: Missing strong A-side data for " + str(sn) + " - skipping"
                    continue
                for i in range(0,4): #Strong values
                    vals.append(data[sn][0][i])
                    crysts.append(data[sn][2][i])
                if data[sn][0][6] < 0:
                    print "WARNING: Missing weak A-side data for " + str(sn) + " - skipping"
                    continue
                for i in range(0,4): #Weak values
                    vals.append(data[sn][0][6 + i])
                
                if params[3] == "Y": #Subtract out dark current
                    if data[sn][0][12] == -1:
                        print "WARNING: No dark current for " + str(sn) + " - skipping"
                        continue                        
                    for i in range(0,4):
                        vals[i] = vals[i] - data[sn][0][12 + i] #Strong
                        vals[4 + i] = vals[4 + i] - data[sn][0][12 + i] #Weak
                        crysts[i] = crysts[i] - data[sn][2][12 + i]

                    if params[4] == "Y": #Correct using crystals
                        cFctr = sum(crysts)
                        if cFctr < 0:
                            print "WARNING: No crystal data for " + str(sn) + " - skipping"
                            continue
                        for i in range(0,8):
                            vals[i] = vals[i] / cFctr

                    elif params[6] == "Y": #Plot ratio to golden dicounter, not current
                        date = data[sn][0][5].date()
                        if date not in goldens.keys():
                            print "WARNING: No golden measurement on " + str(date) + " - skipping " + sn
                            continue
                        for i in range(0,4):
                            golds.append(goldens[date][0][i] - goldens[date][0][12 + i])
                            vals[i] = vals[i] / golds[i]
                        for i in range(0,4):
                            golds.append(goldens[date][0][6 + i] - goldens[date][0][12 + i])
                            vals[4 + i] = vals[4 + i] / golds[4 + i]

                else: #Don't subtract dark current
                    if params[4] == "Y": #Correct using crystals
                        cFctr = sum(crysts)
                        if cFctr < 0:
                            print "WARNING: No crystal data for " + str(sn) + " - skipping"
                            continue
                        for i in range(0,8):
                            vals[i] = vals[i] / cFctr

                    elif params[6] == "Y": #Plot ratio to golden dicounter, not current
                        date = data[sn][0][5].date()
                        if date not in goldens.keys():
                            print "WARNING: No golden measurement on " + str(date) + " - skipping " + sn
                            continue
                        for i in range(0,4):
                            golds.append(goldens[date][0][i] - goldens[date][0][12 + i])
                            vals[i] = vals[i] / golds[i]
                        for i in range(0,4):
                            golds.append(goldens[date][0][6 + i] - goldens[date][0][12 + i])
                            vals[4 + i] = vals[4 + i] / golds[4 + i]
        
            #Store values to arrays and clear temporary arrays
            a1s.append(vals[0])
            a2s.append(vals[1])
            a3s.append(vals[2])
            a4s.append(vals[3])
            vals = []
            golds = []
            crysts = []
                
        if params[0] == "B" or params[0] == "BOTH" or params[0] == "ALL": #Need B-side data
            if params[1] == "STRONG": #Source 1m from side-B
                if data[sn][1][0] < 0:
                    print "WARNING: Missing strong B-side data for " + str(sn) + " - skipping"
                    continue
                for i in range(0,4):
                    vals.append(data[sn][1][i])
                    crysts.append(data[sn][2][i])
                

                if params[3] == "Y": #Subtract out dark current
                    if data[sn][1][12] == -1:
                        print "WARNING: No dark current for " + str(sn) + " - skipping"
                        continue                        
                        
                    for i in range(0,4):
                        vals[i] = vals[i] - data[sn][1][12 + i]
                        crysts[i] = crysts[i] - data[sn][2][12 + i]

                    if params[4] == "Y": #Correct using crystals
                        cFctr = sum(crysts)
                        if cFctr < 0:
                            print "WARNING: No crystal data for " + str(sn) + " - skipping"
                            continue
                        for i in range(0,4):
                            vals[i] = vals[i] / cFctr

                    elif params[6] == "Y": #Plot ratio to golden dicounter, not current
                        date = data[sn][1][5].date()
                        if goldens[date] == None:
                            print "WARNING: No golden measurement on " + str(date) + " - skipping " + sn
                            continue
                        for i in range(0,4):
                            golds.append(goldens[date][1][i] - goldens[date][1][12 + i])
                            vals[i] = vals[i] / golds[i]

                else: #Don't subtract dark current
                    if params[4] == "Y": #Correct using crystals
                        cFctr = sum(crysts)
                        if cFctr < 0:
                            print "WARNING: No crystal data for " + str(sn) + " - skipping"
                            continue
                        for i in range(0,4):
                            vals[i] = vals[i] / cFctr

                    elif params[6] == "Y": #Plot ratio to golden dicounter, not current
                        date = data[sn][1][5].date()
                        if goldens[date] == None:
                            print "WARNING: No golden measurement on " + str(date) + " - skipping " + sn
                            continue
                        for i in range(0,4):
                            golds.append(goldens[date][1][i])
                            vals[i] = vals[i] / golds[i]

            elif params[1] == "WEAK": #Source 1m from side-A
                if data[sn][1][6] < 0:
                    print "WARNING: Missing weak B-side data for " + str(sn) + " - skipping"
                    continue
                for i in range(0,4):
                    vals.append(data[sn][1][6 + i])
                    crysts.append(data[sn][2][6 + i])
                

                if params[3] == "Y": #Subtract out dark current
                    if data[sn][1][12] == -1:
                        print "WARNING: No dark current for " + str(sn) + " - skipping"
                        continue                        
                        
                    for i in range(0,4):
                        vals[i] = vals[i] - data[sn][1][12 + i]
                        crysts[i] = crysts[i] - data[sn][2][12 + i]

                    if params[4] == "Y": #Correct using crystals
                        cFctr = sum(crysts)
                        if cFctr < 0:
                            print "WARNING: No crystal data for " + str(sn) + " - skipping"
                            continue
                        for i in range(0,4):
                            vals[i] = vals[i] / cFctr

                    elif params[6] == "Y": #Plot ratio to golden dicounter, not current
                        date = data[sn][1][11].date()
                        if goldens[date] == None:
                            print "WARNING: No golden measurement on " + str(date) + " - skipping " + sn
                            continue
                        for i in range(0,4):
                            golds.append(goldens[date][1][i] - goldens[date][1][12 + i])
                            vals[i] = vals[i] / golds[i]

                else: #Don't subtract dark current
                    if params[4] == "Y": #Correct using crystals
                        cFctr = sum(crysts)
                        if cFctr < 0:
                            print "WARNING: No crystal data for " + str(sn) + " - skipping"
                            continue
                        for i in range(0,4):
                            vals[i] = vals[i] / cFctr

                    elif params[6] == "Y": #Plot ratio to golden dicounter, not current
                        date = data[sn][1][11].date()
                        if goldens[date] == None:
                            print "WARNING: No golden measurement on " + str(date) + " - skipping " + sn
                            continue
                        for i in range(0,4):
                            golds.append(goldens[date][1][i])
                            vals[i] = vals[i] / golds[i]

            else: #All source positions
                if data[sn][1][0] < 0:
                    print "WARNING: Missing strong B-side data for " + str(sn) + " - skipping"
                    continue
                for i in range(0,4): #Strong values
                    vals.append(data[sn][1][i])
                    crysts.append(data[sn][2][i])
                if data[sn][1][6] < 0:
                    print "WARNING: Missing weak B-side data for " + str(sn) + " - skipping"
                    continue
                for i in range(0,4): #Weak values
                    vals.append(data[sn][1][6 + i])
                
                if params[3] == "Y": #Subtract out dark current
                    if data[sn][1][12] == -1:
                        print "WARNING: No dark current for " + str(sn) + " - skipping"
                        continue                        
                    for i in range(0,4):
                        vals[i] = vals[i] - data[sn][1][12 + i] #Strong
                        vals[4 + i] = vals[4 + i] - data[sn][1][12 + i] #Weak
                        crysts[i] = crysts[i] - data[sn][2][12 + i]

                    if params[4] == "Y": #Correct using crystals
                        cFctr = sum(crysts)
                        if cFctr < 0:
                            print "WARNING: No crystal data for " + str(sn) + " - skipping"
                            continue
                        for i in range(0,8):
                            vals[i] = vals[i] / cFctr

                    elif params[6] == "Y": #Plot ratio to golden dicounter, not current
                        date = data[sn][1][5].date()
                        if goldens[date] == None:
                            print "WARNING: No golden measurement on " + str(date) + " - skipping " + sn
                            continue
                        for i in range(0,4):
                            golds.append(goldens[date][1][i] - goldens[date][1][12 + i])
                            vals[i] = vals[i] / golds[i]
                        for i in range(0,4):
                            golds.append(goldens[date][1][6 + i] - goldens[date][1][12 + i])
                            vals[4 + i] = vals[4 + i] / golds[4 + i]

                else: #Don't subtract dark current
                    if params[4] == "Y": #Correct using crystals
                        cFctr = sum(crysts)
                        if cFctr < 0:
                            print "WARNING: No crystal data for " + str(sn) + " - skipping"
                            continue
                        for i in range(0,8):
                            vals[i] = vals[i] / cFctr

                    elif params[6] == "Y": #Plot ratio to golden dicounter, not current
                        date = data[sn][1][5].date()
                        if goldens[date] == None:
                            print "WARNING: No golden measurement on " + str(date) + " - skipping " + sn
                            continue
                        for i in range(0,4):
                            golds.append(goldens[date][1][i] - goldens[date][1][12 + i])
                            vals[i] = vals[i] / golds[i]
                        for i in range(0,4):
                            golds.append(goldens[date][1][6 + i] - goldens[date][1][12 + i])
                            vals[4 + i] = vals[4 + i] / golds[4 + i]
        
            #Store values to arrays and clear temporary arrays
            b1s.append(vals[0])
            b2s.append(vals[1])
            b3s.append(vals[2])
            b4s.append(vals[3])
            vals = []
            golds = []
            crysts = []

        if params[0] == "DARK" or params[0] == "ALL": #If need dark current plot
            if data[sn][0][12] == -1:
                print "WARNING: No dark current for " + str(sn) + " - skipping"
                continue
            for i in range(0,4):
                vals.append(data[sn][0][12 + i])
                vals.append(data[sn][1][12 + i])

            if params[4] == "Y": #Correct using crystals
                cFctr = 0
                for i in range(0,4):
                    cFctr += data[sn][2][12 + i]
                if cFctr < 0:
                    print "WARNING: No crystal data for " + str(sn) + " - skipping"
                    continue
                for i in range(0,4):
                    vals[i] = vals[i] / cFctr
            
            #Store values in arrays and clear variables
            d1s.extend(vals[0:2])
            d2s.extend(vals[2:4])
            d3s.extend(vals[4:6])
            d4s.extend(vals[6:])
            vals = []
            cFctor = 0

    #Normalize if desired
    if params[7] == "Y":
        a1s = normalize(a1s)
        a2s = normalize(a2s)
        a3s = normalize(a3s)
        a4s = normalize(a4s)
        b1s = normalize(b1s)
        b2s = normalize(b2s)
        b3s = normalize(b3s)
        b4s = normalize(b4s)
        d1s = normalize(d1s)
        d2s = normalize(d2s)
        d3s = normalize(d3s)
        d4s = normalize(d4s)
    
    #Initialize and plot histograms
    if params[0] == "A" or params[0] == "ALL":
        if params[2] == "N": #Don't plot by channel
            aSide = a1s + a2s + a3s + a4s
            aHist = initializeHist("A-side Response", "A", aSide, params)
            histograms.append(aHist)

            if params[0] == "A":
                plot(aHist)
            else:
                plot(aHist, 3)
        else: #Plot by channel 
            if params[2].find("1") >= 0:
                hists.append(initializeHist("A1 Response", "A1", a1s, params))
            if params[2].find("2") >= 0:
                hists.append(initializeHist("A2 Response", "A2", a2s, params))
            if params[2].find("3") >= 0:
                hists.append(initializeHist("A3 Response", "A3", a3s, params))
            if params[2].find("4") >= 0:
                hists.append(initializeHist("A4 Response", "A4", a4s, params))
            
            if params[0] == "A":
                plotOverlaid(hists)
            else:
                plotOverlaid(hists, 3)

            histograms.extend(hists)
    hists = []

    if params[0] == "B" or params[0] == "ALL":
        if params[2] == "N": #Don't plot by channel
            bSide = b1s + b2s + b3s + b4s
            bHist = initializeHist("B-side Response", "B", bSide, params)
            histograms.append(bHist)

            if params[0] == "B":
                plot(bHist)
            else:
                plot(bHist, 4)
        else: #Plot by channel 
            if params[2].find("1") >= 0:
                hists.append(initializeHist("B1 Response", "B1", b1s, params))
            if params[2].find("2") >= 0:
                hists.append(initializeHist("B2 Response", "B2", b2s, params))
            if params[2].find("3") >= 0:
                hists.append(initializeHist("B3 Response", "B3", b3s, params))
            if params[2].find("4") >= 0:
                hists.append(initializeHist("B4 Response", "B4", b4s, params))
            
            if params[0] == "B":
                plotOverlaid(hists)
            else:
                plotOverlaid(hists, 4)

            histograms.extend(hists)
    hists = []

    if params[0] == "DARK" or params[0] == "ALL":
        if params[2] == "N": #Don't plot by channel
            darks = d1s + d2s + d3s + d4s
            darkHist = initializeHist("Dark Current", "Dark Current", darks, params)
            histograms.append(darkHist)

            if params[0] == "DARK":
                plot(darkHist)
            else:
                plot(darkHist, 2)
        else: #Plot by channel
            if params[2].find("1") >= 0:
                hists.append(initializeHist("D1", "D1", d1s, params))
            if params[2].find("2") >= 0:
                hists.append(initializeHist("D2", "D2", d2s, params))
            if params[2].find("3") >= 0:
                hists.append(initializeHist("D3", "D4", d1s, params))
            if params[2].find("4") >= 0:
                hists.append(initializeHist("D4", "D4", d2s, params))  

            if params[0] == "DARK":
                plotOverlaid(hists)
            else:
                plotOverlaid(hists, 2)

            histograms.extend(hists)
    hists = []
    
    if params[0] == "BOTH" or params[0] == "ALL":
        if params[2] == "N": #Don't plot by channel
            both = a1s + a2s + a3s + a4s + b1s + b2s + b3s + b4s
            bothHist = initializeHist("Di-Counter Response", "All Channels", both, params)
            histograms.append(bothHist)

            plot(bothHist)
        else: #Plot by channel
            if params[2].find("1") >= 0:
                hists.append(initializeHist("Channel 1", "Channel 1", a1s + b1s, params))
            if params[2].find("2") >= 0:
                hists.append(initializeHist("Channel 2", "Channel 2", a2s + b2s, params))
            if params[2].find("3") >= 0:
                hists.append(initializeHist("Channel 3", "Channel 3", a3s + b3s, params))
            if params[2].find("4") >= 0:
                hists.append(initializeHist("Channel 4", "Channel 4", a4s + b4s, params))

            plotOverlaid(hists)
            histograms.extend(hists)
    hists = []
        

#------------------------------------------------------------------------------------------------------------

#Helper function to normalize a list of data about its mean
def normalize(vals = []):
    if len(vals) == 0:
        return vals

    for val in vals:
        if val < 0:
            del val
            
    mean = sum(vals) / len(vals)
    normVals = []
    for val in vals:
        normVals.append(val / mean)

    return normVals

#------------------------------------------------------------------------------------------------------------

##Function to delete/close all ROOT objects to prevent memory leaks
def cleanRootObjects():
    global histograms, canvas

    for hist in histograms:
        del(hist)
    
    histograms = []

    canvas.Close()

#------------------------------------------------------------------------------------------------------------


