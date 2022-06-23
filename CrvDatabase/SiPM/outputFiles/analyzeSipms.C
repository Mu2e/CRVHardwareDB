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
//
//  To print out diagnostics...
//	> root
//	.x analyzeSipmsVendor.C("rootFileName.root",1,debugLevel)  // debug level = 1, 2, 3, 4
//
// Modified by cmj2022Jan24... changed how character strings are read from the
//                             root tree.  The python3 version of pyroot saves
//                             character strings as std:vector<std::string>.  This
//                             required changes to read in this structure.
// Modified by cmj2022Jun3.... Remove the arrayis of TGraphs....
// Modified by cmj2022Jun3.... Change the way that the I vs V curves for all Sipms
//                             are plotted. Instead use a T2HF scatter plot.  Then
//                             use a color option to plot the  frequency of hits in a bin.
// Modified by cmj2022Jun6.... Add time on X axis date plots... See https://root.cern/doc/master/timeonaxis2_8C.html
//                             for full instructions.... 
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
//-------------------------------------------------------
//	Declare the Class!
class sipmVendorTest{
  public:
  sipmVendorTest(TString tempInFile, Int_t printGraphics, Int_t tempDebug);
  ~sipmVendorTest();
  void setBranches(void);
  void bookHistograms(void);
  void fillHistograms(void);
  void drawCanvas(void);
  void plotIvsV(Int_t,TString,TTree *currentTree);
  void drawIvsVCanvas(void);
  private:
    TString makeGraphicsFileName(TString _tempString);
    TFile *inputRootFile;
    TTree *myTree1;   // TTree to hold the Sipm currents with light source....
    TTree *myTree2;   // TTree to hold the dark current tree
    TString GraphicsFileType;
    TString Title;
    TString Name;
        // Control features of class...
    Int_t cmjDiag;
    Int_t printGraphicsFile;
    TString outDirectory;
    // I vs V....analyzeSipms-2022Jun2.C
    TH2F *h2_IvsV;
    TCanvas *c_h2_IvsV;
    // Combine all data points onto one plot
    TMultiGraph *mg_IvsV;
    TCanvas *c_mg_IvsV;
    Int_t numberOfIvsVSipms;
    // Define histograms
    Int_t numberOfSipmsTested, numberOfSipmsLocalTest, numberOfSipmsVendorTest;
    TH1F *h_biasVoltage_vendor, *h_darkCount_vendor,*h_gain_vendor, *h_temperature_vendor;
    TH1F *h_breakDownVoltage_vendor, *h_darkCountRate_vendor, *h_currentVoltageCond_vendor, *h_xTalk_vendor, *h_ledResponse_vendor;
    TH1F *h_biasVoltage_local, *h_darkCount_local,*h_gain_local, *h_temperature_local;
    TH1F *h_breakDownVoltage_local, *h_darkCountRate_local, *h_currentVoltageCond_local, *h_xTalk_local, *h_ledResponse_local;
    TH1F *h_testDate_local;  // All test dates
    // Define Bins
    Int_t nVoltBin; Double_t lowVoltBin; Double_t hiVoltBin;
    Int_t nDarkCountBin; Double_t lowDarkCountBin; Double_t hiDarkCountBin;
    Int_t nGainBin; Double_t lowGainBin; Double_t hiGainBin;
    Int_t nTempBin; Double_t lowTempBin; Double_t hiTempBin;
    Int_t nBreakDownVoltageBin; Double_t lowBreakDownVoltageBin; Double_t hiBreakDownVoltageBin;
    Int_t nDarkCountRateBin;	Double_t lowDarkCountRateBin;	Double_t hiDarkCountRateBin;
    Int_t nCurrentVoltageCondBin; Double_t lowCurrentVoltageCondBin; Double_t hiCurrentVoltageCondBin;
    Int_t nXTalkBin;	Double_t lowXTalkBin; 	Double_t hiXTalkBin;
    Int_t nLedResponseBin;	Double_t lowLedResponseBin; Double_t hiLedResponseBin;
    Int_t nDates; TDatime tDatime_tOffset; TDatime tDatime_tLow; TDatime tDatime_tHi;  Int_t tOffset; Int_t tLow; Int_t tHi;
    // Define Canvases
    TCanvas *c_biasVoltage_vendor, *c_darkCount_vendor,*c_gain_vendor,*c_temperature_vendor;
    TCanvas *c_breakDownVoltage_vendor, *c_darkCountRate_vendor, *c_currentVoltageCond_vendor, *c_xTalk_vendor, *c_ledResponse_vendor;
    TCanvas *c_biasVoltage_local, *c_darkCount_local,*c_gain_local,*c_temperature_local;
    TCanvas *c_breakDownVoltage_local, *c_darkCountRate_local, *c_currentVoltageCond_local, *c_xTalk_local, *c_ledResponse_local;
    TCanvas *c_testDate_local;
    //
    //  cmj2022Jan25
    //  For python 3... character arrays are stored as std::vector<std::string>
    std::vector<std::string> *vect_sipmNumber;       TBranch *branch_vect_sipmNumber; //cmj2022Jan25 
    std::vector<std::string> *vect_testDate;         TBranch *branch_vect_testDate; //cmj2022Jan25 
    std::vector<std::string> *vect_testType;         TBranch *branch_vect_testType; //cmj2022Jan25 
    std::vector<std::string> *vect_workerBarCode;    TBranch *branch_vect_workerBarCode; //cmj2022Jan25 
    std::vector<std::string> *vect_workStationBarCode;    TBranch *branch_vect_workStationBarCode; //cmj2022Jan25 
    std::vector<std::string> *vect_dataFileLocation; TBranch *branch_vect_dataFileLocation; //cmj2022Jan25 
    std::vector<std::string> *vect_dataFileName;     TBranch *branch_vect_dataFileName; //cmj2022Jan25 
    TString string_sipmNumber, string_testDate, string_testType, string_workerBarCode;
    TString string_workStationBarCode, string_dataFileLocation, string_dataFileName;
    //  cmj2022Jan25
    Float_t biasVoltage, darkCount, gain, temperature;
    Float_t breakDownVoltage, darkCountRate, currentVoltageCond, xTalk, ledResponse;

};
// ------------------------drawCountCanvas(void)------------------------------
//  Implement the Class!
// ------------------------------------------------------
//  Constructor
  sipmVendorTest::sipmVendorTest(TString tempInFile,Int_t printGraphics = 0, Int_t debug = 0){
  outDirectory = "graphicsAllSipms2022Jun8/";
  cmjDiag = debug;
    if(cmjDiag != 0) {
    cout <<"**sipmVendorTest::sipmVendorTest.. turn on debug: debug level = "<<cmjDiag<<endl;
    cout<<"**sipmVendorTest::sipmVendorTest: start"<<endl;
    }
  printGraphicsFile = printGraphics;
  GraphicsFileType = ".png";
    if(printGraphicsFile != 0) cout<<"**sipmVendorTest::sipmVendorTest... print graphics file" << endl;
  gStyle -> SetOptStat("nemruoi");  // Print statistitics... page 32 root manual.. reset defaul
  gStyle -> SetOptDate(1);       // Print date on plots
  gStyle -> SetOptFit(1111); // show parameters, errors and chi2... page 72 root manual
  cout<<"..sipmVendorTest::sipmVendorTest: tempInputFileName = "<<tempInFile<<endl;
  inputRootFile = new TFile(tempInFile);
  // Get the first root tree for the events with a light source
  myTree1 = new TTree("myTree1","Sipm Counts from NIU Tests");
  //myTree1 = (TTree*)inputRootFile->Get("DiCounterSignal/diCounterSignal");
  myTree1 = (TTree*)inputRootFile->Get("AllSipmMeasurements");
  if(cmjDiag > 3 ) myTree1->Scan();
  if(cmjDiag > 2) cout << "Current Root Directory "<< (gDirectory->GetPath()) << endl;
  nVoltBin= 100; lowVoltBin=50.0; hiVoltBin=60.0;
  nDarkCountBin = 100; lowDarkCountBin=0.00; hiDarkCountBin=0.1;
  nGainBin = 100;  lowGainBin = 0.0; hiGainBin = 20.0;
  nTempBin = 15;  lowTempBin = 15.0; hiTempBin = 31.0;
  nBreakDownVoltageBin = 100;		lowBreakDownVoltageBin = 50.0;	hiBreakDownVoltageBin = 60.0;
  nDarkCountRateBin = 100;		lowDarkCountRateBin = 0.0;	hiDarkCountRateBin = 300.0;
  nCurrentVoltageCondBin = 100;		lowCurrentVoltageCondBin = 0.0;	hiCurrentVoltageCondBin = 200.0;
  nXTalkBin = 100;			lowXTalkBin = 0.0;		hiXTalkBin = 10.0;
  nLedResponseBin = 100;		lowLedResponseBin = 0.0 ;	hiLedResponseBin = 10.0;
  //
  //   Set bins for X axis date histograms.
  nDates = 300;
  tDatime_tOffset.Set(2022,6,1,0,0,0);    // This is the offset time to define time axis... 
  tOffset = tDatime_tOffset.Convert();    // Convert thye TDatime object to an integer
                                          // Set this one large in format: Y/m/d hh:mm:ss
                                          // This offset is used for all histogrammed date calculations.
  tDatime_tLow.Set(2018,9,1,0,0,0);       // Set the low bin date (September 9, 2018)
  tLow = tDatime_tLow.Convert()-tOffset;  // calculate the low bin as an integer relative to offset
  tDatime_tHi.Set(2020,1,1,0,0,0);        // Set the high bin date (June 6, 2022)
  tHi = tDatime_tHi.Convert()-tOffset;    // calculate the hig bin as an integer relative to offset
  // 
  numberOfIvsVSipms = 0;
  TString tempFiberName = "";
  mg_IvsV = new TMultiGraph();
  mg_IvsV->SetTitle("Current vs Voltage: All SiPMs; Voltage (Volts); Current (#mu Amps)");
  h2_IvsV = new TH2F("h2_IvsV","I vs V - All Sipms",100,49.0,65.0,1000,-0.1,10.0); // cmj2022Jun3
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
    tempFiberName=Form("%d",m);
    //cout << "sipmVendorTest:: m = "<<m<<" tempName = "<<tempName<<std::endl;
    //cout << "sipmVendorTest:: Tree Number = "<< m << " tree name = "<<Tree_data->GetName() << " abbrv name = "<< tempName(0,8)<<" tempFiberName = "<< tempFiberName <<std::endl;
    //cout << "sipmVendorTest::tempName(0,9) = "<<tempName(0,9)<<endl;
    m++;
    if(tempName(0,9)=="SipmIvsV-") {
      plotIvsV(m,tempFiberName,Tree_data);
      numberOfIvsVSipms++;
    }
    delete Tree_data;
    //if(m > 2) break;  // cmj2022Jun3... for testing purposes 
    }
  }
  cout<<"Number of Sipms with IvsV test "<<numberOfIvsVSipms<<endl;
  drawIvsVCanvas();
}
// ------------------------------------------------------
//  Destructor
  sipmVendorTest::~sipmVendorTest(){ 
  if(cmjDiag != 0) cout<<"**sipmVendorTest::~sipmVendorTest: end"<<endl;
  return;
}
// -----------------------------------------------------------------------
void sipmVendorTest::plotIvsV(Int_t m5,TString fiberName,TTree *currentTree){
  //td::cout << "sipmVendorTest::plotIvsV... enter"<<std::endl;
  TString tempTreeNumber = "";
  TString preTitle = "Sipms-Current vs Voltage";
  TString titleString;
  Int_t numberOfPoints;
  Float_t current[100], voltage[100];
  currentTree->SetBranchAddress("numberOfEntries",&numberOfPoints);
  currentTree->SetBranchAddress("sipm_current",current);
  currentTree->SetBranchAddress("sipm_voltage",voltage);
  Int_t mmm = (Int_t) currentTree->GetEntries();
  //std::cout<<" number entries = "<< mmm << std::endl;
  TGraph *gr_IvsV = 0;
  for (Int_t m = 0; m < mmm; m++) {
    currentTree->GetEntry(m);
    //std::cout<<" numberOfPoints = "<< numberOfPoints<<std::endl;
    delete gr_IvsV;
    gr_IvsV = new TGraph(numberOfPoints,voltage,current);
    for(int nn = 0; nn < numberOfPoints; nn++){
      h2_IvsV->Fill(voltage[nn],current[nn]);
    }
    gr_IvsV->SetMarkerStyle(20);
    gr_IvsV->SetMarkerColor(3);
    gr_IvsV->SetMarkerSize(1.0);
    titleString = preTitle+" "+fiberName;
    //std::cout<<"sipmVendorTest::plotIvsV... tCanvasName = " <<tCanvasName << std::endl;
    //std::cout<<"sipmVendorTest::plotIvsV... titleString = " <<titleString << std::endl;
    gr_IvsV->SetTitle(titleString);
    gr_IvsV->GetXaxis()->SetTitle("Voltage (Volts)");
    gr_IvsV->GetYaxis()->SetTitle("Current (#mu Amps)");
    gr_IvsV->GetXaxis()->SetTitleSize(0.03);
    gr_IvsV->GetYaxis()->SetTitleSize(0.03);
    gr_IvsV->GetXaxis()->SetLabelSize(0.03);
    gr_IvsV->GetYaxis()->SetLabelSize(0.02);
    gr_IvsV->GetYaxis()->SetTitleOffset(1.5);
    mg_IvsV->Add(gr_IvsV,"AP");  // Add all attenuation vs wavelength onto one graph
  }
  //std::cout << "sipmVendorTest::plotIvsV... exit"<<std::endl;
}
// -----------------------------------------------------------------------
void sipmVendorTest::drawIvsVCanvas(void){
  //  Plot all aI vs V as a TGraph
  TString preTitle = "Sipms-Current vs Voltage";
  TString titleString = preTitle+" All SiPMs";
  c_mg_IvsV = new TCanvas("c_mg_IvsV","Current vs Voltage (all SiPMs)",200,200,500,500);
  mg_IvsV->Draw("AP");
  c_mg_IvsV->SetLogy();
  c_mg_IvsV->Modified();
  mg_IvsV->SetMinimum(1.0e-5);
  mg_IvsV->SetMaximum(1.0e3);
  TString outFileName = makeGraphicsFileName(titleString);
  if(printGraphicsFile == 1) c_mg_IvsV->Print(outFileName);
  // Plot all I vs V as a T2HF
  titleString = preTitle+" All SiPMs Scatter Plot";
  c_h2_IvsV = new TCanvas("c_h2_IvsV",titleString,200,210,800,510);
  gStyle->SetPalette(kRainBow);
  h2_IvsV->Draw("colz");
  h2_IvsV->SetMinimum(1.0);
  h2_IvsV->SetMaximum(1000.0);
  h2_IvsV->GetYaxis()->SetLimits(1.0e-2,10.0);
  //
  //h2_IvsV->SetTitle(titleString);
  h2_IvsV->GetXaxis()->SetTitle("Voltage (Volts)");
  h2_IvsV->GetYaxis()->SetTitle("Current (#mu Amps)");
  h2_IvsV->GetXaxis()->SetTitleSize(0.03);
  h2_IvsV->GetYaxis()->SetTitleSize(0.03);
  h2_IvsV->GetXaxis()->SetLabelSize(0.03);
  h2_IvsV->GetYaxis()->SetLabelSize(0.02);
  h2_IvsV->GetYaxis()->SetTitleOffset(1.5);
  //
  TString tempString = "Number of Sipms in plot = ";
  TString tempStringNumber = "";
  tempStringNumber = Form("%d",numberOfIvsVSipms);
  tempString += tempStringNumber;
  TLatex *myText = new TLatex();
  myText->SetTextSize(0.03);
  myText->DrawLatex(50.0,0.02,tempString);
  //
  c_h2_IvsV->Update();
  TPaveStats* statBox = (TPaveStats*)h2_IvsV->FindObject("stats");
  statBox->SetX1(60.5);
  statBox->SetX2(65.0);
  c_h2_IvsV->SetLogy();
  outFileName = makeGraphicsFileName(titleString);
  if(printGraphicsFile == 1) c_h2_IvsV->Print(outFileName);
return;
}
// -----------------------------------------------------------------------
//  Define the histograms.... for tree 1 (signal)
void sipmVendorTest::bookHistograms(void){
  if(cmjDiag != 0) cout<<"**sipmVendorTest::bookCurrentHistograms"<<endl;
  h_biasVoltage_vendor = new TH1F("h_biasVoltage_vendor","Sipm Bias Voltage (Vendor)",nVoltBin,lowVoltBin,hiVoltBin);
  h_biasVoltage_vendor->GetXaxis()->SetTitle("Bias Voltage (Volts)");
  h_biasVoltage_vendor->GetXaxis()->SetTitleSize(0.03);
  h_biasVoltage_vendor->SetFillColor(kRed);
  h_darkCount_vendor = new TH1F("h_darkCount_vendor","Sipm Dark Count (Vendor)",nDarkCountBin,lowDarkCountBin,hiDarkCountBin);
  h_darkCount_vendor->GetXaxis()->SetTitle("Counts");
  h_darkCount_vendor->GetXaxis()->SetTitleSize(0.03);
  h_darkCount_vendor->SetFillColor(kMagenta);
  h_gain_vendor = new TH1F("h_gain_vendor","Sipm Gain (Vendor)",nGainBin,lowGainBin,hiGainBin);
  h_gain_vendor->GetXaxis()->SetTitle("Counts");
  h_gain_vendor->GetXaxis()->SetTitleSize(0.03);
  h_gain_vendor->SetFillColor(kBlue);
  h_temperature_vendor = new TH1F("h_temperature_vendor","Sipm Temperature (Vendor)",nTempBin,lowTempBin,hiTempBin);
  h_temperature_vendor->GetXaxis()->SetTitle("Temperature (^oC)");
  h_temperature_vendor->GetXaxis()->SetTitleSize(0.03);
  h_temperature_vendor->SetFillColor(kGreen);
  h_breakDownVoltage_vendor = new TH1F("h_breakDownVoltage_vendor","Breakdown Voltage (Vendor)",nBreakDownVoltageBin,lowBreakDownVoltageBin,hiBreakDownVoltageBin);
  h_breakDownVoltage_vendor->GetXaxis()->SetTitle("Breakdown Voltage (Volts)");
  h_breakDownVoltage_vendor->GetXaxis()->SetTitleSize(0.03);
  h_breakDownVoltage_vendor->SetFillColor(kOrange);
  h_darkCountRate_vendor = new TH1F("h_darkCountRate_vendor","Dark Count Rate (Vendor)",nDarkCountRateBin,lowDarkCountRateBin,hiDarkCountRateBin);
  h_darkCountRate_vendor->GetXaxis()->SetTitle("Darkcount Rate");
  h_darkCountRate_vendor->GetXaxis()->SetTitleSize(0.03);
  h_darkCountRate_vendor->SetFillColor(kBlack);
  h_xTalk_vendor = new TH1F("h_xTalk_vendor","Cross Talk (Vendor)",nXTalkBin,lowXTalkBin,hiXTalkBin);
  h_xTalk_vendor->GetXaxis()->SetTitle("Darkcount Rate");
  h_xTalk_vendor->GetXaxis()->SetTitleSize(0.03);
  h_xTalk_vendor->SetFillColor(kBlue);
  h_ledResponse_vendor = new TH1F("h_ledResponse_vendor","LED Response (Vendor)",nLedResponseBin,lowLedResponseBin,hiLedResponseBin);
  //
  //  Setup the local testing date histogram
  nDates = 100;
  gStyle->SetTimeOffset(tOffset);
  h_testDate_local = new TH1F("h_testDate_local","Local Test Dates",nDates,tLow,tHi);
    h_testDate_local->SetFillColor(kBlack);
  h_testDate_local->GetXaxis()->SetTimeDisplay(1);
  h_testDate_local->GetXaxis()->SetTimeFormat("%Y/%m/%d");
  h_testDate_local->GetXaxis()->SetLabelSize(0.02);
  //
  h_biasVoltage_local = new TH1F("h_biasVoltage_local","Sipm Bias Voltage (Local)",nVoltBin,lowVoltBin,hiVoltBin);
  h_biasVoltage_local->GetXaxis()->SetTitle("Bias Voltage (Volts)");
  h_biasVoltage_local->GetXaxis()->SetTitleSize(0.03);
  h_biasVoltage_local->SetFillColor(kRed);
  h_darkCount_local = new TH1F("h_darkCount_local","Sipm Dark Count (Local)",nDarkCountBin,lowDarkCountBin,hiDarkCountBin);
  h_darkCount_local->GetXaxis()->SetTitle("Counts");
  h_darkCount_local->GetXaxis()->SetTitleSize(0.03);
  h_darkCount_local->SetFillColor(kMagenta);
  h_gain_local = new TH1F("h_gain_local","Sipm Gain (Local)",nGainBin,lowGainBin,hiGainBin);
  h_gain_local->GetXaxis()->SetTitle("Counts");
  h_gain_local->GetXaxis()->SetTitleSize(0.03);
  h_gain_local->SetFillColor(kBlue);
  h_temperature_local = new TH1F("h_temperature_local","Sipm Temperature (Local)",nTempBin,lowTempBin,hiTempBin);
  h_temperature_local->GetXaxis()->SetTitle("Temperature (^{o}C)");
  h_temperature_local->GetXaxis()->SetTitleSize(0.03);
  h_temperature_local->SetFillColor(kGreen);
  h_breakDownVoltage_local = new TH1F("h_breakDownVoltage_local","Breakdown Voltage (Local)",nBreakDownVoltageBin,lowBreakDownVoltageBin,hiBreakDownVoltageBin);
  h_breakDownVoltage_local->GetXaxis()->SetTitle("Breakdown Voltage (Volts)");
  h_breakDownVoltage_local->GetXaxis()->SetTitleSize(0.03);
  h_breakDownVoltage_local->SetFillColor(kOrange);
  h_darkCountRate_local = new TH1F("h_darkCountRate_local","Dark Count Rate (Local)",nDarkCountRateBin,lowDarkCountRateBin,hiDarkCountRateBin);
  h_darkCountRate_local->GetXaxis()->SetTitle("Darkcount Rate");
  h_darkCountRate_local->GetXaxis()->SetTitleSize(0.03);
  h_darkCountRate_local->SetFillColor(kBlack);
  h_xTalk_local = new TH1F("h_xTalk_local","Cross Talk (Local)",nXTalkBin,lowXTalkBin,hiXTalkBin);
  h_xTalk_local->GetXaxis()->SetTitle("Darkcount Rate");
  h_xTalk_local->GetXaxis()->SetTitleSize(0.03);
  h_xTalk_local->SetFillColor(kBlue);
  h_ledResponse_local = new TH1F("h_ledResponse_local","LED Response (Local)",nLedResponseBin,lowLedResponseBin,hiLedResponseBin);
}
// -----------------------------------------------------------------------
//  Define Branches.... from tree 1 (signal)
void sipmVendorTest::setBranches(void){
  if(cmjDiag != 0)cout<<"**sipmVendorTest::setCurrentBranches"<<endl;
  //
  vect_sipmNumber = 0; branch_vect_sipmNumber = 0;
  myTree1->SetBranchAddress("sipmId",&vect_sipmNumber,&branch_vect_sipmNumber);
  vect_testDate = 0; branch_vect_testDate = 0;
  myTree1->SetBranchAddress("sipmTestDate",&vect_testDate,&branch_vect_testDate);
  vect_testType = 0; branch_vect_testType = 0;
  myTree1->SetBranchAddress("sipmTestType",&vect_testType,&branch_vect_testType);
  vect_workerBarCode = 0; branch_vect_workerBarCode = 0;
  myTree1->SetBranchAddress("workerBarCode",&vect_workerBarCode,&branch_vect_workerBarCode);
  vect_workStationBarCode = 0; branch_vect_workStationBarCode = 0;
  myTree1->SetBranchAddress("workstationBarCode",&vect_workStationBarCode,&branch_vect_workStationBarCode);
  vect_dataFileLocation = 0; branch_vect_dataFileLocation = 0;
  myTree1->SetBranchAddress("dataFileLocation",&vect_dataFileLocation,&branch_vect_dataFileLocation);
  vect_dataFileName = 0; branch_vect_dataFileName = 0;
  myTree1->SetBranchAddress("dataFileName",&vect_dataFileName,&branch_vect_dataFileName);
  //cmj2022Jan25
  myTree1->SetBranchAddress("biasVoltage",&biasVoltage);
  myTree1->SetBranchAddress("darkCount",&darkCount);
  myTree1->SetBranchAddress("gain",&gain);
  myTree1->SetBranchAddress("temperature",&temperature);
  myTree1->SetBranchAddress("breakDownVolt",&breakDownVoltage);
  myTree1->SetBranchAddress("darkCountRate",&darkCountRate);
  myTree1->SetBranchAddress("currentVsVoltCond",&currentVoltageCond);
  myTree1->SetBranchAddress("xTalk",&xTalk);
  myTree1->SetBranchAddress("ledResponse",&ledResponse);
  if(cmjDiag > 3) myTree1->Print();
}
// -----------------------------------------------------------------------
//  fill the histograms.... from tree 1 (signal)
//  The way PyRoot works to save a tree is to save lists...
//	This is effectively one entry with arrays that are the 
//	size of the number of leaves.....
void sipmVendorTest::fillHistograms(void){
  numberOfSipmsTested = 0;
  numberOfSipmsLocalTest = 0; 
  numberOfSipmsVendorTest = 0;
  //Int_t tallyTestDate = 0;
  //TString oldTestDate;
  Int_t Time;
  TString sVendor = "vendor";
  TString sMeasured = "measured";
  TDatime tDatime_TestTime;
  if(cmjDiag != 0) cout<<"**sipmVendorTest::fillCurrentHistograms"<<endl;
  if(cmjDiag > 2) myTree1->Scan();
  Int_t maxEntries = (Int_t) myTree1->GetEntries();
  if(cmjDiag != 0) cout<<"**sipmVendorTest::fillCurrentHistogram maxEntries = "<<maxEntries<<endl;
  //for(Int_t m = 0; m < 10000; m++){
  for(Int_t m = 0; m < maxEntries; m++){
   if(m < 10) std::cout<<" sipmVendorTest::fillHistograms... testType = "<<string_testType<<std::endl;
   myTree1->GetEntry(m);
   // Report progess... periodically....
     if(m < 10){std::cout<<"sipmVendorTest::fillHistograms... m = "<<m<<std::endl;}
     else if(m % 100 == 0 && m <1000){std::cout<<"sipmVendorTest::fillHistograms... m = "<<m<<std::endl;}
     else if(m % 1000 == 0 && m <10000){std::cout<<"sipmVendorTest::fillHistograms... m = "<<m<<std::endl;}
     else if (m % 10000 == 0){std::cout<<"sipmVendorTest::fillHistograms... m = "<<m<<std::endl;}
  //  cmj2022Jan25
  //  Load the strings variable for selection of database keys... First get the branch_vect_fiberComment
   Long64_t tentry = myTree1->LoadTree(m);
   //if( m < 2) myTree1->Scan();
   branch_vect_sipmNumber->GetEntry(tentry);
   branch_vect_testDate->GetEntry(tentry);
   branch_vect_testType->GetEntry(tentry);
   branch_vect_workerBarCode->GetEntry(tentry);
   branch_vect_workStationBarCode->GetEntry(tentry);
   branch_vect_dataFileLocation->GetEntry(tentry);
   branch_vect_dataFileName->GetEntry(tentry);
     // Load the string variables for selection of database keys... Second get the contents
   string_sipmNumber = vect_sipmNumber->at(m);
   //cout<<" ...SipmNumber = "<<string_sipmNumber<<endl;;
   string_testDate = vect_testDate->at(m);
   string_testType = vect_testType->at(m);
   string_workerBarCode = vect_workerBarCode->at(m);
   string_workStationBarCode = vect_workStationBarCode->at(m);
   string_dataFileLocation = vect_dataFileLocation->at(m);
   string_dataFileName = vect_dataFileName->at(m);
   // cmj2022jan25
   if(string_testType==sVendor){
   tDatime_TestTime.Set(string_testDate);
   Time = tDatime_TestTime.Convert()-tOffset;  // Local Test Date
   h_testDate_local->Fill((Float_t) Time);     // Local Test Date
   h_biasVoltage_vendor->Fill(biasVoltage);
   h_darkCount_vendor->Fill(darkCount);
   h_gain_vendor->Fill(gain);
   h_temperature_vendor->Fill(temperature);
   h_breakDownVoltage_vendor->Fill(breakDownVoltage);
   h_darkCountRate_vendor->Fill(darkCountRate);
   //h_currentVoltageCond_vendor->Fill(currentVoltageCond);
   h_xTalk_vendor->Fill(xTalk);
   h_ledResponse_vendor->Fill(ledResponse);
   numberOfSipmsVendorTest++;
   }
  // 
   if(string_testType==sMeasured){
   h_biasVoltage_local->Fill(biasVoltage);
   h_darkCount_local->Fill(darkCount);
   h_gain_local->Fill(gain);
   h_temperature_local->Fill(temperature);
   h_breakDownVoltage_local->Fill(breakDownVoltage);
   h_darkCountRate_local->Fill(darkCountRate);
   //h_currentVoltageCond_local->Fill(currentVoltageCond);
   h_xTalk_local->Fill(xTalk);
   h_ledResponse_local->Fill(ledResponse);
   numberOfSipmsLocalTest++;
   }
     if(cmjDiag > 0){
    cout<<" ---------------- Event: "<<m<<" ------------------------ "<< endl;
    cout <<"**sipmVendorTest::fillHistograms... simpNumber  = "<<string_sipmNumber<<endl;
    cout <<"**sipmVendorTest::fillHistograms... sipmTestDate = "<<string_testDate<<endl;
    cout <<"**sipmVendorTest::fillHistograms... TestType     = "<<string_testType<<endl;
    cout <<"**sipmVendorTest::fillHistograms... WorkerBarCode = "<< string_workerBarCode<< endl;
    cout <<"**sipmVendorTest::fillHistograms... WorkStationBarCode    = "<< string_workStationBarCode << endl;
    cout <<"**sipmVendorTest::fillHistograms... DataFileName     = "<< string_dataFileName << endl;
    cout <<"**sipmVendorTest::fillHistograms... DataFileLocation = "<< string_dataFileLocation << endl;
    cout <<"**sipmVendorTest::fillHistograms... biasVoltage      = "<< biasVoltage << endl;
    cout <<"**sipmVendorTest::fillHistograms... darkCount        = "<< darkCount<< endl;
    cout <<"**sipmVendorTest::fillHistograms... gain             = "<< gain << endl;
    cout <<"**sipmVendorTest::fillHistograms... temperature      = "<< temperature << endl;
    cout <<"**sipmVendorTest::fillHistograms... breakDownVoltage = "<< breakDownVoltage << endl;
    cout <<"**sipmVendorTest::fillHistograms... darkCountRate    = "<< darkCountRate << endl;
    cout <<"**sipmVendorTest::fillHistograms... xTalk            = "<< xTalk << endl;
    cout <<"**sipmVendorTest::fillHistograms... ledResponse      = "<< ledResponse << endl;
    }
  }
  //myTree1->Show();
}
// -----------------------------------------------------------------------
//  Draw the histograms.... from tree 1 (signal)
void sipmVendorTest::drawCanvas(void){
  Int_t X0   = 50;  Int_t Y0   = 50;

Int_t DelX = 10;  Int_t DelY = 10;
Int_t X; Int_t Y;
Int_t Width = 600; Int_t Height = 600;
X = X0; Y = Y0;
TDatime *myTime = new TDatime();
Char_t space[2] = " ";
Char_t underline[2] = "_";
TString myString = "";
TString myStringNumber;
TString myOutFileName;
//
TString theTime = myTime->AsString();
myString = "Number of Sipms, Vendor = ";
myStringNumber = Form("%d",numberOfSipmsVendorTest);
myString += myStringNumber;
TLatex *myLatex = new TLatex();
myLatex->SetTextSize(0.03);
//
if(cmjDiag != 0) cout << "**sipmVendorTest::drawDarkCurrentCanvas: time = "<< theTime.ReplaceAll(" ","_") <<endl;
c_biasVoltage_vendor = new TCanvas("c_biasVoltage_vendor","Sipm Bias Voltage (Vendor)",X,Y,Width,Height);
h_biasVoltage_vendor->Draw();
  myOutFileName = makeGraphicsFileName("Sipms-BiasVoltageVendor_");
  if(printGraphicsFile != 0) c_biasVoltage_vendor->Print(myOutFileName);
X += DelX; Y += DelY;
c_darkCount_vendor = new TCanvas("c_darkCount_vendor","Sipm Vendor Count (Vendor)",X,Y,Width,Height);
h_darkCount_vendor->Draw();
  myLatex->DrawLatex(0.05,5000.0,myString);
  myOutFileName = makeGraphicsFileName("Sipms-DarkCountVendor_");
  if(printGraphicsFile != 0) c_darkCount_vendor->Print(myOutFileName);
X += DelX; Y += DelY;
c_gain_vendor = new TCanvas("c_gain_vendor","Sipm Gain (Vendor)",X,Y,Width,Height);
c_gain_vendor->SetLogy();
h_gain_vendor->Draw();
  myLatex->DrawLatex(4.0,40.0,myString);
  myOutFileName = makeGraphicsFileName("Sipms-Gain (Vendor)_");
  if(printGraphicsFile != 0) c_gain_vendor->Print(myOutFileName);
X += DelX; Y += DelY;
c_temperature_vendor = new TCanvas("c_temperature_vendor","Sipm  TestTemperature (Vendor)",X,Y,Width,Height);
h_temperature_vendor->Draw();
myLatex->DrawLatex(15.5,10000.0,myString);
  myOutFileName = makeGraphicsFileName("Sipms-TestTemperatureVendor_");
  if(printGraphicsFile != 0) c_temperature_vendor->Print(myOutFileName);
X += DelX; Y += DelY;
c_breakDownVoltage_vendor = new TCanvas("c_breakDownVoltage_vendor","Sipm Breakdown Voltage",X,Y,Width,Height);
h_breakDownVoltage_vendor->Draw();
  myLatex->DrawLatex(51,0.4,myString);
  myOutFileName = makeGraphicsFileName("Sipms-BreakDownVoltage(Vendor)_");
  if(printGraphicsFile != 0) c_breakDownVoltage_vendor->Print(myOutFileName);
X += DelX; Y += DelY;
c_darkCountRate_vendor = new TCanvas("c_darkCountRate_vendor","Sipm  Dark Count Rate (Vendor)",X,Y,Width,Height);
h_darkCountRate_vendor->Draw();
  myLatex->DrawLatex(51,0.4,myString);
  myOutFileName = makeGraphicsFileName("Sipms-DarkCountRateVendor_");
  if(printGraphicsFile != 0) c_darkCountRate_vendor->Print(myOutFileName);
  /*
X += DelX; Y += DelY;
c_currentVoltageCond_vendor = new TCanvas("c_currentVoltageCond_vendor","Sipm Current vs Voltage Cond (Vendor)",X,Y,Width,Height);
h_currentVoltageCond_vendor->Draw();
  if(printGraphicsFile != 0) c_currentVoltageCond_vendor->Print(outDirectory+"Sipms-CurrentVsVoltCondVendor_"+theTime+".png");
*/
 

X += DelX; Y += DelY;
c_xTalk_vendor = new TCanvas("c_xTalk_vendor","Sipm Cross Talk (Vendor)",X,Y,Width,Height);
h_xTalk_vendor->Draw();
  myLatex->DrawLatex(1,0.4,myString);
  myOutFileName = makeGraphicsFileName("Sipms-CrossTalkVendor_");
  //if(printGraphicsFile != 0) c_xTalk_vendor->Print(outDirectory+"Sipms-CrossTalkVendor_"+theTime+".png");
  if(printGraphicsFile != 0) c_xTalk_vendor->Print(myOutFileName);
X += DelX; Y += DelY;
c_ledResponse_vendor = new TCanvas("c_ledResponse_vendor","Sipm Led Response (Vendor)",X,Y,Width,Height);
h_ledResponse_vendor->Draw();
  myLatex->DrawLatex(1,0.4,myString);
  myOutFileName = makeGraphicsFileName("Sipms-LedResponseVendor_");
  if(printGraphicsFile != 0) c_ledResponse_vendor->Print(myOutFileName);
//
// --- Local Measurement Results...
//
myString = "Number of Sipms, Local = ";
myStringNumber = Form("%d",numberOfSipmsLocalTest);
myString += myStringNumber;
//
X += DelX; Y += DelY;
c_testDate_local = new TCanvas("c_testDate_local","Local Test Dates",X,Y,Width,Height);
h_testDate_local->Draw();
  myLatex->DrawLatex(1,0.4,myString);
  c_testDate_local->Modified();
  myOutFileName = makeGraphicsFileName("Sipms-LocalTestDate_");
  if(printGraphicsFile != 0) c_testDate_local->Print(myOutFileName);
//
//
c_biasVoltage_local = new TCanvas("c_biasVoltage_local","Sipm Bias Voltage (Local)",X,Y,Width,Height);
h_biasVoltage_local->Draw();
  myLatex->DrawLatex(54,1200.0,myString);
  myOutFileName = makeGraphicsFileName("Sipms-BiasVoltagelocal_");
  if(printGraphicsFile != 0) c_biasVoltage_local->Print(myOutFileName);
X += DelX; Y += DelY;
c_darkCount_local = new TCanvas("c_darkCount_local","Sipm local Count (Local)",X,Y,Width,Height);
h_darkCount_local->Draw();
  myLatex->DrawLatex(0.05,600.0,myString);
  myOutFileName = makeGraphicsFileName("Sipms-DarkCountLocal_");
  if(printGraphicsFile != 0) c_darkCount_local->Print(myOutFileName);
X += DelX; Y += DelY;
c_gain_local = new TCanvas("c_gain_local","Sipm Gain (local)",X,Y,Width,Height);
c_gain_local->SetLogy();
h_gain_local->Draw();
  myLatex->DrawLatex(2.0,600.0,myString);
  myOutFileName = makeGraphicsFileName("Sipms-Gain (Local)_");
  if(printGraphicsFile != 0) c_gain_local->Print(myOutFileName);
X += DelX; Y += DelY;
c_temperature_local = new TCanvas("c_temperature_local","Sipm  TestTemperature (Local)",X,Y,Width,Height);
h_temperature_local->Draw();
  myLatex->DrawLatex(15.5,5000.0,myString);
  myOutFileName = makeGraphicsFileName("Sipms-TestTemperaturelocal_");
  if(printGraphicsFile != 0) c_temperature_local->Print(myOutFileName);
X += DelX; Y += DelY;
c_breakDownVoltage_local = new TCanvas("c_breakDownVoltage_local","Sipm Breakdown Voltage (Local)",X,Y,Width,Height);
h_breakDownVoltage_local->Draw();
  myLatex->DrawLatex(52.0,400.0,myString);
  myOutFileName = makeGraphicsFileName("Sipms-BreakDownVoltage(Local)_");
  if(printGraphicsFile != 0) c_breakDownVoltage_local->Print(myOutFileName);
  
X += DelX; Y += DelY;
c_darkCountRate_local = new TCanvas("c_darkCountRate_local","Sipm  Dark Count Rate (Local)",X,Y,Width,Height);
h_darkCountRate_local->Draw();
  myLatex->DrawLatex(170.0,220.0,myString);
  myOutFileName = makeGraphicsFileName("Sipms-DarkCountRateLocal_");
  if(printGraphicsFile != 0) c_darkCountRate_local->Print(myOutFileName);

/*
X += DelX; Y += DelY;
c_currentVoltageCond_local = new TCanvas("c_currentVoltageCond_local","Sipm Current vs Voltage Cond (Local)",X,Y,Width,Height);
h_currentVoltageCond_local->Draw();
  if(printGraphicsFile != 0) c_currentVoltageCond_local->Print(outDirectory+"Sipms-CurrentVsVoltCondLocal_"+theTime+".png");
*/

X += DelX; Y += DelY;
c_xTalk_local = new TCanvas("c_xTalk_local","Sipm Cross Talk (Local)",X,Y,Width,Height);
h_xTalk_local->Draw();
  myLatex->DrawLatex(4.7,250.0,myString);
  myOutFileName = makeGraphicsFileName("Sipms-CrossTalkLocal_");
  //if(printGraphicsFile != 0) c_xTalk_local->Print(outDirectory+"Sipms-CrossTalkLocal_"+theTime+".png");
  if(printGraphicsFile != 0) c_xTalk_local->Print(myOutFileName);
X += DelX; Y += DelY;
c_ledResponse_local = new TCanvas("c_ledResponse_local","Sipm Led Response (Local)",X,Y,Width,Height);
h_ledResponse_local->Draw();
  myOutFileName = makeGraphicsFileName("Sipms-LedResponseLocal_");
  myLatex->DrawLatex(4.0e-3,0.4,myString);
  if(printGraphicsFile != 0) c_ledResponse_local->Print(myOutFileName);
}
//--------------------------------------------------------
//	Construct graphics file name for a plot....
TString sipmVendorTest::makeGraphicsFileName(TString _tempString){
_tempString = _tempString.ReplaceAll(" ","_");
_tempString = _tempString.ReplaceAll(".","_");
_tempString = _tempString.ReplaceAll(",","_");
_tempString = _tempString.ReplaceAll("=","_");
_tempString = _tempString.ReplaceAll(":","_");
TDatime *myTime = new TDatime();
Char_t space[2] = " ";
Char_t underline[2] = "_";
TString theTime = myTime->AsString();

theTime = theTime.ReplaceAll(" ","_");
theTime = theTime.ReplaceAll(".","_");
theTime = theTime.ReplaceAll(",","_");
theTime = theTime.ReplaceAll("=","_");
theTime = theTime.ReplaceAll(":","_");

TString _graphicsFileName;
_graphicsFileName=outDirectory + _tempString.ReplaceAll(" ","") +theTime+GraphicsFileType;
cout << "Save graphics file: " << _graphicsFileName << endl;
return _graphicsFileName;
}
//
//  --------------------------------------------------------------------
//  Run macro here....
void analyzeSipms(TString inFile = "SipmRootHistograms_2022Jun1_09_39_29_.root",Int_t drawGraphics = 0, Int_t debugLevel = 0){
sipmVendorTest *mySipmVendorTest = new sipmVendorTest(inFile,drawGraphics,debugLevel);
//	Signal... Current with dicounters expoxed to light source.
mySipmVendorTest -> bookHistograms();
mySipmVendorTest -> setBranches();
mySipmVendorTest -> fillHistograms();
mySipmVendorTest -> drawCanvas();
}