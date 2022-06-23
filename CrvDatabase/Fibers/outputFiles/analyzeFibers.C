//
//  File = "analyzeDiCounters.C"
//  Derived from File = "analyzeDiCounters.C"
//
//
// Written by cmj 2017Jul14 to show how to 
// read the root tree from the DiCounters root file
// and populate histograms with them.
//
//
// to read in the tree and display as graphs..
//  To run this script by default:
//	> root
//	.x analyzeDiCounters.C("rootFileName.root")
//  To print graphics files in the graphics directory:
//	> root
//	.x analyzeDiCounters.C("rootFileName.root",1)
//  To print out diagnostics...
//	> root
//	.x analyzeDiCounters.C("rootFileName.root",1,debugLevel)  // debug level = 1, 2, 3, 4
//
// Modified by cmj2022Jan24... changed how character strings are read from the
//                             root tree.  The python3 version of pyroot saves
//                             character strings as std:vector<std::string>.  This
//                             required changes to read in this structure.
// Modified by cmj2022Jan24... Add menu structure to select analyisis.
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

#include "TObject.h"
using namespace std;

//-------------------------------------------------------
//	Declare the Class!
class fiberTest{
  public:
  fiberTest(TString tempInFile, Int_t printGraphics, Int_t tempDebug);
  ~fiberTest();
  //  Vendor Measurements
  void choosePlotVendor(void);
  void readVendorMeasurements(TFile *);
  void setVendorBranches(void);
  void bookVendorHistograms(void);
  void fillVendorHistograms(void);
  void drawVendorCanvas(void);
    //  Local Measurements
  void choosePlotLocal(void);
  void readLocalMeasurements(TFile *);
  void setLocalBranches(void);
  void bookLocalHistograms(void);
  void fillLocalHistograms(void);
  void drawLocalCanvas(void);
  //   Read & plot Local Attenuation measurements (ADC counts) vs Wavelength (measured at UVa)
  void choosePlotLambdaVsWavelength(void);
  void readLambdavsAtten(TFile *);
  void plotLambdavsAtten(Int_t,TString,TTree *currentTree);
  void drawLambdavsAtten(void);
  //   Read & plot Local Attenuation measurements (ADC counts) vs Fiber Length (measured at UVa)
  void choosePlotAttenVsFiberLength_local(void);
  void readAttenVsLengthTree_local(TFile *);
  void plotAttenVsLength_local(Int_t,Int_t, TString,TTree *currentTree);
  void bookAttenVsLength_local(void);
  void fillAttenVsLength_local(void);
  void drawAttenVsLength_local(void);
   //   Read & plot Vendor Attenuation measurements (voltage (mV)) vs Fiber Length (measured by Hamamatsu)  
  void choosePlotAttenVsFiberLength_vendor();
  void readAttenVsLengthTree_vendor(TFile *);
  void plotAttenVsLength_vendor(Int_t,Int_t, TString,TTree *currentTree);
  void bookAttenVsLength_vendor(void);
  void fillAttenVsLength_vendor(void);
  void drawAttenVsLength_vendor(void);
  //
  void enableGraphics(Int_t);
  void setGraphicsDirectoryName(TString);
  //   
  TString makeGraphicsFileName(TString);
  int _printGraphics;
  private:
    TFile *inputRootFile;
    TTree *myTree1;   // TTree to hold the Vendor measured quantities....
    TTree *myTree2;   // TTree to hold the Locally measured quantities
    TString GraphicsFileType;
    TString Title;
    TString Name;
    TString graphicsFileDir;
    TString graphicsFileType;
    // Control features of class...
    Int_t cmjDiag;
    Int_t printGraphicsFile;
    // Define histograms
    TH1F *h_vendorDiameter, *h_vendorSigma, *h_vendorAttenuation, *h_vendorAttenuationVoltage, *h_vendorEccentricity;
    TH1F *h_vendorDiameter15, *h_vendorDiameter18;
    //
    TH1F *h_localDiameter, *h_localAttenuation;
    TCanvas *c_localDiameter, *c_localAttenuation;
    TH1F *h_localDiameter15, *h_localDiameter18;
    TCanvas *c_localDiameter15, *c_localDiameter18;
    //  Attenuation vs Wavelength!
    TGraph *gr_array_attenVsLambda[1000];  // Define an array of TGraphs
    TCanvas *c_array_attenVsLambda[1000];  // Define an array of Canvases 
    // Combine all data points onto one plot
    TMultiGraph *mg_attenVsLambda;
    TCanvas *c_mg_attenVsLambda;
    // Local Attenuation (ADC counts) vs Fiber Length (locally measured!)
    Int_t maxFibersLocal;
    TCanvas *c_array_attenVsLength_local_noFit[1000];  // Define an array of Canvases
    TGraph *gr_array_attenVsLength_local_noFit[1000];  //  Define an array of TGraphs
    TGraph *gr_array_attenVsLength_local[1000];        //  Define an array of TGraphs
    TCanvas *c_array_attenVsLength_local[1000];        // Define an array of Canvases
    TH1F *h_slope_attenVsLength_local;
    TCanvas *c_slope_attenVsLength_local;
    Float_t stored_slope_attenVsLength_local[1000];
    // Combine all data points onto one plot
    TMultiGraph *mg_attenVsLength_local;
    TCanvas *c_mg_attenVsLength_local;
    
    // Vendor Attenuation (Volts, mv) vs Fiber Length (Vendor measured!)
    Int_t maxFibersVendor;
    TCanvas *c_array_attenVsLength_vendor_noFit[1000]; // Define an array of Canvases
    TGraph *gr_array_attenVsLength_vendor_noFit[1000]; //  Define an array of TGraphs
    TGraph *gr_array_attenVsLength_vendor[1000];       //  Define an array of TGraphs
    TCanvas *c_array_attenVsLength_vendor[1000];       // Define an array of Canvases
    TH1F *h_slope_attenVsLength_vendor;
    TCanvas *c_slope_attenVsLength_vendor;
    Float_t stored_slope_attenVsLength_vendor[1000];
    // Combine all data points onto one plot
    TMultiGraph *mg_attenVsLength_vendor;
    TCanvas *c_mg_attenVsLength_vendor;

    // Define Bins
    Int_t nBin1; Double_t lowBin1; Double_t hiBin1;
    Int_t nBin2; Double_t lowBin2; Double_t hiBin2;
    Int_t nTBin; Double_t lowTBin; Double_t hiTBin;
    Int_t nSBin; Double_t lowSBin; Double_t hiSBin;
    
    Int_t nDiameter;      Double_t lowDiameter;      Double_t hiDiameter;
    Int_t nDiameter15;      Double_t lowDiameter15;    Double_t hiDiameter15;
    Int_t nDiameter18;      Double_t lowDiameter18;      Double_t hiDiameter18;
    Int_t nSigma;         Double_t lowSigma;         Double_t hiSigma;
    Int_t nVendAtten;     Double_t lowVendAtten;     Double_t hiVendAtten;
    Int_t nVendAttenVolt; Double_t lowVendAttenVolt; Double_t hiVendAttenVolt;
    Int_t nEccen;         Double_t lowEccen;         Double_t hiEnccen;
    //
    Int_t nDiameterLocal; Double_t lowDiameterLocal; Double_t hiDiameterLocal;
    Int_t nDiameterLocal15; Double_t lowDiameterLocal15; Double_t hiDiameterLocal15;
    Int_t nDiameterLocal18; Double_t lowDiameterLocal18; Double_t hiDiameterLocal18;
    // Define Canvases
    TCanvas *c_vendorDiameter, *c_vendorSigma, *c_vendorAttenuation, *c_vendorAttenuationVoltage, *c_vendorEccentricity;
    TCanvas *c_vendorDiameter15, *c_vendorDiameter18;
    TCanvas *c_attenVsLambda;
    Int_t nAttenVsLengthSlope ; Double_t lowAttenVsLengthSlope; Double_t hiAttenVsLengthSlope;
// 
   //  cmj2022Jan25
   //  For python 3... character arrays are stored as std::vector<std::string>
   std::vector<std::string> *vect_fiberId;             TBranch *branch_vect_fiberId;
   std::vector<std::string> *vect_fiberProductionDate; TBranch *branch_vect_fiberProductionDate;
   std::vector<std::string> *vect_fiberComment;        TBranch *branch_vect_fiberComment;
   TString string_fiberId, string_fiberProductionDate, string_fiberComment;
   // cmj2022 Jan25
   Int_t numberOfEntries;
   Float_t fiberVendorDiameter, fiberVendorSigma, fiberVendorAttenaution, fiberVendorAttenuationVoltage, fiberVendorEccentricity;
   //
   Float_t fiberLocalDiameter, fiberLocalAttenuation;
   //  cmj2022Jan25
   //  For python 3... character arrays are stored as std::vector<std::string>
   std::vector<std::string> *vect_fiberIdLocal; TBranch *branch_vect_fiberIdLocal;
   std::vector<std::string> *vect_fiberTestDateLocal; TBranch *branch_vect_fiberTestDateLocal;
   std::vector<std::string> *vect_fiberCommentLocal; TBranch *branch_vect_fiberCommentLocal;
   TString string_fiberIdLocal, string_fiberTestDateLocal, string_fiberCommentLocal;
};  
//
// ------------------------drawCurrentCanvas(void)------------------------------
//  Implement the Class!
// ------------------------------------------------------
//  Constructor
  fiberTest::fiberTest(TString tempInFile,Int_t printGraphics = 0, Int_t debug = 0){
  cmjDiag = debug;
    if(cmjDiag != 0) {
    cout <<"**fiberTest::fiberTest.. turn on debug: debug level = "<<cmjDiag<<endl;
    cout<<"**fiberTest::fiberTest... start"<<endl;
    }
  _printGraphics = printGraphics;
  graphicsFileType = ".png";
  graphicsFileDir = "Fibers-graphics2022Jan27-All/";
  //graphicsFileDir = "testGraphics/";
  printGraphicsFile = printGraphics;
  if(printGraphicsFile != 0) cout<<"**fiberTest::fiberTest... print graphics file" << endl;
  gStyle -> SetOptStat("nemruoi");  // Print statistitics... page 32 root manual.. reset defaul
  gStyle -> SetOptDate(1);       // Print date on plots
  gStyle -> SetOptFit(111111); // show parameters, errors and chi2... page 72 root manual
  //  Get root file containing root tree
  inputRootFile = new TFile(tempInFile);
  //
  nDiameter      = 100; lowDiameter15      = 1200.0;  hiDiameter15     = 1900;
  nDiameter15      = 40; lowDiameter15      = 1200.0;  hiDiameter15      = 1500.0;  // same scale as local
  nDiameter18      = 50; lowDiameter18      = 1500.0;  hiDiameter18      = 200.0;  // same scale as local
  nSigma         = 40; lowSigma         = 4.0;     hiSigma         = 14.0;
  nVendAtten     = 40; lowVendAtten     = 380.0;   hiVendAtten     = 480;
  nVendAttenVolt = 40; lowVendAttenVolt = 14.0;    hiVendAttenVolt = 22.0;
  nEccen         = 20;  lowEccen         = 0.0;     hiEnccen         = 5.0e-3;
  nAttenVsLengthSlope = 100 ; lowAttenVsLengthSlope = -0.2; Double_t hiAttenVsLengthSlope = 0.0;
  nDiameterLocal  = 100; lowDiameterLocal   = 1200.0;  hiDiameterLocal      = 1900.0;
  nDiameterLocal15  = 40; lowDiameterLocal15   = 1200.0;  hiDiameterLocal15      = 1500.0;
  nDiameterLocal18  = 50; lowDiameterLocal18   = 1500.0;  hiDiameterLocal18      = 2000.0;
}
// ------------------------------------------------------
//  Destructor
  fiberTest::~fiberTest(){ 
  if(cmjDiag != 0) cout<<"**fiberTest::~fiberTest: end"<<endl;
  return;
}
// ######################################################################
//   This group of methods reads in the trees for the
//   Vendor Measured quantities
// ----------------------------------------------------------------------
//  Plot the vendor measurements
void fiberTest::choosePlotVendor(void){
  readVendorMeasurements(inputRootFile);
  bookVendorHistograms();
  setVendorBranches();
  fillVendorHistograms();
  drawVendorCanvas();
  return;
}
// ----------------------------------------------------------------------
//   Read root tree with local measurements
void fiberTest::readVendorMeasurements(TFile *tempInputRootFile){
  // Get the first root tree for the events with a light source
  myTree1 = new TTree("myTree1","Fiber Test Results");
  myTree1 = (TTree*)inputRootFile->Get("Vendor Fiber Measurements");
}
// -----------------------------------------------------------------------
//  Define the histograms.... for tree 1 (signal)
void fiberTest::bookVendorHistograms(void){
  if(cmjDiag != 0) cout<<"**fiberTest::bookVendorHistograms"<<endl;
  // Vendor Measurements
  h_vendorDiameter = new TH1F("h_vendorDiameter","Vendor Measured Fiber Diameter",nDiameter,lowDiameter,hiDiameter);
  h_vendorDiameter->GetXaxis()->SetTitle("Diameter (#mu m)");
  //TGaxis *myX4 = (TGaxis*) h_vendorDiameter->GetXaxis();
  //myX4->SetMaxDigits(1);
  h_vendorDiameter->GetXaxis()->SetLabelSize(0.02);
  h_vendorDiameter->SetFillColor(kRed);
  
  h_vendorSigma = new TH1F("h_vendorSigma","Vendor Measured Fiber Sigma",nSigma,lowSigma,hiSigma);
  h_vendorSigma->GetXaxis()->SetTitle("Fiber Sigma (#mu m)");
  //TGaxis *myX0 = (TGaxis*) h_vendorSigma->GetXaxis();
  //myX0->SetMaxDigits(1);
  h_vendorSigma->GetXaxis()->SetLabelSize(0.02);
  h_vendorSigma->SetFillColor(kBlue);
  
  h_vendorEccentricity = new TH1F("h_vendorEccentricity","Vendor Measured Fiber Eccentricity",nEccen,lowEccen,hiEnccen);
  h_vendorEccentricity->GetXaxis()->SetTitle("Fiber Eccentricity");
  TGaxis *myX1 = (TGaxis*) h_vendorEccentricity->GetXaxis();
  myX1->SetMaxDigits(2);
  h_vendorEccentricity->SetFillColor(kGreen);
  
  h_vendorAttenuation = new TH1F("h_vendorAttenuation","Vendor Measured Fiber Attenuation Length",nVendAtten,lowVendAtten,hiVendAtten);
  h_vendorAttenuation->GetXaxis()->SetTitle("Fiber Attenuation(mm)");
  TGaxis *myX2 = (TGaxis*) h_vendorAttenuation->GetXaxis();
  myX2->SetMaxDigits(1);
  h_vendorAttenuation->SetFillColor(kViolet);
  
  h_vendorAttenuationVoltage = new TH1F("h_vendorAttenuationVoltage","Vendor Measured Fiber Attenuation Voltage",nVendAttenVolt,lowVendAttenVolt,hiVendAttenVolt);
  h_vendorAttenuationVoltage->GetXaxis()->SetTitle("Fiber Attenuation Voltage (V)");
  TGaxis *myX3 = (TGaxis*) h_vendorAttenuationVoltage->GetXaxis();
  myX3->SetMaxDigits(1);
  h_vendorAttenuation->SetFillColor(kViolet);
  h_vendorAttenuationVoltage->SetFillColor(kViolet);
  // ------------------
  h_vendorDiameter15 = new TH1F("h_vendorDiameter15","Vendor Measured Fiber Diameter15",nDiameter15,lowDiameter15,hiDiameter15);
  h_vendorDiameter15->GetXaxis()->SetTitle("Diameter (#mu m)");
  //TGaxis *myX10 = (TGaxis*) h_vendorDiameter15->GetXaxis();
  //myX10->SetMaxDigits(1);
  h_vendorDiameter15->GetXaxis()->SetLabelSize(0.02);
  h_vendorDiameter15->SetFillColor(kRed);
  //
  h_vendorDiameter18 = new TH1F("h_vendorDiameter18","Vendor Measured Fiber Diameter18",nDiameter18,lowDiameter18,hiDiameter18);
  h_vendorDiameter18->GetXaxis()->SetTitle("Diameter (#mu m)");
  //TGaxis *myX11 = (TGaxis*) h_vendorDiameter18->GetXaxis();
  //myX11->SetLabelSize(0.5);
  //myX11->SetMaxDigits(1);
  h_vendorDiameter18->GetXaxis()->SetLabelSize(0.02);
  h_vendorDiameter18->SetFillColor(kRed);
  return;
}
// -----------------------------------------------------------------------
//  Define Branches....
void fiberTest::setVendorBranches(void){
  if(cmjDiag != 0)cout<<"**fiberTest::setVendorBranches"<<endl;
  //  cmj2022Jan25
  // For python3 ... read character arrays stored as std::vector<std::string>
  vect_fiberId = 0; branch_vect_fiberId = 0;
  myTree1 -> SetBranchAddress("fiberId",&vect_fiberId,&branch_vect_fiberId);
  vect_fiberProductionDate = 0; branch_vect_fiberProductionDate =0;
  myTree1->SetBranchAddress("fiberProductionDate",&vect_fiberProductionDate,&branch_vect_fiberProductionDate);
  vect_fiberComment = 0; branch_vect_fiberComment;
  myTree1->SetBranchAddress("fiberComments",&vect_fiberComment,&branch_vect_fiberComment);
  // cmj2022Jan25
  myTree1->SetBranchAddress("fiberVendorDiameter",&fiberVendorDiameter);
  myTree1->SetBranchAddress("fiberVendorSigma",&fiberVendorSigma);
  myTree1->SetBranchAddress("fiberVendorAttenuation",&fiberVendorAttenaution);
  myTree1->SetBranchAddress("fiberVendorAttenuationVolt285cm",&fiberVendorAttenuationVoltage);
  myTree1->SetBranchAddress("fiberVendorEccentricity",&fiberVendorEccentricity);
  if(cmjDiag > 0) myTree1->Print();
}
// -----------------------------------------------------------------------
//  fill the histograms.... from tree 1 (signal)
//  The way PyRoot works to save a tree is to save lists...
//	This is effectively one entry with arrays that are the 
//	size of the number of leaves.....
void fiberTest::fillVendorHistograms(void){
  if(cmjDiag != 0) cout<<"**fiberTest::fillVendorHistograms"<<endl;
  if(cmjDiag > 2) myTree1->Scan();
  Int_t maxEntries = (Int_t) myTree1->GetEntries();
  if(cmjDiag != 0) cout<<"**fiberTest::fillVendorHistogram maxEntries = "<<maxEntries<<endl;
  for(Int_t m = 0; m < maxEntries; m++){
  myTree1->GetEntry(m);
  //  cmj2022Jan25
  //  Load the strings variable for selection of database keys... First get the branch_vect_fiberComment
  Long64_t tentry = myTree1->LoadTree(m);
  branch_vect_fiberId->GetEntry(tentry);
  branch_vect_fiberProductionDate->GetEntry(tentry);
  branch_vect_fiberComment->GetEntry(tentry);
  // Load the string variables for selection of database keys... Second get the contents
  string_fiberId             = vect_fiberId->at(m);
  string_fiberProductionDate = vect_fiberProductionDate->at(m);
  string_fiberComment        = vect_fiberComment->at(m);
  // cmj2022Jan25
  h_vendorDiameter->Fill(fiberVendorDiameter);
  h_vendorSigma->Fill(fiberVendorSigma);
  h_vendorAttenuation->Fill(fiberVendorAttenaution);
  h_vendorAttenuationVoltage->Fill(fiberVendorAttenuationVoltage);
  h_vendorEccentricity->Fill(fiberVendorEccentricity);
  if(!string_fiberId.Contains("M2103")) h_vendorDiameter15->Fill(fiberVendorDiameter);
  if(string_fiberId.Contains("M2103")) h_vendorDiameter18->Fill(fiberVendorDiameter);
  if(cmjDiag > 2){
    cout <<"**fiberTest::fillCurrentHistogram... fiberId = "<<string_fiberId<<endl;
    cout <<"**fiberTest::fillCurrentHistogram... fiberProductionDate = "<<string_fiberProductionDate<<endl;
    cout <<"**fiberTest::fillCurrentHistogram... fiberComment = "<<string_fiberComment<<endl;
    cout <<"**fiberTest::fillCurrentHistogram... fiberVendorDiameter = "<< fiberVendorDiameter << endl;
    cout <<"**fiberTest::fillCurrentHistogram... fiberVendorSigma    = "<< fiberVendorSigma << endl;
    cout <<"**fiberTest::fillCurrentHistogram... fiberVendorAttenaution   = "<< fiberVendorAttenaution << endl;
    cout <<"**fiberTest::fillCurrentHistogram... fiberVendorAttenuationVoltage = "<< fiberVendorAttenuationVoltage << endl;
    cout <<"**fiberTest::fillCurrentHistogram... fiberVendorEccentricity   = "<< fiberVendorEccentricity << endl;
    }
  }
}
// -----------------------------------------------------------------------
//  Draw the histograms.... from tree 1 (signal)
void fiberTest::drawVendorCanvas(void){
  Int_t X0   = 50;  Int_t Y0   = 50;
Int_t DelX = 10;  Int_t DelY = 10;
Int_t X; Int_t Y;
Int_t Width = 600; Int_t Height = 600;
X = X0; Y = Y0;
TString Title;
TString outFileName;
// 
X += DelX; Y += DelY;
Title = "Fibers-Vendor Measured Fiber Diameter";
c_vendorDiameter = new TCanvas("c_vendorDiameter",Title,X,Y,Width,Height);
h_vendorDiameter->Draw();
outFileName = makeGraphicsFileName(Title);
if(printGraphicsFile != 0) c_vendorDiameter ->Print(outFileName);
X += DelX; Y += DelY;
Title = "Fibers-Vendor Measured Fiber Sigma";
c_vendorSigma = new TCanvas("c_vendorSigma",Title,X,Y,Width,Height);
h_vendorSigma->Draw();
outFileName = makeGraphicsFileName(Title);
if(printGraphicsFile != 0) c_vendorSigma ->Print(outFileName);
X += DelX; Y += DelY;
Title = "Fibers-Vendor Measured Attenuation";
c_vendorAttenuation = new TCanvas("c_vendorAttenuation",Title,X,Y,Width,Height);
h_vendorAttenuation->Draw();
outFileName = makeGraphicsFileName(Title);
if(printGraphicsFile != 0) c_vendorAttenuation ->Print(outFileName);
X += DelX; Y += DelY;
Title = "Fibers-Fibers-Vendor Measured Attenuation Voltage";
c_vendorAttenuationVoltage = new TCanvas("c_vendorAttenuationVoltage",Title,X,Y,Width,Height);
h_vendorAttenuationVoltage->Draw();
outFileName = makeGraphicsFileName(Title);
if(printGraphicsFile != 0) c_vendorAttenuationVoltage ->Print(outFileName);
X += DelX; Y += DelY;
Title = "Fibers-Vendor Measured Fiber Eccentricity";
c_vendorEccentricity = new TCanvas("c_vendorEccentricity",Title,X,Y,Width,Height);
h_vendorEccentricity->Draw();
outFileName = makeGraphicsFileName(Title);
if(printGraphicsFile != 0) c_vendorEccentricity ->Print(outFileName);

//
X += DelX; Y += DelY;
Title = "Fibers-Vendor Measured Fiber Small Diameter";
c_vendorDiameter15 = new TCanvas("c_vendorDiameter15",Title,X,Y,Width,Height);
h_vendorDiameter15->Draw();
outFileName = makeGraphicsFileName(Title);
if(printGraphicsFile != 0) c_vendorDiameter15 ->Print(outFileName);

X += DelX; Y += DelY;
Title = "Fibers-Vendor Measured Fiber Large Diameter";
c_vendorDiameter18 = new TCanvas("c_vendorDiameter18",Title,X,Y,Width,Height);
h_vendorDiameter18->Draw();
outFileName = makeGraphicsFileName(Title);
if(printGraphicsFile != 0) c_vendorDiameter18 ->Print(outFileName);
}

// ######################################################################
//   This group of methods reads in the trees for the
//   Locally Measured quantities
// ----------------------------------------------------------------------
//  Plot the vendor measurements
void fiberTest::choosePlotLocal(void){
  readLocalMeasurements(inputRootFile);
  bookLocalHistograms();  if(cmjDiag > 0){
    cout <<"**fiberTest::fillCurrentHistogram... fiberId = "<<string_fiberId<<endl;
    cout <<"**fiberTest::fillCurrentHistogram... fiberProductionDate = "<<string_fiberProductionDate<<endl;
    cout <<"**fiberTest::fillCurrentHistogram... fiberComment = "<<string_fiberComment<<endl;
    cout <<"**fiberTest::fillCurrentHistogram... fiberVendorDiameter = "<< fiberVendorDiameter << endl;
    cout <<"**fiberTest::fillCurrentHistogram... fiberVendorSigma    = "<< fiberVendorSigma << endl;
    cout <<"**fiberTest::fillCurrentHistogram... fiberVendorAttenaution   = "<< fiberVendorAttenaution << endl;
    cout <<"**fiberTest::fillCurrentHistogram... fiberVendorAttenuationVoltage = "<< fiberVendorAttenuationVoltage << endl;
    cout <<"**fiberTest::fillCurrentHistogram... fiberVendorEccentricity   = "<< fiberVendorEccentricity << endl;
    }
  setLocalBranches();
  fillLocalHistograms();
  drawLocalCanvas();
  return;
}
// ----------------------------------------------------------------------
//   Read root tree with local measurements
void fiberTest::readLocalMeasurements(TFile *tempInputRootFile){
  // Get the first root tree for the events with a light source
  myTree2 = new TTree("myTree2","Fiber Local Measurements");
  myTree2 = (TTree*)inputRootFile->Get("Local Fiber Measurement");
}
// -----------------------------------------------------------------------
//  Define the histograms.... for tree 2 (local measurements)
void fiberTest::bookLocalHistograms(void){
  if(cmjDiag != 0) cout<<"**fiberTest::booklocalHistograms"<<endl;
  // local Measurements
  h_localDiameter = new TH1F("h_localDiameter","Locally Measured Fiber Diameter",nDiameterLocal,lowDiameterLocal,hiDiameterLocal);
  h_localDiameter->GetXaxis()->SetTitle("Diameter (#mu m)");
  h_localDiameter->GetXaxis()->SetLabelSize(0.02);
  TGaxis *myX4 = (TGaxis*) h_localDiameter->GetXaxis();
  myX4->SetMaxDigits(1);
  h_localDiameter->SetFillColor(kRed);
  
  h_localDiameter15 = new TH1F("h_localDiameter15","Locally Measured Fiber Diameter 15",nDiameterLocal15,lowDiameterLocal15,hiDiameterLocal15);
  h_localDiameter15->GetXaxis()->SetTitle("Diameter (#mu m)");
  h_localDiameter15->GetXaxis()->SetLabelSize(0.02);
  TGaxis *myX40 = (TGaxis*) h_localDiameter15->GetXaxis();
  myX40->SetMaxDigits(1);
  h_localDiameter15->SetFillColor(kRed);
  
  h_localDiameter18 = new TH1F("h_localDiameter18","Locally Measured Fiber Diameter 18",nDiameterLocal18,lowDiameterLocal18,hiDiameterLocal18);
  h_localDiameter18->GetXaxis()->SetTitle("Diameter (#mu m)");
  h_localDiameter18->GetXaxis()->SetLabelSize(0.02);
  TGaxis *myX41 = (TGaxis*) h_localDiameter18->GetXaxis();
  myX41->SetMaxDigits(1);
  h_localDiameter18->SetFillColor(kRed);
  
  //h_localAttenuation18 = new TH1F("h_localAttenuation","Locally Measured Fiber Attenuation Length",nDiameterLocal18,lowDiameterLocal18,hiDiameterLocal18);
  //h_localAttenuation18->GetXaxis()->SetTitle("Fiber Attenuation(mm)");
  //TGaxis *myX41 = (TGaxis*) h_localAttenuation18->GetXaxis();
  //myX401->SetMaxDigits(1);
  //h_localAttenuation18->SetFillColor(kRed);
  return;
}
// -----------------------------------------------------------------------
//  Define Branches....
void fiberTest::setLocalBranches(void){
  if(cmjDiag != 0)cout<<"**fiberTest::setVendorBranches"<<endl;
  //  cmj2022Jan25
  // For python3 ... read character arrays stored as std::vector<std::string>
  vect_fiberIdLocal = 0; branch_vect_fiberIdLocal = 0;
  myTree2->SetBranchAddress("fiberId",&vect_fiberIdLocal,&branch_vect_fiberIdLocal);
  vect_fiberTestDateLocal = 0; branch_vect_fiberTestDateLocal = 0;
  myTree2->SetBranchAddress("testDate",&vect_fiberTestDateLocal,&branch_vect_fiberTestDateLocal);
  vect_fiberCommentLocal = 0; branch_vect_fiberCommentLocal = 0;
  myTree2->SetBranchAddress("comment",&vect_fiberCommentLocal,&branch_vect_fiberCommentLocal);
  // cmj2022Jan25
  myTree2->SetBranchAddress("LocalDiameter",&fiberLocalDiameter);
  myTree2->SetBranchAddress("LocalAttenuation",&fiberLocalAttenuation);
  if(cmjDiag > 3) myTree2->Print();
}
// -----------------------------------------------------------------------
//  fill the histograms.... from tree 2 (local measurements)
//  The way PyRoot works to save a tree is to save lists...
//	This is effectively one entry with arrays that are the 
//	size of the number of leaves.....

void fiberTest::fillLocalHistograms(void){
  if(cmjDiag != 0) cout<<"**fiberTest::fillLocalHistograms"<<endl;
  if(cmjDiag > 2) myTree2->Scan();
  Int_t maxEntries = (Int_t) myTree2->GetEntries();
  if(cmjDiag != 0) cout<<"**fiberTest::fillLocalHistogram maxEntries = "<<maxEntries<<endl;
  for(Int_t m = 0; m < maxEntries; m++){
  myTree2->GetEntry(m);
  //  cmj2022Jan25
  //  Load the strings variable for selection of database keys... First get the branch_vect_fiberComment
  Long64_t tentry = myTree2->LoadTree(m);
  branch_vect_fiberIdLocal->GetEntry(tentry);
  branch_vect_fiberTestDateLocal->GetEntry(tentry);
  branch_vect_fiberCommentLocal->GetEntry(tentry);
  //  Load the strings variable for selection of database keys... second get the contents
  string_fiberIdLocal = vect_fiberIdLocal->at(m);
  string_fiberTestDateLocal = vect_fiberTestDateLocal->at(m);
  string_fiberCommentLocal = vect_fiberCommentLocal->at(m);
  // cmj2022Jan25
  h_localDiameter->Fill(fiberLocalDiameter);
  h_localDiameter15->Fill(fiberLocalDiameter);
  h_localDiameter18->Fill(fiberLocalDiameter);
  //h_localAttenuation->Fill(fiberLocalAttenuation);
    if(cmjDiag > 0){
    cout <<"**fiberTest::fillLocalHistogram... fiberId = "<<string_fiberIdLocal<<endl;
    cout <<"**fiberTest::fillLocalHistogram... fiberProductionDate = "<<string_fiberTestDateLocal<<endl;
    cout <<"**fiberTest::fillLocalHistogram... fiberComment = "<<string_fiberCommentLocal<<endl;
    cout <<"**fiberTest::fillLocalHistogram... fiberLocalDiameter = "<< fiberLocalDiameter << endl;
    cout <<"**fiberTest::fillLocalHistogram... fiberLocalAttenuation    = "<< fiberLocalAttenuation << endl;
    }
  }
}
// -----------------------------------------------------------------------
//  Draw the histograms.... from tree 2 (local measurements)
void fiberTest::drawLocalCanvas(void){
Int_t X0   = 50;  Int_t Y0   = 50;
Int_t DelX = 10;  Int_t DelY = 10;
Int_t X; Int_t Y;
Int_t Width = 600; Int_t Height = 600;
X = X0; Y = Y0;
TString Title;
TString outFileName;
// 
X += DelX; Y += DelY;
Title = "Fibers-Local Measured Fiber Diameter";
c_localDiameter = new TCanvas("c_localDiameter",Title,X,Y,Width,Height);
h_localDiameter->Draw();
outFileName = makeGraphicsFileName(Title);
if(printGraphicsFile != 0) c_localDiameter ->Print(outFileName);

X += DelX; Y += DelY;
Title = "Fibers-Local Measured Fiber Diameter 15";
c_localDiameter15 = new TCanvas("c_localDiameter15",Title,X,Y,Width,Height);
h_localDiameter15->Draw();
outFileName = makeGraphicsFileName(Title);
if(printGraphicsFile != 0) c_localDiameter15 ->Print(outFileName);

X += DelX; Y += DelY;
Title = "Fibers-Local Measured Fiber Diameter 18";
c_localDiameter18 = new TCanvas("c_localDiameter18",Title,X,Y,Width,Height);
h_localDiameter18->Draw();
outFileName = makeGraphicsFileName(Title);
if(printGraphicsFile != 0) c_localDiameter18 ->Print(outFileName);


// += DelX; Y += DelY;

//X += DelX; Y += DelY;
//Title = "Fibers-Local Measured Attenuation";
//c_localAttenuation = new TCanvas("c_localAttenuation",Title,X,Y,Width,Height);
//h_localAttenuation->Draw();
//outFileName = makeGraphicsFileName(Title);
//if(printGraphicsFile != 0) c_localAttenuation ->Print(outFileName);

return;
}
//
// ######################################################################
//   This group of methods reads in the trees for the
//   Attenuation (ADC counts) vs Wavelength of Light
// ---------------------------------------------------------------------
//  Driving program that calls all of the methods needed
void fiberTest::choosePlotLambdaVsWavelength(void){
  readLambdavsAtten(inputRootFile);
}
// ----------------------------------------------------------------------
//   Read in all trees... select the ones containing the locally measured
//   Attenuation (ADC count) vs Wavelength (measured at UVa)
void fiberTest::readLambdavsAtten(TFile *tempInputRootFile){
   //bookAttenVsLength_local();
   // read name of the root tree
  mg_attenVsLambda = new TMultiGraph();
  mg_attenVsLambda->SetTitle("Fiber-Attenuation vs Wavelength: All Fibers; Wavelength (nm); Attenuation Length (m)");
  TIter nextkey(tempInputRootFile->GetListOfKeys());
  Int_t m = 0;
  while( TKey *key = (TKey *)nextkey() ){
    TObject *obj = key->ReadObj();
    if(obj->IsA()->InheritsFrom(TTree::Class())){
    TTree *Tree_data = 0;
    Tree_data = (TTree*) obj;
    //Tree_data->Print();
    TString tempName = Tree_data->GetName();
    TString tempFiberName = tempName(24,10);
    //cout << "(readLambdavsAtten) Tree Number = "<< m << " tree name = "<<Tree_data->GetName() << "abbrv name = xx"<< tempName(0,22)<<"xx"<<" tempFiberName = xx"<< tempFiberName <<"xx"<<std::endl;
    m++;
    if(tempName(0,23)=="Fiber-WavelengthVsAtten") {
      cout << "(readLambdavsAtten) Tree Number = "<< m << " tree name = "<<Tree_data->GetName() << "abbrv name = xx"<< tempName(0,22)<<"xx"<<" tempFiberName = xx"<< tempFiberName <<"xx"<<std::endl;
      plotLambdavsAtten(m,tempFiberName,Tree_data);
    }
    delete Tree_data;
    Tree_data = 0;
    }
  }
  drawLambdavsAtten();
}
// -----------------------------------------------------------------------
//   Get Branches and and fill TGraphs for Attenuation vs Wavelength
void fiberTest::plotLambdavsAtten(Int_t m5,TString fiberName,TTree *currentTree){
  TString tempTreeNumber = "";
  TString preTitle = "Fibers-Attenuation vs. Wavelength";
  TString titleString;
  Int_t numberOfPoints;
  Float_t lambda[100], length[100];
  currentTree->SetBranchAddress("numberOfEntries",&numberOfPoints);
  currentTree->SetBranchAddress("wavelength",lambda);
  currentTree->SetBranchAddress("attenuation",length);
  Int_t mmm = (Int_t) currentTree->GetEntries();
  std::cout<<" number entries = "<< mmm << std::endl;
  for (Int_t m = 0; m < mmm; m++) {
    currentTree->GetEntry(m);
    std::cout<<" numberOfPoints = "<< numberOfPoints<<std::endl;
    gr_array_attenVsLambda[m5] = new TGraph(numberOfPoints,lambda,length);
    tempTreeNumber=Form("%d",m5);
    if(fiberName == "swhite-tes") continue;
    TString tCanvasName = "c_attenVsLambda_"+tempTreeNumber;
    c_array_attenVsLambda[m5] = new TCanvas(tCanvasName,"Fibers-Attenuation vs. Wavelength",200,200,500,500);
    gr_array_attenVsLambda[m5]->SetMarkerStyle(20);
    gr_array_attenVsLambda[m5]->SetMarkerColor(4);
    gr_array_attenVsLambda[m5]->SetMarkerSize(1.0);
    titleString = preTitle+" "+fiberName;
    gr_array_attenVsLambda[m5]->SetTitle(titleString);
    gr_array_attenVsLambda[m5]->GetXaxis()->SetTitle("Wavelength (nm)");
    gr_array_attenVsLambda[m5]->GetYaxis()->SetTitle("Attenuation Length (m)");
    gr_array_attenVsLambda[m5]->GetXaxis()->SetTitleSize(0.03);
    gr_array_attenVsLambda[m5]->GetYaxis()->SetTitleSize(0.03);
    gr_array_attenVsLambda[m5]->GetXaxis()->SetLabelSize(0.03);
    gr_array_attenVsLambda[m5]->GetYaxis()->SetLabelSize(0.02);
    gr_array_attenVsLambda[m5]->GetYaxis()->SetTitleOffset(1.5);
    gr_array_attenVsLambda[m5]->Draw("AP");
    TString outFileName = makeGraphicsFileName(titleString);
    if(_printGraphics == 1) c_array_attenVsLambda[m5]->Print(outFileName);
    mg_attenVsLambda->Add(gr_array_attenVsLambda[m5],"AP");  // Add all attenuation vs wavelength onto one graph
  }
}
// ----------------------------------------------------------------------
void fiberTest::drawLambdavsAtten(void){
  //  Plot all attenuation vs wavelengths onto one graph
  TString preTitle = "Attenuation vs. Wavelength";
  TString titleString = preTitle+" All Fibers";
  c_mg_attenVsLambda = new TCanvas("c_mg_attenVsLambda","Fibers-Attenuation vs. Wavelength: All Fibers",200,200,500,500);
  mg_attenVsLambda->Draw("AP");
  TString outFileName = makeGraphicsFileName(titleString);
  if(_printGraphics == 1) c_mg_attenVsLambda->Print(outFileName);
}
// ######################################################################
//   This group of methods reads in the trees for the locally measured
//   Attenuation (ADC counts) vs Fiber length (measured at UVa)
// ----------------------------------------------------------------------
//   Method to call all of the needed methods
void fiberTest::choosePlotAttenVsFiberLength_local(void){
  readAttenVsLengthTree_local(inputRootFile);
}
// ----------------------------------------------------------------------
//   Read in all trees... select the ones containing the locally measured
//   Attenuation (ADC count) vs Fiber length (measured at UVa)
void fiberTest::readAttenVsLengthTree_local(TFile *tempInputRootFile){
  maxFibersLocal = 0;
  bookAttenVsLength_local();
  mg_attenVsLength_local = new TMultiGraph();
  mg_attenVsLength_local->SetTitle("Fibers-Attenuation (ADC Count) vs FiberLength (local): All Fibers; Fiber Length (cm); Attenuation (ADC count)");
  // read name of the root tree
  TIter nextkey(tempInputRootFile->GetListOfKeys());
  Int_t m = 0;
  while( TKey *key = (TKey *)nextkey() ){
    TObject *obj = key->ReadObj();
    if(obj->IsA()->InheritsFrom(TTree::Class())){
    TTree *Tree_data = 0;
    Tree_data = (TTree*) obj;
    //Tree_data->Print();
    TString tempName = Tree_data->GetName();
    TString tempFiberName = tempName(25,10);
    //cout << "(readAttenVsLengthTree_local) Tree Number = "<< m << " tree name = "<<Tree_data->GetName() << "abbrv name = xx"<< tempName(0,22)<<"xx"<<" tempFiberName = xx"<< tempFiberName <<"xx"<<std::endl;
    m++;
    if(tempName(0,24)=="Fiber-LocalAttenVsLength") {
      cout << "(readAttenVsLengthTree_local) Tree Number = "<< m << " tree name = "<<Tree_data->GetName() << "abbrv name = xx"<< tempName(0,22)<<"xx"<<" tempFiberName = xx"<< tempFiberName <<"xx"<<std::endl;
      plotAttenVsLength_local(m,maxFibersLocal,tempFiberName,Tree_data);
      maxFibersLocal++;
    }    
    delete Tree_data;
    Tree_data = 0; // cmj2022Jan26
    }
  }
  fillAttenVsLength_local();
  drawAttenVsLength_local();
}
// -----------------------------------------------------------------------
//   Get branches and fill histograms for locally measured attenuation
//   ADC counts vs Fiber length (measured at UVa)
void fiberTest::plotAttenVsLength_local(Int_t m5,Int_t fiberIndex, TString fiberName,TTree *currentTree){
  TString tempTreeNumber = "";
  TString preTitle = "Fibers-Attenuation ADC Count Vs FiberLength (local)";
  TString titleString;
  Int_t numberOfPoints;
  Float_t _length[100], _adcCount[100];
  if(currentTree == NULL){
    std::cout<<"fiberTest::plotAttenVsLength_local... Tree = "<<currentTree->GetName()<<" Empty "<<std::endl;
    return;
  }
  currentTree->SetBranchAddress("numberOfEntries",&numberOfPoints);
  currentTree->SetBranchAddress("fiberLength",_length);
  currentTree->SetBranchAddress("adcCount",_adcCount);
  Int_t mmm = (Int_t) currentTree->GetEntries();
  std::cout<<" number entries = "<< mmm << std::endl;
  Double_t slope, err_slope;
  for (Int_t m = 0; m < mmm; m++) {
    currentTree->GetEntry(m);
    if(fiberName == "swhite-tes") continue;
    std::cout<<" numberOfPoints = "<< numberOfPoints<<std::endl;
    gr_array_attenVsLength_local[m5] = new TGraph(numberOfPoints,_length,_adcCount);
    tempTreeNumber=Form("%d",m5);
    TString tCanvasName = "c_attenVsLambda_"+tempTreeNumber;
    c_array_attenVsLength_local[m5] = new TCanvas(tCanvasName,"Fibers-Attenuation vs. Fiber Length (local)",200,200,500,500);
    gr_array_attenVsLength_local[m5]->SetMarkerStyle(20);
    gr_array_attenVsLength_local[m5]->SetMarkerColor(6);
    gr_array_attenVsLength_local[m5]->SetMarkerSize(1.0);
    titleString = preTitle+" "+fiberName+" (local)";
    gr_array_attenVsLength_local[m5]->SetTitle(titleString);
    gr_array_attenVsLength_local[m5]->GetXaxis()->SetTitle("Fiber Length (cm)");
    gr_array_attenVsLength_local[m5]->GetYaxis()->SetTitle("ADC (counts)");
    gr_array_attenVsLength_local[m5]->GetXaxis()->SetTitleSize(0.03);
    gr_array_attenVsLength_local[m5]->GetYaxis()->SetTitleSize(0.03);
    gr_array_attenVsLength_local[m5]->GetXaxis()->SetLabelSize(0.03);
    gr_array_attenVsLength_local[m5]->GetYaxis()->SetLabelSize(0.02);
    gr_array_attenVsLength_local[m5]->GetYaxis()->SetTitleOffset(1.5);

    
    gr_array_attenVsLength_local[m5]->Fit("expo");
    TF1 *fit = gr_array_attenVsLength_local[m5]->GetFunction("expo");
    slope = fit->GetParameter(1);
    err_slope = fit->GetParError(1);
    stored_slope_attenVsLength_local[fiberIndex] = slope;
    std::cout<<"Fit Results:  m5 = "<<m5<<" "<<tCanvasName<<" slope = "<<slope<<" +/- "<<err_slope<<" || fiberIndex = "<<fiberIndex<<" stored_slope_attenVsLength = "<<stored_slope_attenVsLength_vendor[fiberIndex]<<std::endl;
    gr_array_attenVsLength_local[m5]->Draw("AP");
    c_array_attenVsLength_local[m5]->SetLogy();
    TString outFileName = makeGraphicsFileName(titleString);
    if(_printGraphics == 1) c_array_attenVsLength_local[m5]->Print(outFileName);
    
    gr_array_attenVsLength_local_noFit[m5] = new TGraph(numberOfPoints,_length,_adcCount);
    gr_array_attenVsLength_local_noFit[m5]->SetMarkerStyle(20);
    gr_array_attenVsLength_local_noFit[m5]->SetMarkerColor(6);
    gr_array_attenVsLength_local_noFit[m5]->SetMarkerSize(1.0);
    titleString = preTitle+" "+fiberName+" (local)";
    gr_array_attenVsLength_local_noFit[m5]->SetTitle(titleString);
    gr_array_attenVsLength_local_noFit[m5]->GetXaxis()->SetTitle("Fiber Length (cm)");
    gr_array_attenVsLength_local_noFit[m5]->GetYaxis()->SetTitle("ADC (counts)");
    gr_array_attenVsLength_local_noFit[m5]->GetXaxis()->SetTitleSize(0.03);
    gr_array_attenVsLength_local_noFit[m5]->GetYaxis()->SetTitleSize(0.03);
    gr_array_attenVsLength_local_noFit[m5]->GetXaxis()->SetLabelSize(0.03);
    gr_array_attenVsLength_local_noFit[m5]->GetYaxis()->SetLabelSize(0.02);
    gr_array_attenVsLength_local_noFit[m5]->GetYaxis()->SetTitleOffset(1.5);
    mg_attenVsLength_local->Add(gr_array_attenVsLength_local_noFit[m5],"AP");  // Add all attenuation vs wavelength onto one graph
  }
}
// -----------------------------------------------------------------------
//  Book histograms for all local attenuation vs length
void fiberTest::bookAttenVsLength_local(void){
  //  Define histogram for all of the fits to the slope
  TString preTitle = "Fibers-Attenuation ADCCount Vs FiberLength (local)";
  TString titleString = preTitle+" Attn. vs Fiber Length: Exp Slope from Fit (local)";
  h_slope_attenVsLength_local = new TH1F("h_slope_attenVsLength_local",titleString,nAttenVsLengthSlope,lowAttenVsLengthSlope,hiAttenVsLengthSlope);
  h_slope_attenVsLength_local->GetXaxis()->SetTitle("Slope from fit");
  h_slope_attenVsLength_local->GetXaxis()->SetTitleSize(0.03);
  h_slope_attenVsLength_local->SetFillColor(kRed);
}
// -----------------------------------------------------------------------
//  fill histograms for all local attenuation vs lengthttenuation (Volts 
void fiberTest::fillAttenVsLength_local(void){
      //  Fill this histogram
  for(Int_t nnn = 0; nnn<maxFibersLocal; nnn++){
    h_slope_attenVsLength_local->Fill(Float_t(stored_slope_attenVsLength_local[nnn]));
    //std::cout<<" fiberTest::fillAttenVsLength_local:: nnn = "<<nnn<<" slope = "<<Float_t(stored_slope_attenVsLength_local[nnn])<<std::endl;
  }
}
// -----------------------------------------------------------------------
//  fill histograms for all local attenuation vs length
void fiberTest::drawAttenVsLength_local(void){  
  //  Draw Canvas
  TString preTitle = "Fibers-Attenuation ADCCount Vs FiberLength (local)";
  TString titleString = preTitle+" Attenuation vs. Fiber Length Exp Slope Fit";
  c_slope_attenVsLength_local = new TCanvas("c_slope_attenVsLength_local","Local Atten. vs Fiber Length: Fit to Exp slope",200,200,550,550);
  h_slope_attenVsLength_local->Draw();
  TString outFileName = makeGraphicsFileName(titleString);
  if(_printGraphics == 1) c_slope_attenVsLength_local->Print(outFileName);
   //  Plot all attenuation vs fiber length onto one graph
  c_mg_attenVsLength_local = new TCanvas("c_mg_attenVsLength_local","ADC Counts (local) vs Length: All Fibers",200,200,500,500);
  titleString = preTitle+" All Fibers";
  mg_attenVsLength_local->Draw("AP");
  c_mg_attenVsLength_local->SetLogy();
  outFileName = makeGraphicsFileName(titleString);
  if(_printGraphics == 1) c_mg_attenVsLength_local->Print(outFileName);
}
//
// ######################################################################
//   This group of methods reads in the trees for the Vendor measured
//   Attenuation (Volts (mv)) vs Fiber length (measured by Hamamatsu)
// ----------------------------------------------------------------------
//   Method to call all of the needed methods
void fiberTest::choosePlotAttenVsFiberLength_vendor(void){
  readAttenVsLengthTree_vendor(inputRootFile);
}
// ----------------------------------------------------------------------
//   Read in all trees... select the ones containing the Vendor measured
//   Attenuation (Volts (mv)) vs Fiber length (measured by Hamamatsu)
// =================================================================================
void fiberTest::readAttenVsLengthTree_vendor(TFile *inputRootFile){
    // Combine all attenuation vs wavelength measurments onto one graph 
  maxFibersVendor = 0;
  bookAttenVsLength_vendor();
  mg_attenVsLength_vendor = new TMultiGraph();
  mg_attenVsLength_vendor->SetTitle("Fibers-Attenuation vs Wavelength (vendor): All Fibers; Fiber Length (cm); Attenuation (Volts (mV))");
  // read name of the root tree
  TIter nextkey(inputRootFile->GetListOfKeys());
  Int_t m = 0;
  while( TKey *key = (TKey *)nextkey() ){
    TObject *obj = key->ReadObj();
    if(obj->IsA()->InheritsFrom(TTree::Class())){
    TTree *Tree_data = 0;
    Tree_data = (TTree*) obj;
    //Tree_data->Print();
    TString tempName = Tree_data->GetName();
    TString tempFiberName = tempName(26,10);
    //cout << "(readAttenVsLengthTree_vendor) Tree Number = "<< m << " tree name = "<<Tree_data->GetName() << "abbrv name = xx"<< tempName(0,22)<<"xx"<<" tempFiberName = xx"<< tempFiberName <<"xx"<<std::endl;
    m++;
    cout<<"(readAttenVsLengthTree_vendor) tempName(0,25) = "<<tempName(0,25)<<endl;
    if(tempName(0,25)=="Fiber-VendorAttenVsLength") {
      Int_t numberOfPoints;
      if(tempName.Contains("M1804")){
	cout << "(readAttenVsLengthTree_vendor) Tree Number = "<< m << " tree name = "<<Tree_data->GetName() << "abbrv name = xx"<< tempName(0,22)<<"xx"<<" tempFiberName = xx"<< tempFiberName <<"xx"<<std::endl;
        plotAttenVsLength_vendor(m,maxFibersVendor,tempFiberName,Tree_data);
        maxFibersVendor++;
        }
    }
    delete Tree_data;
    Tree_data = 0;  // cmj2022Jun26
    }
  }
  fillAttenVsLength_vendor();
  drawAttenVsLength_vendor();
}
// -----------------------------------------------------------------------
void fiberTest::plotAttenVsLength_vendor(Int_t m5,Int_t fiberIndex, TString fiberName,TTree *currentTree){
  TString tempTreeNumber = "";
  TString preTitle = "Fibers-Attenuation Voltage Vs FiberLength (vendor)";
  TString titleString;
  Int_t numberOfPoints;
  Float_t _length[100], _adcCount[100];
  TString tempString1 = currentTree->GetName();
  TBranch *branch_numberOfPoints = 0;
  if(tempString1.Contains("M1804")){
    currentTree->SetBranchAddress("VnumberOfEntries",&numberOfPoints,&branch_numberOfPoints);  // cmj2022Jan27... somehow a "V" was prepended for these...
  }
  else if(tempString1.Contains("M2103")){
    currentTree->SetBranchAddress("numberOfEntries",&numberOfPoints,&branch_numberOfPoints);  // cmj2022Jan27... but no "V" prepend here!
  }
  else{ return;}
  currentTree->SetBranchAddress("fiberLength",_length);
  currentTree->SetBranchAddress("adcCount",_adcCount);
  Int_t mmm = (Int_t) currentTree->GetEntries();
  std::cout<<" number entries = "<< mmm << std::endl;
  Double_t slope, err_slope;
  for (Int_t m = 0; m < mmm; m++) {
    currentTree->GetEntry(m);
    if(fiberName == "swhite-tes") continue;
    std::cout<<" numberOfPoints = "<< numberOfPoints<<std::endl;
    gr_array_attenVsLength_vendor[m5] = new TGraph(numberOfPoints,_length,_adcCount);
    tempTreeNumber=Form("%d",m5);
    TString tCanvasName = "c_attenVsLambda_"+tempTreeNumber;
    c_array_attenVsLength_vendor[m5] = new TCanvas(tCanvasName,"Attenuation vs. Fiber Length (Vendor)",200,200,500,500);
    gr_array_attenVsLength_vendor[m5]->SetMarkerStyle(20);
    gr_array_attenVsLength_vendor[m5]->SetMarkerColor(3);
    gr_array_attenVsLength_vendor[m5]->SetMarkerSize(1.0);
    titleString = preTitle+" "+fiberName+" (vendor)";
    gr_array_attenVsLength_vendor[m5]->SetTitle(titleString);
    gr_array_attenVsLength_vendor[m5]->GetXaxis()->SetTitle("Fiber Length (cm)");
    gr_array_attenVsLength_vendor[m5]->GetYaxis()->SetTitle("Voltage (mV)");
    gr_array_attenVsLength_vendor[m5]->GetXaxis()->SetTitleSize(0.03);
    gr_array_attenVsLength_vendor[m5]->GetYaxis()->SetTitleSize(0.03);
    gr_array_attenVsLength_vendor[m5]->GetXaxis()->SetLabelSize(0.03);
    gr_array_attenVsLength_vendor[m5]->GetYaxis()->SetLabelSize(0.02);
    gr_array_attenVsLength_vendor[m5]->GetYaxis()->SetTitleOffset(1.5);

    
    gr_array_attenVsLength_vendor[m5]->Fit("expo");
    TF1 *fit = gr_array_attenVsLength_vendor[m5]->GetFunction("expo");
    slope = fit->GetParameter(1);
    err_slope = fit->GetParError(1);
    stored_slope_attenVsLength_vendor[fiberIndex] = slope;
    std::cout<<"Fit Results:  m5 = "<<m5<<" "<<tCanvasName<<" slope = "<<slope<<" +/- "<<err_slope<<" || fiberIndex = "<<fiberIndex<<" stored_slope_attenVsLength_vendor = "<<stored_slope_attenVsLength_vendor[fiberIndex]<<std::endl;
    gr_array_attenVsLength_vendor[m5]->Draw("AP");
    c_array_attenVsLength_vendor[m5]->SetLogy();
    TString outFileName = makeGraphicsFileName(titleString);
    if(_printGraphics == 1) c_array_attenVsLength_vendor[m5]->Print(outFileName);
    
    gr_array_attenVsLength_vendor_noFit[m5] = new TGraph(numberOfPoints,_length,_adcCount);
    gr_array_attenVsLength_vendor_noFit[m5]->SetMarkerStyle(20);
    gr_array_attenVsLength_vendor_noFit[m5]->SetMarkerColor(3);
    gr_array_attenVsLength_vendor_noFit[m5]->SetMarkerSize(1.0);
    titleString = preTitle+" "+fiberName+" (vendor)";
    gr_array_attenVsLength_vendor_noFit[m5]->SetTitle(titleString);
    gr_array_attenVsLength_vendor_noFit[m5]->GetXaxis()->SetTitle("Fiber Length (cm)");
    gr_array_attenVsLength_vendor_noFit[m5]->GetYaxis()->SetTitle("Voltage (mV)");
    gr_array_attenVsLength_vendor_noFit[m5]->GetXaxis()->SetTitleSize(0.03);
    gr_array_attenVsLength_vendor_noFit[m5]->GetYaxis()->SetTitleSize(0.03);
    gr_array_attenVsLength_vendor_noFit[m5]->GetXaxis()->SetLabelSize(0.03);
    gr_array_attenVsLength_vendor_noFit[m5]->GetYaxis()->SetLabelSize(0.02);
    gr_array_attenVsLength_vendor_noFit[m5]->GetYaxis()->SetTitleOffset(1.5);
    mg_attenVsLength_vendor->Add(gr_array_attenVsLength_vendor_noFit[m5],"AP");  // Add all attenuation vs wavelength onto one graph
  }

}
// -----------------------------------------------------------------------
//  Book histograms for all vendor attenuation vs length
void fiberTest::bookAttenVsLength_vendor(void){
  //  Define histogram for all of the fits to the slope
  TString preTitle = "Fibers-Attenuation Voltage Vs FiberLength (vendor)";
  TString titleString = preTitle+" Attn. vs Fiber Length: Exp Slope from Fit";
  h_slope_attenVsLength_vendor = new TH1F("h_slope_attenVsLength_vendor",titleString,nAttenVsLengthSlope,lowAttenVsLengthSlope,hiAttenVsLengthSlope);
  h_slope_attenVsLength_vendor->GetXaxis()->SetTitle("Slope from fit");
  h_slope_attenVsLength_vendor->GetXaxis()->SetTitleSize(0.03);
  h_slope_attenVsLength_vendor->SetFillColor(kGreen);
}
// -----------------------------------------------------------------------
//  fill histograms for all vendor attenuation vs length
void fiberTest::fillAttenVsLength_vendor(void){
      //  Fill this histogram
  for(Int_t nnn = 0; nnn<maxFibersVendor; nnn++){
    h_slope_attenVsLength_vendor->Fill(Float_t(stored_slope_attenVsLength_vendor[nnn]));
    //std::cout<<" fiberTest::fillAttenVsLength_vendor:: nnn = "<<nnn<<" slope = "<<Float_t(stored_slope_attenVsLength_vendor[nnn])<<std::endl;
  }
}
// -----------------------------------------------------------------------
//  fill histograms for all vendor attenuation vs length
void fiberTest::drawAttenVsLength_vendor(void){
  //  Draw Canvas
  TString preTitle = "Fibers-Attenuation Voltage Vs FiberLength (vendor)";
  TString titleString = preTitle+" Att. vs. Fiber Length Exp Slope Fit (Vendor)";
  c_slope_attenVsLength_vendor = new TCanvas("c_slope_attenVsLength_vendor","vendor Atten. vs Fiber Length: Fit to Exp slope",200,200,550,550);
  h_slope_attenVsLength_vendor->Draw();
  TString outFileName = makeGraphicsFileName(titleString);
  if(_printGraphics == 1) c_slope_attenVsLength_vendor->Print(outFileName);
  //  Plot all attenuation vs fiber length onto one graph
  c_mg_attenVsLength_vendor = new TCanvas("c_mg_attenVsLength_vendor","ADC Counts (vendor) vs Length: All Fibers",200,200,500,500);
  titleString = preTitle+" All Fibers";
  mg_attenVsLength_vendor->Draw("AP");
  c_mg_attenVsLength_vendor->SetLogy();
  outFileName = makeGraphicsFileName(titleString);
  if(_printGraphics == 1) c_mg_attenVsLength_vendor->Print(outFileName);
}

// =================================================================================

//--------------------------------------------------------
//	Construct graphics file name for a plot....
TString fiberTest::makeGraphicsFileName(TString _tempString){
_tempString = _tempString.ReplaceAll(".","_");
_tempString = _tempString.ReplaceAll(",","_");
_tempString = _tempString.ReplaceAll("=","_");
_tempString = _tempString.ReplaceAll(":","_");
TString _graphicsFileName;
_graphicsFileName=graphicsFileDir + _tempString.ReplaceAll(" ","") + graphicsFileType;
cout << "Save graphics file: " << _graphicsFileName << endl;
return _graphicsFileName;
}
//--------------------------------------------------------
void fiberTest::enableGraphics(Int_t temp){_printGraphics = temp;}
//--------------------------------------------------------
void fiberTest::setGraphicsDirectoryName(TString temp){graphicsFileDir  = temp;} 

// #####################################################################
// #####################################################################
// #####################################################################
// #####################################################################
// #####################################################################
//  --------------------------------------------------------------------
//  Run macro here....
void analyzeFibers(TString inFile = "FiberRootHistograms_2018Sep7_10_15_18_.root", Int_t tempPrint = 0, Int_t debugLevel = 0){
fiberTest *myFiber = new fiberTest(inFile,tempPrint, debugLevel);
//	Signal... Current with dicounters expoxed to light source.
//   Plot one set of histograms at a time! (Too many histograms.... too little memory!)
std::cout<<"...analyzeFibers... open root file: "<<inFile<<std::endl<<std::endl;
std::cout<<"...analyzeFibers... Plot one set of histograms at a time!"<<std::endl;
std::cout<<"...analyzeFibers... (Too many histograms, too little memory)"<<std::endl;
// 
std::cout<<"...analyzeFibers... 1 = Plot Local Test Measurements (default)"<<std::endl;
std::cout<<"...analyzeFibers... 2 = Plot Vendor Test Measurements"<<std::endl;
std::cout<<"...analyzeFibers... 3 = Plot Local Attenuation vs Wavelength"<<std::endl;
std::cout<<"...analyzeFibers... 4 = Plot Local Attenuation vs Length"<<std::endl;
std::cout<<"...analyzeFibers... 5 = Plot Vendor Attenuation vs Length"<<std::endl;
std::cout<<"...analyzeFibers... Enter Choice "<<std::endl;
Int_t imode;
std::cin>>imode;
if(imode == 1) myFiber -> choosePlotLocal();
else if(imode == 2){ myFiber -> choosePlotVendor(); std::cout<<" analyzeFibers:: imode = "<<imode<<" choosePlotVendor()"<<std::endl;}
else if(imode == 3) {myFiber -> choosePlotLambdaVsWavelength(); std::cout<<" analyzeFibers:: imode = "<<imode<<" choosePlotLambdaVsWavelength"<<std::endl;}
else if(imode == 4) {myFiber ->  choosePlotAttenVsFiberLength_local(); std::cout<<" analyzeFibers:: imode = "<<imode<<" choosePlotAttenVsFiberLength_local"<<std::endl;}
else if(imode == 5) {myFiber ->  choosePlotAttenVsFiberLength_vendor(); std::cout<<" analyzeFibers:: imode = "<<imode<<" choosePlotAttenVsFiberLength_vendor"<<std::endl;}
else {myFiber -> choosePlotVendor(); std::cout<<" analyzeFibers:: imode = "<<imode<<" choosePlotVendor()"<<std::endl;}
}

