//
//  File = "analyzeSipmVendor.C"
//
//
// Written by cmj 2017Jul14 to show how to 
// read the root tree from the Sipms root file
// and populate histograms with them.
//
//
// to read in the tree and display as graphs..
//  To run this script by default:
//	> root
//	.x analyzeSipmVendors.C("rootFileName.root")
//  To print graphics files in the graphics directory:
//	> root
//	.x analyzeSipmsVendor.C("rootFileName.root",1)

//  To print out diagnostics...
//	> root
//	.x analyzeSipmsVendor.C("rootFileName.root",1,debugLevel)  // debug level = 1, 2, 3, 4
//
#include <iostream>
#include <sstream>
#include <cstring>
#include <ctime>
// 	Include the root header files here
#include "TStyle.h"
#include "TROOT.h"
#include "TStorage.h"
#include "TFile.h"
#include "TH1.h"
#include "TH2.h"
#include "TF1.h"
#include "TProfile.h"
#include "TNtuple.h"

#include "TRandom.h"
#include "TCanvas.h"
#include "TObjArray.h"
//      Include headers for trees...
#include "TTree.h"
#include "TBranch.h"
//
#include "TLegend.h"
#include "TMath.h"
#include "TVector3.h"
#include "TVectorD.h"
#include "TLorentzVector.h"
using namespace std;

TString graphicsDirectory = "graphicsProduction2018Jun27/";

//-------------------------------------------------------
//	Declare the Class!
class analyzeExtrusions{
  public:
  analyzeExtrusions(TString tempInFile, Int_t printGraphics, Int_t tempDebug);
  ~analyzeExtrusions();
  void setBranches(void);
  void bookHistograms(void);
  void fillHistograms(void);
  void drawCanvas(void);
  private:
        TFile *inputRootFile;
    TTree *myTree1;   // TTree to hold the Sipm currents with light source....
    TTree *myTree2;   // TTree to hold the dark current tree
    TString GraphicsFileType;
    TString Title;
    TString Name;
        // Control features of class...
    Int_t cmjDiag;
    Int_t printGraphicsFile;
    // Define histograms
    //TH1F *h_biasVoltage, *h_darkCurrent,*h_gain, *h_temperature;
    TH1F *h_lightYield, *h_base, *h_height, *h_diameter1, *h_diameter2;
    TH1F *h_base_fit, *h_height_fit;
    // Define Bins
    Int_t nBinYield; Double_t lowYieldBin; Double_t hiYieldBin;
    Int_t nBinBase;  Double_t lowBaseBin; Double_t hiBaseBin;
    Int_t nBinHeight;   Double_t lowHeightBin;   Double_t hiHeightBin;
    Int_t nBinDiameter; Double_t lowDiameterBin; Double_t hiDiameterBin;
    Int_t nBinBase_fit;  Double_t lowBaseBin_fit; Double_t hiBaseBin_fit;
    Int_t nBinHeight_fit;   Double_t lowHeightBin_fit;   Double_t hiHeightBin_fit;
    // Define Canvases
    //TCanvas *c_biasVoltage, *c_darkCurrent,*c_gain,*c_temperature;
    TCanvas *c_lightYield, *c_base, *c_height, *c_diameter1, *c_diameter2;
    TCanvas *c_base_fit, *c_height_fit;
    //
   // Char_t sipmNumber[21];  // This must equal the number of characters used in the PyRoot script!!!
    Float_t lightYield, base, height, diameter1, diameter2;
};
// ------------------------drawCurrentCanvas(void)------------------------------
//  Implement the Class!
// ------------------------------------------------------
//  Constructor
  analyzeExtrusions::analyzeExtrusions(TString tempInFile,Int_t printGraphics = 0, Int_t debug = 0){
  cmjDiag = debug;
    if(cmjDiag != 0) {
    cout <<"**analyzeExtrusions::analyzeExtrusions.. turn on debug: debug level = "<<cmjDiag<<endl;
    cout<<"**analyzeExtrusions::analyzeExtrusions: start"<<endl;
    }
  printGraphicsFile = printGraphics;
    if(printGraphicsFile != 0) cout<<"**analyzeExtrusions::analyzeExtrusions... print graphics file" << endl;
  gStyle -> SetOptStat("nemruoi");  // Print statistitics... page 32 root manual.. reset defaul
  gStyle -> SetOptDate(1);       // Print date on plots
  gStyle -> SetOptFit(1111); // show parameters, errors and chi2... page 72 root manual
  inputRootFile = new TFile(tempInFile);
  // Get the first root tree for the events with a light source
  myTree1 = new TTree("myTree1","Extrusion Measurments");
  //myTree1 = (TTree*)inputRootFile->Get("DiCounterSignal/diCounterSignal");
  myTree1 = (TTree*)inputRootFile->Get("Extrusion");
  if(cmjDiag > 1 ) myTree1->Scan();
  if(cmjDiag > 2) cout << "Current Root Directory "<< (gDirectory->GetPath()) << endl;
  //nVoltBin= 100; lowVoltBin=53.3; hiVoltBin=53.7;
  //nDarkCurrentBin = 10; lowDarkCurrentBin=0.05; hiDarkCurrentBin=1.0;
  //nGainBin = 10;  lowGainBin = -1.0; hiGainBin = 1.0;
  //nTempBin = 10;  lowTempBin = 24.0; hiTempBin = 27.0;
  
  nBinYield    = 100; lowYieldBin    = 1.0e6; hiYieldBin = 5.0e6;
  nBinBase     = 100; lowBaseBin     = 49.0; hiBaseBin = 53.0;
  nBinHeight   = 100; lowHeightBin   = 18.0; hiHeightBin = 22.0;
  nBinDiameter = 80; lowDiameterBin = 1.0;  hiDiameterBin = 5.0;
  nBinBase_fit     = 50; lowBaseBin_fit     = 51.0; hiBaseBin_fit = 51.6;
  nBinHeight_fit   = 50; lowHeightBin_fit   = 19.5; hiHeightBin_fit = 20.0;
}
// ------------------------------------------------------
//  Destructor
  analyzeExtrusions::~analyzeExtrusions(){ 
  if(cmjDiag != 0) cout<<"**analyzeExtrusions::~analyzeExtrusions: end"<<endl;
  return;
}
// -----------------------------------------------------------------------
//  Define the histograms.... for tree 1 (signal)
void analyzeExtrusions::bookHistograms(void){
  if(cmjDiag != 0) cout<<"**analyzeExtrusions::bookHistograms"<<endl;
  //h_biasVoltage = new TH1F("h_biasVoltage","Sipm Vendor Bias Voltage",nVoltBin,lowVoltBin,hiVoltBin);
  //h_darkCurrent = new TH1F("h_darkCurrent","Sipm Vendor Dark Current",nDarkCurrentBin,lowDarkCurrentBin,hiDarkCurrentBin);
  //h_gain = new TH1F("h_gain","Sipm Vendor Gain",nGainBin,lowGainBin,hiGainBin);
  //h_temperature = new TH1F("h_temperature","Sipm Vendor Temperature",nTempBin,lowTempBin,hiTempBin);
  
  h_lightYield = new TH1F("h_lightYield","Extrusion Light Yield",nBinYield,lowYieldBin,hiYieldBin);
  h_base = new TH1F("h_base","Extrusion Base Measurement",nBinBase,lowBaseBin,hiBaseBin);
  h_height = new TH1F("h_height","Extrusion height Measurement",nBinHeight,lowHeightBin,hiHeightBin);
  h_diameter1 = new TH1F("h_diameter1","Diameter 1 Measurment",nBinDiameter,lowDiameterBin,hiDiameterBin);
  h_diameter2 = new TH1F("h_diameter2","Diameter 2 Measurment",nBinDiameter,lowDiameterBin,hiDiameterBin);
  
  h_base_fit = new TH1F("h_base_fit","Extrusion Base Measurement (Expanded)",nBinBase_fit,lowBaseBin_fit,hiBaseBin_fit);
  h_height_fit = new TH1F("h_height_fit","Extrusion height Measurement (Expanded)",nBinHeight_fit,lowHeightBin_fit,hiHeightBin_fit);

}
// -----------------------------------------------------------------------
//  Define Branches.... from tree 1 (signal)
void analyzeExtrusions::setBranches(void){
  if(cmjDiag != 0)cout<<"**analyzeExtrusions::setCurrentBranches"<<endl;
  myTree1->SetBranchAddress("lightYield",&lightYield);
  myTree1->SetBranchAddress("base",&base);
  myTree1->SetBranchAddress("height",&height);
  myTree1->SetBranchAddress("diameter1",&diameter1);
  myTree1->SetBranchAddress("diameter2",&diameter2);
  if(cmjDiag > 3) myTree1->Print();
}
// -----------------------------------------------------------------------
//  fill the histograms.... from tree 1 (signal)
//  The way PyRoot works to save a tree is to save lists...
//	This is effectively one entry with arrays that are the 
//	size of the number of leaves.....
void analyzeExtrusions::fillHistograms(void){
  if(cmjDiag != 0) cout<<"**analyzeExtrusions::fillCurrentHistograms"<<endl;
  if(cmjDiag > 2) myTree1->Scan();
  Int_t maxEntries = (Int_t) myTree1->GetEntries();
  if(cmjDiag != 0) cout<<"**analyzeExtrusions::fillCurrentHistogram maxEntries = "<<maxEntries<<endl;
  for(Int_t m = 0; m < maxEntries; m++){
  myTree1->GetEntry(m);
  //h_biasVoltage->Fill(vendorBiasVoltage);
  //h_darkCurrent->Fill(vendorDarkCurrent);
  //h_gain->Fill(vendorGain);
  //h_temperature->Fill(vendorTemperature);
  h_lightYield->Fill(lightYield);
  h_base->Fill(base);
  h_height->Fill(height);
  h_diameter1->Fill(diameter1);
  h_diameter2->Fill(diameter2);
  h_base_fit->Fill(base);
  h_height_fit->Fill(height);
  }
}
// -----------------------------------------------------------------------
//  Draw the histograms.... from tree 1 (signal)
void analyzeExtrusions::drawCanvas(void){
Int_t X0   = 50;  Int_t Y0   = 50;
Int_t DelX = 10;  Int_t DelY = 10;
Int_t X; Int_t Y;
Int_t Width = 600; Int_t Height = 600;
X = X0; Y = Y0;
TDatime *myTime = new TDatime();
TString yTitle = "";
Float_t binInterval = 0.0;
TString binIntervalString = "";
Char_t space[2] = " ";
Char_t underline[2] = "_";
TString outDirectory = graphicsDirectory;
TString theTime = myTime->AsString();
//
Float_t labelSize = 0.05;
Float_t titleSize = 0.05;
if(cmjDiag != 0) cout << "**analyzeExtrusions::drawCanvas: time = "<< theTime.ReplaceAll(" ","_") <<endl;
c_lightYield = new TCanvas("c_lightYield","Extrusion Light Yield Measurement",X,Y,Width,Height);
binInterval = (hiYieldBin-lowYieldBin)/(Float_t)nBinYield;
binIntervalString = Form("%.1g",binInterval);
yTitle = "Counts per "+binIntervalString;
h_lightYield->GetYaxis()->SetTitle(yTitle);
//h_base->GetYaxis()->SetTitleSize(0.02);
h_lightYield->GetXaxis()->SetTitle("Light Yield (counts)");
h_lightYield->SetFillColor(kBlue);
h_lightYield->Draw();
  if(printGraphicsFile != 0) c_lightYield->Print(outDirectory+"lightYield_"+theTime+".png");
X += DelX; Y += DelY;
c_base = new TCanvas("c_base","Extrusion Base Measurement",X,Y,Width,Height);
binInterval = (hiBaseBin-lowBaseBin)/(Float_t)nBinBase;
binIntervalString = Form("%.1g",binInterval);
yTitle = "Counts per "+binIntervalString+" mm";
h_base->GetYaxis()->SetTitle(yTitle);
//h_base->GetYaxis()->SetTitleSize(0.02);
h_base->GetXaxis()->SetTitle("Base Width (mm)");
h_base->SetFillColor(kRed);
h_base->Draw();
  if(printGraphicsFile != 0) c_base->Print(outDirectory+"base_"+theTime+".png");
X += DelX; Y += DelY;
c_height = new TCanvas("c_height","Extrusion Height Measurment",X,Y,Width,Height);
binInterval = (hiHeightBin-lowHeightBin)/(Float_t)nBinHeight;
binIntervalString = Form("%.1g",binInterval);
yTitle = "Counts per "+binIntervalString+" mm";
h_height->GetYaxis()->SetTitle(yTitle);
//h_base->GetYaxis()->SetTitleSize(0.02);
h_height->GetXaxis()->SetTitle("Height (mm)");
h_height->SetFillColor(kGreen);
h_height->Draw();
  if(printGraphicsFile != 0) c_height->Print(outDirectory+"height_"+theTime+".png");
X += DelX; Y += DelY;
c_diameter1 = new TCanvas("c_diameter1","Extrusion Diameter 1 Measurment",X,Y,Width,Height);
binInterval = (hiDiameterBin-lowDiameterBin)/(Float_t)nBinDiameter;
binIntervalString = Form("%.1g",binInterval);
yTitle = "Counts per "+binIntervalString+" mm";
h_diameter1->GetYaxis()->SetTitle(yTitle);
//h_base->GetYaxis()->SetTitleSize(0.02);
h_diameter1->GetXaxis()->SetTitle("Diameter 1 (mm)");
h_diameter1->SetFillColor(kViolet);
h_diameter1->Draw();
  if(printGraphicsFile != 0) c_diameter1->Print(outDirectory+"diameter1_"+theTime+".png");
  X += DelX; Y += DelY;
c_diameter2 = new TCanvas("c_diameter2","Extrusion Diameter 2 Measurment",X,Y,Width,Height);
binInterval = (hiDiameterBin-lowDiameterBin)/(Float_t)nBinDiameter;
binIntervalString = Form("%.1g",binInterval);
yTitle = "Counts per "+binIntervalString+" mm";
h_diameter2->GetYaxis()->SetTitle(yTitle);
//h_base->GetYaxis()->SetTitleSize(0.02);
h_diameter2->GetXaxis()->SetTitle("Diameter 2 (mm)");
h_diameter2->SetFillColor(kOrange+10);
h_diameter2->Draw();
  if(printGraphicsFile != 0) c_diameter2->Print(outDirectory+"diameter2_"+theTime+".png");
  
  
X += DelX; Y += DelY;
c_base_fit = new TCanvas("c_base_fit","Extrusion Base Measurement (Expanded)",X,Y,Width,Height);
binInterval = (hiBaseBin_fit-lowBaseBin_fit)/(Float_t)nBinBase_fit;
binIntervalString = Form("%.1g",binInterval);
yTitle = "Counts per "+binIntervalString+" mm";
h_base_fit->GetYaxis()->SetTitle(yTitle);
//h_base->GetYaxis()->SetTitleSize(0.02);
h_base_fit->SetFillColor(kRed);
h_base_fit->GetXaxis()->SetTitle("Base Width (mm)");
h_base_fit->Draw();
  if(printGraphicsFile != 0) c_base_fit->Print(outDirectory+"base_expanded_"+theTime+".png");
X += DelX; Y += DelY;
c_height_fit = new TCanvas("c_height_fit","Extrusion Height Measurment (Expanded)",X,Y,Width,Height);
binInterval = (hiHeightBin_fit-lowHeightBin_fit)/(Float_t)nBinHeight_fit;
binIntervalString = Form("%.1g",binInterval);
yTitle = "Counts per "+binIntervalString+" mm";
h_height_fit->GetYaxis()->SetTitle(yTitle);
//h_base->GetYaxis()->SetTitleSize(0.02);
h_height_fit->GetXaxis()->SetTitle("Height (mm)");
h_height_fit->SetFillColor(kGreen);
h_height_fit->Draw();
  if(printGraphicsFile != 0) c_height_fit->Print(outDirectory+"height_expanded_"+theTime+".png");
  
}
//
//  --------------------------------------------------------------------
//  Run macro here....
void analyzeExtrusionMeasurements(TString inFile = "ExtrusionRootHistograms_2018Jun27_12_16_53_.root",Int_t drawGraphics = 0, Int_t debugLevel = 0){  // This file has the entire production
analyzeExtrusions *myAnalyzeExtursions = new analyzeExtrusions(inFile,drawGraphics,debugLevel);
//	Signal... Current with dicounters expoxed to light source.
myAnalyzeExtursions -> bookHistograms();
myAnalyzeExtursions -> setBranches();
myAnalyzeExtursions -> fillHistograms();
myAnalyzeExtursions -> drawCanvas();
}