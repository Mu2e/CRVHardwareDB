//
//  File = "analyzeDiCounters.C"
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
class diCounterTest{
  public:
  diCounterTest(TString tempInFile, Int_t printGraphics, Int_t tempDebug);
  ~diCounterTest();
  void setCurrentBranches(void);
  void bookCurrentHistograms(void);
  void fillCurrentHistograms(void);
  void drawCurrentCanvas(void);
  void setDarkCurrentBranches(void);
  void bookDarkCurrentHistograms(void);
  void fillDarkCurrentHistograms(void);
  void drawDarkCurrentCanvas(void);
  std::string string_from_vector(const std::vector<std::string> &input);
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
    TH1F *h_ledCurrentA1, *h_ledCurrentA2,*h_ledCurrentA3,*h_ledCurrentA4;
    TH1F *h_ledCurrentB1, *h_ledCurrentB2,*h_ledCurrentB3,*h_ledCurrentB4;
    TH1F *h_ledTemperature, *h_ledPosition, *h_ledSipmVoltage;
    
    TH1F *h_sourceCurrentA1, *h_sourceCurrentA2,*h_sourceCurrentA3,*h_sourceCurrentA4;
    TH1F *h_sourceCurrentB1, *h_sourceCurrentB2,*h_sourceCurrentB3,*h_sourceCurrentB4;
    TH1F *h_sourceTemperature, *h_sourceSourcePos, *h_sourceSipmVoltage;

    TH1F *h_cosmicRayCurrentA1, *h_cosmicRayCurrentA2,*h_cosmicRayCurrentA3,*h_cosmicRayCurrentA4;
    TH1F *h_cosmicRayCurrentB1, *h_cosmicRayCurrentB2,*h_cosmicRayCurrentB3,*h_cosmicRayCurrentB4;
    TH1F *h_cosmicRayTemperature, *h_cosmicRaySipmVoltage;
    
    TH1F *h_crystalCurrentA1, *h_crystalCurrentA2,*h_crystalCurrentA3,*h_crystalCurrentA4;
    TH1F *h_crystalCurrentB1, *h_crystalCurrentB2,*h_crystalCurrentB3,*h_crystalCurrentB4;
    TH1F *h_crystalTemperature, *h_crystalSipmVoltage;
    
    TH1F *h_darkCurrentA1, *h_darkCurrentA2,*h_darkCurrentA3,*h_darkCurrentA4;
    TH1F *h_darkCurrentB1, *h_darkCurrentB2,*h_darkCurrentB3,*h_darkCurrentB4;
    TH1F *h_darkCurrentTemp, *h_darkCurrentSipmVoltage;
    // Define Bins
    Int_t nBin1; Double_t lowBin1; Double_t hiBin1;
    Int_t nBin2; Double_t lowBin2; Double_t hiBin2;
    Int_t nTBin; Double_t lowTBin; Double_t hiTBin;
    Int_t nSBin; Double_t lowSBin; Double_t hiSBin;
    Int_t nVoltBin; Double_t lowVoltBin; Double_t hiVoltBin;
    // Define Canvases
    TCanvas *c_ledCurrentA1, *c_ledCurrentA2,*c_ledCurrentA3,*c_ledCurrentA4;
    TCanvas *c_ledCurrentB1, *c_ledCurrentB2,*c_ledCurrentB3,*c_ledCurrentB4;
    TCanvas *c_ledTemperature, *c_ledPosition, *c_ledSipmVoltage;
    
    TCanvas *c_sourceCurrentA1, *c_sourceCurrentA2,*c_sourceCurrentA3,*c_sourceCurrentA4;
    TCanvas *c_sourceCurrentB1, *c_sourceCurrentB2,*c_sourceCurrentB3,*c_sourceCurrentB4;
    TCanvas *c_sourceTemperature, *c_sourceSourcePos, *c_sourceSipmVoltage;
    
    TCanvas *c_cosmicRayCurrentA1, *c_cosmicRayCurrentA2,*c_cosmicRayCurrentA3,*c_cosmicRayCurrentA4;
    TCanvas *c_cosmicRayCurrentB1, *c_cosmicRayCurrentB2,*c_cosmicRayCurrentB3,*c_cosmicRayCurrentB4;
    TCanvas *c_cosmicRayTemperature,  *c_cosmicRaySipmVoltage;
    
    TCanvas *c_crystalCurrentA1, *c_crystalCurrentA2,*c_crystalCurrentA3,*c_crystalCurrentA4;
    TCanvas *c_crystalCurrentB1, *c_crystalCurrentB2,*c_crystalCurrentB3,*c_crystalCurrentB4;
    TCanvas *c_crystalTemperature,  *c_crystalSipmVoltage;
    
    TCanvas *c_darkCurrentA1, *c_darkCurrentA2,*c_darkCurrentA3,*c_darkCurrentA4;
    TCanvas *c_darkCurrentB1, *c_darkCurrentB2,*c_darkCurrentB3,*c_darkCurrentB4;
    TCanvas *c_darkCurrentTemp, *c_darkCurrentSipmVoltage;
    //
    //Char_t diCounterId[30];  // This must equal the number of characters used in the PyRoot script!!!
    //Char_t testDate[30];
    //Char_t flashRate[30];
    //Char_t lightSource[30];
    //  For python 3... character arrays are stored as std::vector<std::string>
    std::vector<std::string> *vect_diCounterId; TBranch *branch_vect_diCounterId;
    std::vector<std::string> *vect_testDate;    TBranch *branch_vect_testDate;
    std::vector<std::string> *vect_flashRate;   TBranch *branch_vect_flashRate;
    std::vector<std::string> *vect_lightSource; TBranch *branch_vect_lightSource;
    //string diCounterId;
    TString string_diCounterId, string_testDate, string_flashRate, string_lightSource;
    Float_t currentA1, currentA2, currentA3, currentA4;
    Float_t currentB1, currentB2, currentB3, currentB4;
    Float_t signalTemp, sourcePos, sipmVoltage;
    //
    //Char_t darkCurrentDiCounterId[21];
    //Char_t darkCurrentTestDate[30];
    TString darkCurrentDiCounterId, darkCurrentTestDate;
    Float_t darkCurrentA1, darkCurrentA2, darkCurrentA3, darkCurrentA4;
    Float_t darkCurrentB1, darkCurrentB2, darkCurrentB3, darkCurrentB4; 
    Float_t darkCurrentTemp, darkCurrentSipmVoltage;
};
//
// ------------------------drawCurrentCanvas(void)------------------------------
//  Implement the Class!
// ------------------------------------------------------
//  Constructor
  diCounterTest::diCounterTest(TString tempInFile,Int_t printGraphics = 0, Int_t debug = 0){
  cmjDiag = debug;
    if(cmjDiag != 0) {
    cout <<"**diCounterTest::diCounterTest.. turn on debug: debug level = "<<cmjDiag<<endl;
    cout<<"**diCounterTest::diCounterTest: start"<<endl;
    }
  printGraphicsFile = printGraphics;
  if(printGraphicsFile != 0) cout<<"*****diCounterTest::diCounterTest... print graphics file!!!!" << endl;
  gStyle -> SetOptStat("nemruoi");  // Print statistitics... page 32 root manual.. reset defaul
  gStyle -> SetOptDate(1);       // Print date on plots
  gStyle -> SetOptFit(1111); // show parameters, errors and chi2... page 72 root manual
  //  Get root file containing root tree
  inputRootFile = new TFile(tempInFile);
  // Get the first root tree for the events with a light source
  myTree1 = new TTree("myTree1","Sipm Currents from UVa Source Tests");
  myTree1 = (TTree*)inputRootFile->Get("diCounterTests");
  //if(cmjDiag > 1 ) myTree1->Scan();
  if(cmjDiag > 1) myTree1->Print();
  if(cmjDiag > 2) cout << "Current Root Directory "<< (gDirectory->GetPath()) << endl;
  nBin1 = 100; lowBin1=0.0; hiBin1=2.0;
  nBin2 = 100; lowBin2=0.0; hiBin2=2.0;
  nTBin = 10;  lowTBin = 15; hiTBin = 25;
  nSBin = 400; lowSBin = 0.0; hiSBin = 400;
  nVoltBin = 50; lowVoltBin = 30.0; hiVoltBin = 80.0;
}
// ------------------------------------------------------
//  Destructor
  diCounterTest::~diCounterTest(){ 
  if(cmjDiag != 0) cout<<"**diCounterTest::~diCounterTest: end"<<endl;
  return;
}
// -----------------------------------------------------------------------
//  Define the histograms.... for tree 1 (signal)
void diCounterTest::bookCurrentHistograms(void){
  if(cmjDiag != 0) cout<<"**diCounterTest::bookHistograms"<<endl;
  //  LED Current
  nBin1 = 100; lowBin1=0.0; hiBin1=2.0;
  h_ledCurrentA1 = new TH1F("h_ledCurrentA1","Sipm Current A1, LED",nBin1,lowBin1,hiBin1);
  h_ledCurrentA2 = new TH1F("h_ledCurrentA2","Sipm Current A2, LED",nBin1,lowBin1,hiBin1);
  h_ledCurrentA3 = new TH1F("h_ledCurrentA3","Sipm Current A3, LED",nBin1,lowBin1,hiBin1);
  h_ledCurrentA4 = new TH1F("h_ledCurrentA4","Sipm Current A4, LED",nBin1,lowBin1,hiBin1);
  h_ledCurrentB1 = new TH1F("h_ledCurrentB1","Sipm Current B1, LED",nBin1,lowBin1,hiBin1);
  h_ledCurrentB2 = new TH1F("h_ledCurrentB2","Sipm Current B2, LED",nBin1,lowBin1,hiBin1);
  h_ledCurrentB3 = new TH1F("h_ledCurrentB3","Sipm Current B3, LED",nBin1,lowBin1,hiBin1);
  h_ledCurrentB4 = new TH1F("h_ledCurrentB4","Sipm Current B4, LED",nBin1,lowBin1,hiBin1);
  h_ledTemperature = new TH1F("h_ledTemperature","Signal Temperature, LED",nTBin,lowTBin,hiTBin);
  h_ledPosition = new TH1F("h_ledPosition","LED Position",nSBin,lowSBin,hiSBin);
  h_ledSipmVoltage = new TH1F("h_ledSipmVoltage","Sipm Voltage, LED",nVoltBin,lowVoltBin,hiVoltBin);
  h_ledCurrentA1->SetFillColor(kRed);
  h_ledCurrentA2->SetFillColor(kRed);
  h_ledCurrentA3->SetFillColor(kRed);
  h_ledCurrentA4->SetFillColor(kRed);
  h_ledCurrentB1->SetFillColor(kRed);
  h_ledCurrentB2->SetFillColor(kRed);
  h_ledCurrentB3->SetFillColor(kRed);
  h_ledCurrentB4->SetFillColor(kRed);
  h_ledTemperature->SetFillColor(kRed);
  h_ledPosition->SetFillColor(kRed);
  h_ledPosition->SetFillColor(kRed);
    //  Source Current
  nBin1 = 100; lowBin1=0.0; hiBin1=2.0;
  h_sourceCurrentA1 = new TH1F("h_sourceCurrentA1","Sipm Current A1, Radioactive Source",nBin1,lowBin1,hiBin1);
  h_sourceCurrentA2 = new TH1F("h_sourceCurrentA2","Sipm Current A2, Radioactive Source",nBin1,lowBin1,hiBin1);
  h_sourceCurrentA3 = new TH1F("h_sourceCurrentA3","Sipm Current A3, Radioactive Source",nBin1,lowBin1,hiBin1);
  h_sourceCurrentA4 = new TH1F("h_sourceCurrentA4","Sipm Current A4, Radioactive Source",nBin1,lowBin1,hiBin1);
  h_sourceCurrentB1 = new TH1F("h_sourceCurrentB1","Sipm Current B1, Radioactive Source",nBin1,lowBin1,hiBin1);
  h_sourceCurrentB2 = new TH1F("h_sourceCurrentB2","Sipm Current B2, Radioactive Source",nBin1,lowBin1,hiBin1);
  h_sourceCurrentB3 = new TH1F("h_sourceCurrentB3","Sipm Current B3, Radioactive Source",nBin1,lowBin1,hiBin1);
  h_sourceCurrentB4 = new TH1F("h_sourceCurrentB4","Sipm Current B4, Radioactive Source",nBin1,lowBin1,hiBin1);
  h_sourceTemperature = new TH1F("h_sourceTemperature","Temperature, Radioactive Source",nTBin,lowTBin,hiTBin);
  h_sourceSourcePos = new TH1F("h_sourceSourcePos","Source Position",nSBin,lowSBin,hiSBin);
  h_sourceSipmVoltage = new TH1F("h_sourceSipmVoltage","Sipm Voltage, Radioactive Source",nVoltBin,lowVoltBin,hiVoltBin);
  h_sourceCurrentA1->SetFillColor(kBlue);
  h_sourceCurrentA2->SetFillColor(kBlue);
  h_sourceCurrentA3->SetFillColor(kBlue);
  h_sourceCurrentA4->SetFillColor(kBlue);
  h_sourceCurrentB1->SetFillColor(kBlue);
  h_sourceCurrentB2->SetFillColor(kBlue);
  h_sourceCurrentB3->SetFillColor(kBlue);
  h_sourceCurrentB4->SetFillColor(kBlue);
  h_sourceTemperature->SetFillColor(kBlue);
  h_sourceSourcePos->SetFillColor(kBlue);
  h_sourceSipmVoltage->SetFillColor(kBlue);
      //  Cosmic Ray Current
  nBin1 = 100; lowBin1=0.0; hiBin1=2.0;
  h_cosmicRayCurrentA1 = new TH1F("h_cosmicRayCurrentA1","Sipm Current A1, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_cosmicRayCurrentA2 = new TH1F("h_cosmicRayCurrentA2","Sipm Current A2, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_cosmicRayCurrentA3 = new TH1F("h_cosmicRayCurrentA3","Sipm Current A3, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_cosmicRayCurrentA4 = new TH1F("h_cosmicRayCurrentA4","Sipm Current A4, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_cosmicRayCurrentB1 = new TH1F("h_cosmicRayCurrentB1","Sipm Current B1, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_cosmicRayCurrentB2 = new TH1F("h_cosmicRayCurrentB2","Sipm Current B2, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_cosmicRayCurrentB3 = new TH1F("h_cosmicRayCurrentB3","Sipm Current B3, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_cosmicRayCurrentB4 = new TH1F("h_cosmicRayCurrentB4","Sipm Current B4, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_cosmicRayTemperature = new TH1F("h_cosmicRayTemperature","Temperature, Cosmic Rays",nTBin,lowTBin,hiTBin);
  h_cosmicRaySipmVoltage = new TH1F("h_cosmicRaySipmVoltage","Sipm Voltage, Cosmic Rays",nVoltBin,lowVoltBin,hiVoltBin);
  h_cosmicRayCurrentA1->SetFillColor(kViolet);
  h_cosmicRayCurrentA2->SetFillColor(kViolet);
  h_cosmicRayCurrentA3->SetFillColor(kViolet);
  h_cosmicRayCurrentA4->SetFillColor(kViolet);
  h_cosmicRayCurrentB1->SetFillColor(kViolet);
  h_cosmicRayCurrentB2->SetFillColor(kViolet);
  h_cosmicRayCurrentB3->SetFillColor(kViolet);
  h_cosmicRayCurrentB4->SetFillColor(kViolet);
  h_cosmicRayTemperature->SetFillColor(kViolet);
  h_cosmicRaySipmVoltage->SetFillColor(kViolet);
  //  Crystal Current
  nBin1 = 100; lowBin1=0.0; hiBin1=2.0;
  h_crystalCurrentA1 = new TH1F("h_crystalCurrentA1","Sipm Current A1, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_crystalCurrentA2 = new TH1F("h_crystalCurrentA2","Sipm Current A2, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_crystalCurrentA3 = new TH1F("h_crystalCurrentA3","Sipm Current A3, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_crystalCurrentA4 = new TH1F("h_crystalCurrentA4","Sipm Current A4, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_crystalCurrentB1 = new TH1F("h_crystalCurrentB1","Sipm Current B1, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_crystalCurrentB2 = new TH1F("h_crystalCurrentB2","Sipm Current B2, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_crystalCurrentB3 = new TH1F("h_crystalCurrentB3","Sipm Current B3, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_crystalCurrentB4 = new TH1F("h_crystalCurrentB4","Sipm Current B4, Cosmic Rays",nBin1,lowBin1,hiBin1);
  h_crystalTemperature = new TH1F("h_crystalTemperature","Temperature, Cosmic Rays",nTBin,lowTBin,hiTBin);
  h_crystalSipmVoltage = new TH1F("h_crystalSipmVoltage","Sipm Voltage, Cosmic Rays",nVoltBin,lowVoltBin,hiVoltBin);
  h_crystalCurrentA1->SetFillColor(kBlue);
  h_crystalCurrentA2->SetFillColor(kBlue);
  h_crystalCurrentA3->SetFillColor(kBlue);
  h_crystalCurrentA4->SetFillColor(kBlue);
  h_crystalCurrentB1->SetFillColor(kBlue);
  h_crystalCurrentB2->SetFillColor(kBlue);
  h_crystalCurrentB3->SetFillColor(kBlue);
  h_crystalCurrentB4->SetFillColor(kBlue);
  h_crystalTemperature->SetFillColor(kBlue);
  h_crystalSipmVoltage->SetFillColor(kBlue);
  //
  nBin1 = 100; lowBin1=0.0; hiBin1=2.0;
  h_darkCurrentA1 = new TH1F("h_darkCurrentA1","Sipm Dark Current A1",nBin2,lowBin2,hiBin2);
  h_darkCurrentA2 = new TH1F("h_darkCurrentA2","Sipm Dark Current A2",nBin2,lowBin2,hiBin2);
  h_darkCurrentA3 = new TH1F("h_darkCurrentA3","Sipm Dark Current A3",nBin2,lowBin2,hiBin2);
  h_darkCurrentA4 = new TH1F("h_darkCurrentA4","Sipm Dark Current A4",nBin2,lowBin2,hiBin2);
  h_darkCurrentB1 = new TH1F("h_darkCurrentB1","Sipm Dark Current B1",nBin2,lowBin2,hiBin2);
  h_darkCurrentB2 = new TH1F("h_darkCurrentB2","Sipm Dark Current B2",nBin2,lowBin2,hiBin2);
  h_darkCurrentB3 = new TH1F("h_darkCurrentB3","Sipm Dark Current B3",nBin2,lowBin2,hiBin2);
  h_darkCurrentB4 = new TH1F("h_darkCurrentB4","Sipm Dark Current B4",nBin2,lowBin2,hiBin2);
  h_darkCurrentTemp = new TH1F("h_darkCurrentTemp","Dark Current Temperature",nTBin,lowTBin,hiTBin);
  h_darkCurrentSipmVoltage = new TH1F("h_darkCurrentSipmVoltage","Dark Current Sipm Voltage",nVoltBin,lowVoltBin,hiVoltBin);
  h_darkCurrentA1->SetFillColor(kBlack);
  h_darkCurrentA2->SetFillColor(kBlack);
  h_darkCurrentA3->SetFillColor(kBlack);
  h_darkCurrentA4->SetFillColor(kBlack);
  h_darkCurrentB1->SetFillColor(kBlack);
  h_darkCurrentB2->SetFillColor(kBlack);
  h_darkCurrentB3->SetFillColor(kBlack);
  h_darkCurrentB4->SetFillColor(kBlack);
  h_darkCurrentTemp->SetFillColor(kBlack);
  h_darkCurrentSipmVoltage->SetFillColor(kBlack);
}
// -----------------------------------------------------------------------
//  Define Branches....
void diCounterTest::setCurrentBranches(void){
  if(cmjDiag != 0)cout<<"**diCounterTest::setCurrentBranches"<<endl;
  // For python3 ... read character arrays stored as std::vector<std::string>
  vect_diCounterId = 0; branch_vect_diCounterId = 0;
  myTree1 -> SetBranchAddress("diCounterId",&vect_diCounterId,&branch_vect_diCounterId);
  vect_testDate = 0; branch_vect_testDate = 0;
  myTree1-> SetBranchAddress("testDate",&vect_testDate,&branch_vect_testDate);
  vect_flashRate = 0; branch_vect_flashRate = 0;
  myTree1-> SetBranchAddress("flashRate",&vect_flashRate,&branch_vect_flashRate);
  vect_lightSource = 0; branch_vect_lightSource = 0;
  myTree1-> SetBranchAddress("lightSource",&vect_lightSource,&branch_vect_lightSource);
  //
  myTree1->SetBranchAddress("currentA1",&currentA1);
  myTree1->SetBranchAddress("currentA2",&currentA2);
  myTree1->SetBranchAddress("currentA3",&currentA3);
  myTree1->SetBranchAddress("currentA4",&currentA4);
  myTree1->SetBranchAddress("currentB1",&currentB1);
  myTree1->SetBranchAddress("currentB2",&currentB2);
  myTree1->SetBranchAddress("currentB3",&currentB3);
  myTree1->SetBranchAddress("currentB4",&currentB4);
  myTree1->SetBranchAddress("temperature",&signalTemp);
  //myTree1->SetBranchAddress("light_source_position",&sourcePos);
  //myTree1->SetBranchAddress("sipmVoltage",&sipmVoltage);
  if(cmjDiag > 3) myTree1->Print();
}
// -----------------------------------------------------------------------
//  fill the histograms.... from tree 1 (signal)
//  The way PyRoot works to save a tree is to save lists...
//	This is effectively one entry with arrays that are the 
//	size of the number of leaves.....
void diCounterTest::fillCurrentHistograms(void){
  if(cmjDiag != 0) cout<<"**diCounterTest::fillCurrentHistograms"<<endl;
  if(cmjDiag > 2) myTree1->Scan();
  Int_t maxEntries = (Int_t) myTree1->GetEntries();
  if(cmjDiag != 0) cout<<"**diCounterTest::fillCurrentHistogram maxEntries = "<<maxEntries<<endl;
  for(Int_t m = 0; m < maxEntries; m++){
  myTree1->GetEntry(m);
  //  Load the strings variable for selection of database keys... First get the branch  
  Long64_t tentry = myTree1->LoadTree(m);
  branch_vect_diCounterId->GetEntry(tentry);
  branch_vect_testDate->GetEntry(tentry);
  branch_vect_flashRate->GetEntry(tentry);
  branch_vect_lightSource->GetEntry(tentry);
  //  Load the strings variable for selection of database keys... second get the contents
  string_diCounterId = vect_diCounterId->at(m);
  string_testDate = vect_testDate->at(m);
  string_flashRate = vect_flashRate->at(m);
  string_lightSource = vect_lightSource->at(m);
  //
  if(TString(string_lightSource)=="led"){
  h_ledCurrentA1->Fill(currentA1);
  h_ledCurrentA2->Fill(currentA1);
  h_ledCurrentA3->Fill(currentA1);
  h_ledCurrentA4->Fill(currentA1);
  h_ledCurrentB1->Fill(currentB1);
  h_ledCurrentB2->Fill(currentB2);
  h_ledCurrentB3->Fill(currentB3);
  h_ledCurrentB4->Fill(currentB4);
  h_ledTemperature->Fill(signalTemp);
  h_ledPosition->Fill(sourcePos);
  h_ledSipmVoltage->Fill(sipmVoltage);
  }
  if(TString(string_lightSource)=="rad"){
  h_sourceCurrentA1->Fill(currentA1);
  h_sourceCurrentA2->Fill(currentA1);
  h_sourceCurrentA3->Fill(currentA1);
  h_sourceCurrentA4->Fill(currentA1);
  h_sourceCurrentB1->Fill(currentB1);
  h_sourceCurrentB2->Fill(currentB2);
  h_sourceCurrentB3->Fill(currentB3);
  h_sourceCurrentB4->Fill(currentB4);
  h_sourceTemperature->Fill(signalTemp);
  h_sourceSourcePos->Fill(sourcePos);
  h_sourceSipmVoltage->Fill(sipmVoltage);
  }
  
  //  for crystals!!!!
  if(TString(string_lightSource)=="cosmic"){
  h_crystalCurrentA1->Fill(currentA1);
  h_crystalCurrentA2->Fill(currentA1);
  h_crystalCurrentA3->Fill(currentA1);
  h_crystalCurrentA4->Fill(currentA1);
  h_crystalCurrentB1->Fill(currentB1);
  h_crystalCurrentB2->Fill(currentB2);
  h_crystalCurrentB3->Fill(currentB3);
  h_crystalCurrentB4->Fill(currentB4);
  h_crystalTemperature->Fill(signalTemp);
  h_crystalSipmVoltage->Fill(sipmVoltage);
  }
  if(TString(string_lightSource)=="cosmic"){
  h_cosmicRayCurrentA1->Fill(currentA1);
  h_cosmicRayCurrentA2->Fill(currentA1);
  h_cosmicRayCurrentA3->Fill(currentA1);
  h_cosmicRayCurrentA4->Fill(currentA1);
  h_cosmicRayCurrentB1->Fill(currentB1);
  h_cosmicRayCurrentB2->Fill(currentB2);
  h_cosmicRayCurrentB3->Fill(currentB3);
  h_cosmicRayCurrentB4->Fill(currentB4);
  h_cosmicRayTemperature->Fill(signalTemp);
  h_cosmicRaySipmVoltage->Fill(sipmVoltage);
  }
  //	Dark current
  if(TString(string_lightSource)=="dark"){
  h_darkCurrentA1->Fill(currentA1);
  h_darkCurrentA2->Fill(currentA1);
  h_darkCurrentA3->Fill(currentA1);
  h_darkCurrentA4->Fill(currentA1);
  h_darkCurrentB1->Fill(currentB1);
  h_darkCurrentB2->Fill(currentB2);
  h_darkCurrentB3->Fill(currentB3);
  h_darkCurrentB4->Fill(currentB4);
  h_darkCurrentTemp->Fill(signalTemp);
  h_darkCurrentSipmVoltage->Fill(sipmVoltage);
  }
  //cout<<"**diCounterTest.. diCounterId = "<<string_diCounterId<<" testDate "<<string_testDate<<" flashRate = "<<string_flashRate<<" lightSource = "<<string_lightSource<<endl;
  if(cmjDiag > 2){
    cout <<"**diCounterTest::fillCurrentHistogram... diCounterId = "<<string_diCounterId << endl;
    cout <<"**diCounterTest::fillCurrentHistogram... testDate    = "<<string_testDate << endl;
    cout <<"**diCounterTest::fillCurrentHistogram... flashRate   = "<<string_flashRate<< endl;
    cout <<"**diCounterTest::fillCurrentHistogram... lightSource = "<<string_lightSource << endl;
    }
  }
}
// -------------------------------
//  from stack overflow...
std::string diCounterTest::string_from_vector(const std::vector<std::string> &input) {
  std::stringstream ss;
  for(std::vector<std::string>::const_iterator itr = input.begin(); itr != input.end(); itr++){ss << *itr;}
  return ss.str();
}
// -----------------------------------------------------------------------
//  Draw the histograms.... from tree 1 (signal)
void diCounterTest::drawCurrentCanvas(void){
  Int_t X0   = 50;  Int_t Y0   = 50;
Int_t DelX = 10;  Int_t DelY = 10;
Int_t X; Int_t Y;
Int_t Width = 600; Int_t Height = 600;
X = X0; Y = Y0;
TDatime *myTime = new TDatime();
Char_t space[2] = " ";
Char_t underline[2] = "_";
TString outDirectory = "graphics-DiCounters-2022Jun22/";
cout<<"diCounterTest::drawCurrentCanvas... write files to "<<outDirectory<<endl;
TString theTime = myTime->AsString();
std::cout << "**diCounterTest::drawDarkCurrentCanvas: time = "<< theTime.ReplaceAll(" ","_") <<std::endl;
//  LED Canvases
c_ledCurrentA1 = new TCanvas("c_ledCurrentA1","Sipm Current A1, LED",X,Y,Width,Height);
h_ledCurrentA1->Draw();
  if(printGraphicsFile != 0) c_ledCurrentA1->Print(outDirectory+"ledCurrentA1_"+theTime+".png");
X += DelX; Y += DelY;
c_ledCurrentA2 = new TCanvas("c_ledCurrentA2","Sipm Current A2, LED",X,Y,Width,Height);
h_ledCurrentA2->Draw();
  if(printGraphicsFile != 0) c_ledCurrentA2->Print(outDirectory+"ledCurrentA2_"+theTime+".png");
X += DelX; Y += DelY;
c_ledCurrentA3 = new TCanvas("c_ledCurrentA3","Sipm Current A3, LED",X,Y,Width,Height);
h_ledCurrentA3->Draw();
  if(printGraphicsFile != 0) c_ledCurrentA3->Print(outDirectory+"ledCurrentA3_"+theTime+".png");
X += DelX; Y += DelY;
c_ledCurrentA4 = new TCanvas("c_ledCurrentA4","LSipm Current A4, LED",X,Y,Width,Height);
h_ledCurrentA4->Draw();
  if(printGraphicsFile != 0) c_ledCurrentA4->Print(outDirectory+"ledCurrentA4_"+theTime+".png");
X += DelX; Y += DelY;
c_ledCurrentB1 = new TCanvas("c_ledCurrentB1","Sipm Current B1, LED",X,Y,Width,Height);
h_ledCurrentB1->Draw();
  if(printGraphicsFile != 0) c_ledCurrentB1->Print(outDirectory+"ledCurrentB1_"+theTime+".png");
X += DelX; Y += DelY;
c_ledCurrentB2 = new TCanvas("c_ledCurrentB2","Sipm Current B2, LED",X,Y,Width,Height);
h_ledCurrentA2->Draw();
  if(printGraphicsFile != 0) c_ledCurrentB2->Print(outDirectory+"ledCurrentB2_"+theTime+".png");
X += DelX; Y += DelY;
c_ledCurrentB3 = new TCanvas("c_ledCurrentB3","Sipm Current B3, LED",X,Y,Width,Height);
h_ledCurrentB3->Draw();
  if(printGraphicsFile != 0) c_ledCurrentB3->Print(outDirectory+"ledCurrentB3_"+theTime+".png");
X += DelX; Y += DelY;
c_ledCurrentB4 = new TCanvas("c_ledCurrentB4","Sipm Current B4, LED",X,Y,Width,Height);
h_ledCurrentB4->Draw();
  if(printGraphicsFile != 0) c_ledCurrentB4->Print(outDirectory+"ledCurrentB4_"+theTime+".png");
X += DelX; Y += DelY;
c_ledTemperature = new TCanvas("c_ledTemperature","Temperature with LED",X,Y,Width,Height);
h_ledTemperature->Draw();
  if(printGraphicsFile != 0) c_ledTemperature->Print(outDirectory+"ledSignalTemp_"+theTime+".png");
X += DelX; Y += DelY;
c_ledPosition = new TCanvas("c_ledPosition","LED Position",X,Y,Width,Height);
h_ledPosition->Draw();
  if(printGraphicsFile != 0) c_ledPosition->Print(outDirectory+"LedPosition_"+theTime+".png");
X += DelX; Y += DelY;
c_ledSipmVoltage = new TCanvas("c_ledSipmVoltage","Sipm Voltage, LED",X,Y,Width,Height);
h_ledSipmVoltage->Draw();
  if(printGraphicsFile != 0) c_ledSipmVoltage->Print(outDirectory+"ledSipmVoltage_"+theTime+".png");
  
  
//  Source Canvases
X += 200; Y += 50;
c_sourceCurrentA1 = new TCanvas("c_sourceCurrentA1","Sipm Current A1, Radioactive Source",X,Y,Width,Height);
h_sourceCurrentA1->Draw();
  if(printGraphicsFile != 0) c_sourceCurrentA1->Print(outDirectory+"sourceCurrentA1_"+theTime+".png");
X += DelX; Y += DelY;
c_sourceCurrentA2 = new TCanvas("c_sourceCurrentA2","Sipm Current A2, Radioactive Source",X,Y,Width,Height);
h_sourceCurrentA2->Draw();
  if(printGraphicsFile != 0) c_sourceCurrentA2->Print(outDirectory+"sourceCurrentA2_"+theTime+".png");
X += DelX; Y += DelY;
c_sourceCurrentA3 = new TCanvas("c_sourceCurrentA3","Sipm Current A3, Radioactive Source",X,Y,Width,Height);
h_sourceCurrentA3->Draw();
  if(printGraphicsFile != 0) c_sourceCurrentA3->Print(outDirectory+"sourceCurrentA3_"+theTime+".png");
X += DelX; Y += DelY;
c_sourceCurrentA4 = new TCanvas("c_sourceCurrentA4","Sipm Current A4, Radioactive Source",X,Y,Width,Height);
h_sourceCurrentA4->Draw();
  if(printGraphicsFile != 0) c_sourceCurrentA4->Print(outDirectory+"sourceCurrentA4_"+theTime+".png");
X += DelX; Y += DelY;
c_sourceCurrentB1 = new TCanvas("c_sourceCurrentB1","Sipm Current B1, Radioactive Source",X,Y,Width,Height);
h_sourceCurrentB1->Draw();
  if(printGraphicsFile != 0) c_sourceCurrentB1->Print(outDirectory+"sourceCurrentB1_"+theTime+".png");
X += DelX; Y += DelY;
c_sourceCurrentB2 = new TCanvas("c_sourceCurrentB2","Sipm Current B2, Radioactive Source",X,Y,Width,Height);
h_sourceCurrentB2->Draw();
  if(printGraphicsFile != 0) c_sourceCurrentB2->Print(outDirectory+"sourceCurrentB2_"+theTime+".png");
X += DelX; Y += DelY;
c_sourceCurrentB3 = new TCanvas("c_sourceCurrentB3","Sipm Current B3, Radioactive Source",X,Y,Width,Height);
h_sourceCurrentB3->Draw();
  if(printGraphicsFile != 0) c_sourceCurrentB3->Print(outDirectory+"sourceCurrentB3_"+theTime+".png");
X += DelX; Y += DelY;
c_sourceCurrentB4 = new TCanvas("c_sourceCurrentB4","Sipm Current B4, Radioactive Source",X,Y,Width,Height);
h_sourceCurrentB4->Draw();
  if(printGraphicsFile != 0) c_sourceCurrentB4->Print(outDirectory+"sourceCurrentB4_"+theTime+".png");
X += DelX; Y += DelY;
c_sourceTemperature = new TCanvas("c_sourceTemperature","Temperature with Radioactive Source",X,Y,Width,Height);
h_sourceTemperature->Draw();
  if(printGraphicsFile != 0) c_sourceTemperature->Print(outDirectory+"sourceSignalTemperature_"+theTime+".png");
X += DelX; Y += DelY;
c_sourceSourcePos = new TCanvas("c_sourceSourcePos","Radioactive Source Position",X,Y,Width,Height);
h_sourceSourcePos->Draw();
  if(printGraphicsFile != 0) c_sourceSourcePos->Print(outDirectory+"sourcePosition_"+theTime+".png");
X += DelX; Y += DelY;
c_sourceSipmVoltage = new TCanvas("c_sourceSipmVoltage","Sipm Voltage, Radioactive Source",X,Y,Width,Height);
h_sourceSipmVoltage->Draw();
  if(printGraphicsFile != 0) c_sourceSipmVoltage->Print(outDirectory+"sourceSipmVoltage_"+theTime+".png");
  
 
//  Cosmic Ray Canvases
X += 200; Y += 50;
c_cosmicRayCurrentA1 = new TCanvas("c_cosmicRayCurrentA1","Sipm Current A1, Cosmic Rays",X,Y,Width,Height);
h_cosmicRayCurrentA1->Draw();
  if(printGraphicsFile != 0) c_cosmicRayCurrentA1->Print(outDirectory+"cosmicRayCurrentA1_"+theTime+".png");
X += DelX; Y += DelY;
c_cosmicRayCurrentA2 = new TCanvas("c_cosmicRayCurrentA2","Sipm Current A2, Cosmic Rays",X,Y,Width,Height);
h_cosmicRayCurrentA2->Draw();
  if(printGraphicsFile != 0) c_cosmicRayCurrentA2->Print(outDirectory+"cosmicRayCurrentA2_"+theTime+".png");
X += DelX; Y += DelY;
c_cosmicRayCurrentA3 = new TCanvas("c_cosmicRayCurrentA3","Sipm Current A3, Cosmic Rays",X,Y,Width,Height);
h_cosmicRayCurrentA3->Draw();
  if(printGraphicsFile != 0) c_cosmicRayCurrentA3->Print(outDirectory+"cosmicRayCurrentA3_"+theTime+".png");
X += DelX; Y += DelY;
c_cosmicRayCurrentA4 = new TCanvas("c_cosmicRayCurrentA4","Sipm Current A4, Cosmic Rays",X,Y,Width,Height);
h_cosmicRayCurrentA4->Draw();
  if(printGraphicsFile != 0) c_cosmicRayCurrentA4->Print(outDirectory+"cosmicRayCurrentA4_"+theTime+".png");
X += DelX; Y += DelY;
c_cosmicRayCurrentB1 = new TCanvas("c_cosmicRayCurrentB1","Sipm Current B1, Cosmic Rays",X,Y,Width,Height);
h_cosmicRayCurrentB1->Draw();
  if(printGraphicsFile != 0) c_cosmicRayCurrentB1->Print(outDirectory+"cosmicRayCurrentB1_"+theTime+".png");
X += DelX; Y += DelY;
c_cosmicRayCurrentB2 = new TCanvas("c_cosmicRayCurrentB2","Sipm Current B2, Cosmic Rays",X,Y,Width,Height);
h_cosmicRayCurrentB2->Draw();
  if(printGraphicsFile != 0) c_cosmicRayCurrentB2->Print(outDirectory+"cosmicRayCurrentB2_"+theTime+".png");
X += DelX; Y += DelY;
c_cosmicRayCurrentB3 = new TCanvas("c_cosmicRayCurrentB3","Sipm Current B3, Cosmic Rays",X,Y,Width,Height);
h_cosmicRayCurrentB3->Draw();
  if(printGraphicsFile != 0) c_cosmicRayCurrentB3->Print(outDirectory+"cosmicRayCurrentB3_"+theTime+".png");
X += DelX; Y += DelY;
c_cosmicRayCurrentB4 = new TCanvas("c_cosmicRayCurrentB4","Sipm Current B4, Cosmic Rays",X,Y,Width,Height);
h_cosmicRayCurrentB4->Draw();
  if(printGraphicsFile != 0) c_cosmicRayCurrentB4->Print(outDirectory+"cosmicRayCurrentB4_"+theTime+".png");
X += DelX; Y += DelY;
c_cosmicRayTemperature = new TCanvas("c_cosmicRayTemperature","Temperature with Cosmic Rays",X,Y,Width,Height);
h_cosmicRayTemperature->Draw();
  if(printGraphicsFile != 0) c_cosmicRayTemperature->Print(outDirectory+"cosmicRaySignalTemperature_"+theTime+".png");
//X += DelX; Y += DelY;
//c_sourceSourcePos = new TCanvas("c_sourceSourcePos","Radioactive Source Position",X,Y,Width,Height);
//h_sourceSourcePos->Draw();
//  if(printGraphicsFile != 0) c_sourceSourcePos->Print(outDirectory+"sourcePosition_"+theTime+".png");
X += DelX; Y += DelY;
c_cosmicRaySipmVoltage = new TCanvas("c_cosmicRaySipmVoltage","Sipm Voltage, Cosmic Rays",X,Y,Width,Height);
h_cosmicRaySipmVoltage->Draw();
  if(printGraphicsFile != 0) c_cosmicRaySipmVoltage->Print(outDirectory+"cosmicRayVoltage_"+theTime+".png");
  
  
 
//  Cosmic Ray Canvases
X += 200; Y += 50;
c_crystalCurrentA1 = new TCanvas("c_crystalCurrentA1","Sipm Current A1, Cosmic Rays",X,Y,Width,Height);
h_crystalCurrentA1->Draw();
  if(printGraphicsFile != 0) c_crystalCurrentA1->Print(outDirectory+"crystalCurrentA1_"+theTime+".png");
X += DelX; Y += DelY;
c_crystalCurrentA2 = new TCanvas("c_crystalCurrentA2","Sipm Current A2, Cosmic Rays",X,Y,Width,Height);
h_crystalCurrentA2->Draw();
  if(printGraphicsFile != 0) c_crystalCurrentA2->Print(outDirectory+"crystalCurrentA2_"+theTime+".png");
X += DelX; Y += DelY;
c_crystalCurrentA3 = new TCanvas("c_crystalCurrentA3","Sipm Current A3, Cosmic Rays",X,Y,Width,Height);
h_crystalCurrentA3->Draw();
  if(printGraphicsFile != 0) c_crystalCurrentA3->Print(outDirectory+"crystalCurrentA3_"+theTime+".png");
X += DelX; Y += DelY;
c_crystalCurrentA4 = new TCanvas("c_crystalCurrentA4","Sipm Current A4, Cosmic Rays",X,Y,Width,Height);
h_crystalCurrentA4->Draw();
  if(printGraphicsFile != 0) c_crystalCurrentA4->Print(outDirectory+"crystalCurrentA4_"+theTime+".png");
X += DelX; Y += DelY;
c_crystalCurrentB1 = new TCanvas("c_crystalCurrentB1","Sipm Current B1, Cosmic Rays",X,Y,Width,Height);
h_crystalCurrentB1->Draw();
  if(printGraphicsFile != 0) c_crystalCurrentB1->Print(outDirectory+"crystalCurrentB1_"+theTime+".png");
X += DelX; Y += DelY;
c_crystalCurrentB2 = new TCanvas("c_crystalCurrentB2","Sipm Current B2, Cosmic Rays",X,Y,Width,Height);
h_crystalCurrentB2->Draw();
  if(printGraphicsFile != 0) c_crystalCurrentB2->Print(outDirectory+"crystalCurrentB2_"+theTime+".png");
X += DelX; Y += DelY;
c_crystalCurrentB3 = new TCanvas("c_crystalCurrentB3","Sipm Current B3, Cosmic Rays",X,Y,Width,Height);
h_crystalCurrentB3->Draw();
  if(printGraphicsFile != 0) c_crystalCurrentB3->Print(outDirectory+"crystalCurrentB3_"+theTime+".png");
X += DelX; Y += DelY;
c_crystalCurrentB4 = new TCanvas("c_crystalCurrentB4","Sipm Current B4, Cosmic Rays",X,Y,Width,Height);
h_crystalCurrentB4->Draw();
  if(printGraphicsFile != 0) c_crystalCurrentB4->Print(outDirectory+"crystalCurrentB4_"+theTime+".png");
X += DelX; Y += DelY;
c_crystalTemperature = new TCanvas("c_crystalTemperature","Temperature with Cosmic Rays",X,Y,Width,Height);
h_crystalTemperature->Draw();
  if(printGraphicsFile != 0) c_crystalTemperature->Print(outDirectory+"crystalSignalTemperature_"+theTime+".png");
//X += DelX; Y += DelY;
//c_sourceSourcePos = new TCanvas("c_sourceSourcePos","Radioactive Source Position",X,Y,Width,Height);
//h_sourceSourcePos->Draw();
//  if(printGraphicsFile != 0) c_sourceSourcePos->Print(outDirectory+"sourcePosition_"+theTime+".png");
X += DelX; Y += DelY;
c_crystalSipmVoltage = new TCanvas("c_crystalSipmVoltage","Sipm Voltage, Cosmic Rays",X,Y,Width,Height);
h_crystalSipmVoltage->Draw();
  if(printGraphicsFile != 0) c_crystalSipmVoltage->Print(outDirectory+"crystalVoltage_"+theTime+".png");  
  
  
// Dark Currentif(printGraphicsFile != 0) c_darkCurrentB3->Print(outDirectory+"darkCurrentB3_"+theTime+".png");
X += 200; Y += 50;
c_darkCurrentA1 = new TCanvas("c_darkCurrentA1","Sipm Dark Current A1",X,Y,Width,Height);
h_darkCurrentA1->Draw();
  if(printGraphicsFile != 0) c_darkCurrentA1->Print(outDirectory+"darkCurrentA1_"+theTime+".png");
X += DelX; Y += DelY;
c_darkCurrentA2 = new TCanvas("c_darkCurrentA2","Sipm Dark Current A2",X,Y,Width,Height);
h_darkCurrentA2->Draw();
  if(printGraphicsFile != 0) c_darkCurrentA2->Print(outDirectory+"darkCurrentA2_"+theTime+".png");
X += DelX; Y += DelY;
c_darkCurrentA3 = new TCanvas("c_darkCurrentA3","Sipm Dark Current A3",X,Y,Width,Height);
h_darkCurrentA3->Draw();
  if(printGraphicsFile != 0) c_darkCurrentA3->Print(outDirectory+"darkCurrentA3_"+theTime+".png");
X += DelX; Y += DelY;
c_darkCurrentA4 = new TCanvas("c_darkCurrentA4","Sipm Dark Current A4",X,Y,Width,Height);
h_darkCurrentA4->Draw();
  if(printGraphicsFile != 0) c_darkCurrentA4->Print(outDirectory+"darkCurrentA4_"+theTime+".png");
X += DelX; Y += DelY;
c_darkCurrentB1 = new TCanvas("c_darkCurrentB1","Sipm Dark Current B1",X,Y,Width,Height);
h_darkCurrentB1->Draw();
  if(printGraphicsFile != 0) c_darkCurrentB1->Print(outDirectory+"darkCurrentB1_"+theTime+".png");
X += DelX; Y += DelY;
c_darkCurrentB2 = new TCanvas("c_darkCurrentB2","Sipm Dark Current B2",X,Y,Width,Height);
h_darkCurrentB2->Draw();
  if(printGraphicsFile != 0) c_darkCurrentB2->Print(outDirectory+"darkCurrentB2_"+theTime+".png");
X += DelX; Y += DelY;
c_darkCurrentB3 = new TCanvas("c_darkCurrentB3","Sipm Dark Current B3",X,Y,Width,Height);
h_darkCurrentB3->Draw();
  if(printGraphicsFile != 0) c_darkCurrentB3->Print(outDirectory+"darkCurrentB3_"+theTime+".png");
X += DelX; Y += DelY;
c_darkCurrentB4 = new TCanvas("c_darkCurrentB4","Sipm Dark Current B4",X,Y,Width,Height);
h_darkCurrentB4->Draw();
  if(printGraphicsFile != 0)  c_darkCurrentB4->Print(outDirectory+"darkCurrentB4_"+theTime+".png");
X += DelX; Y += DelY;
c_darkCurrentTemp = new TCanvas("c_darkCurrentTemp","Dark Current Temperature",X,Y,Width,Height);
  if(printGraphicsFile != 0) c_darkCurrentTemp->Print(outDirectory+"darkCurrentTemp_"+theTime+".png");
h_darkCurrentTemp->Draw();
X += DelX; Y += DelY;

}

// -----------------------------------------------------------------------
//  fill the histograms.... from tree 2 (dark current)
//  The way PyRoot works to save a tree is to save lists...
//	This is effectively one entry with arrays that are the 
//	size of the number of leaves.....
void diCounterTest::fillDarkCurrentHistograms(void){
  if(cmjDiag != 0) cout<<"**diCounterTest::fillDarkCurrentHistograms"<<endl;
  Int_t maxEntries = (Int_t) myTree2->GetEntries();
  for(Int_t m = 0; m < maxEntries; m++){
  myTree2->GetEntry(m);
    //  Load the strings variable for selection of database keys... First get the branch  
  Long64_t tentry = myTree1->LoadTree(m);
  branch_vect_diCounterId->GetEntry(tentry);
  branch_vect_testDate->GetEntry(tentry);
  branch_vect_flashRate->GetEntry(tentry);
  branch_vect_lightSource->GetEntry(tentry);
  //  Load the strings variable for selection of database keys... second get the contents
  string_diCounterId = vect_diCounterId->at(m);
  string_testDate = vect_testDate->at(m);
  string_flashRate = vect_flashRate->at(m);
  string_lightSource = vect_lightSource->at(m);
  //
  h_darkCurrentA1->Fill(darkCurrentA1);
  h_darkCurrentA2->Fill(darkCurrentA2);
  h_darkCurrentA3->Fill(darkCurrentA3);
  h_darkCurrentA4->Fill(darkCurrentA4);
  h_darkCurrentB1->Fill(darkCurrentB1);
  h_darkCurrentB2->Fill(darkCurrentB2);
  h_darkCurrentB3->Fill(darkCurrentB3);
  h_darkCurrentB4->Fill(darkCurrentB4);
  h_darkCurrentTemp->Fill(darkCurrentTemp);
  h_darkCurrentSipmVoltage->Fill(darkCurrentSipmVoltage);
 //   if(cmjDiag > 2){
 //   cout <<"**diCounterTest::fillDarkCurrentHistograms... darkCurrentDiCounterId = "<<darkCurrentDiCounterId << endl;
 //   cout <<"**diCounterTest::fillDarkCurrentHistograms... darkCurrentTestDate  = "<<darkCurrentTestDate << endl;;
 //   }
  }
}
// -----------------------------------------------------------------------
//  Draw the histograms.... from tree 2 (dark current)
void diCounterTest::drawDarkCurrentCanvas(void){
Int_t X0   = 300;  Int_t Y0   = 50;
Int_t DelX = 10;  Int_t DelY = 10;
Int_t X; Int_t Y;
Int_t Width = 600; Int_t Height = 600;
X = X0; Y = Y0;
TDatime *myTime = new TDatime();
Char_t space[2] = " ";
Char_t underline[2] = "_";
TString outDirectory = "graphics-DiCounters-2022Jun22/";
TString theTime = myTime->AsString();
if(cmjDiag != 0) cout << "**diCounterTest::drawDarkCurrentCanvas: time = "<< theTime.ReplaceAll(" ","_") <<endl;
c_darkCurrentA1 = new TCanvas("c_darkCurrentA1","Sipm Current A1",X,Y,Width,Height);
h_darkCurrentA1->Draw();
  if(printGraphicsFile != 0) c_darkCurrentA1->Print(outDirectory+"darkCurrentA1_"+theTime+".png");
X += DelX; Y += DelY;
c_darkCurrentA2 = new TCanvas("c_darkCurrentA2","Sipm Current A2",X,Y,Width,Height);
h_darkCurrentA2->Draw();
  if(printGraphicsFile != 0) c_darkCurrentA2->Print(outDirectory+"darkCurrentA2_"+theTime+".png");
X += DelX; Y += DelY;
c_darkCurrentA3 = new TCanvas("c_darkCurrentA3","Sipm Current A3",X,Y,Width,Height);
h_darkCurrentA3->Draw();
  if(printGraphicsFile != 0) c_darkCurrentA3->Print(outDirectory+"darkCurrentA3_"+theTime+".png");
X += DelX; Y += DelY;
c_darkCurrentA4 = new TCanvas("c_darkCurrentA4","Sipm Current A4",X,Y,Width,Height);
h_darkCurrentA4->Draw();
  if(printGraphicsFile != 0) c_darkCurrentA4->Print(outDirectory+"darkCurrentA4_"+theTime+".png");
X += DelX; Y += DelY;
c_darkCurrentB1 = new TCanvas("c_darkCurrentB1","Sipm Current B1",X,Y,Width,Height);
h_darkCurrentB1->Draw();
  if(printGraphicsFile != 0) c_darkCurrentB1->Print(outDirectory+"darkCurrentB1_"+theTime+".png");
X += DelX; Y += DelY;
c_darkCurrentB2 = new TCanvas("c_darkCurrentB2","Sipm Current B2",X,Y,Width,Height);
h_darkCurrentA2->Draw();
  if(printGraphicsFile != 0) c_darkCurrentB2->Print(outDirectory+"darkCurrentB2_"+theTime+".png");
X += DelX; Y += DelY;
c_darkCurrentB3 = new TCanvas("c_darkCurrentB3","Sipm Current B3",X,Y,Width,Height);
h_darkCurrentB3->Draw();
  if(printGraphicsFile != 0) c_darkCurrentB3->Print(outDirectory+"darkCurrentB3_"+theTime+".png");
X += DelX; Y += DelY;
c_darkCurrentB4 = new TCanvas("c_darkCurrentB4","Sipm Current B4",X,Y,Width,Height);
h_darkCurrentB4->Draw();
X += DelX; Y += DelY;
c_darkCurrentTemp = new TCanvas("c_darkCurrentTemp","Dark Current Temperature",X,Y,Width,Height);
  if(printGraphicsFile != 0) c_darkCurrentTemp->Print(outDirectory+"darkCurrentTemp_"+theTime+".png");
h_darkCurrentTemp->Draw();
X += DelX; Y += DelY;
c_darkCurrentSipmVoltage = new TCanvas("c_darkCurrentSipmVoltage","Dark CurrentSipm Voltage",X,Y,Width,Height);
h_darkCurrentSipmVoltage->Draw();
  if(printGraphicsFile != 0) c_darkCurrentSipmVoltage->Print(outDirectory+"darkCurrentSipmVoltage_"+theTime+".png");
}

//  --------------------------------------------------------------------
//  Run macro here....
void analyzeDiCounters(TString inFile = "DiCounters_2022Jun22_11_30_32_.root", Int_t tempPrint = 1, Int_t debugLevel = 0){
diCounterTest *myDiCounter = new diCounterTest(inFile,tempPrint, debugLevel);
//	Signal... Current with dicounters expoxed to light source.
myDiCounter -> bookCurrentHistograms();
myDiCounter -> setCurrentBranches();
myDiCounter -> fillCurrentHistograms();
myDiCounter -> drawCurrentCanvas();
//   Dark Current Analysis..
//myDiCounter -> bookDarkCurrentHistograms();
//myDiCounter -> setDarkCurrentBranches();
//myDiCounter -> fillDarkCurrentHistograms();
//myDiCounter -> drawDarkCurrentCanvas();
}

