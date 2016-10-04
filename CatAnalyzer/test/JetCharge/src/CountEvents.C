#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TTreeReader.h"
#include "TTreeReaderValue.h"


void CountEvents(const char* filename="cmskin_quality.root")
{
  gROOT->ProcessLine(".L tdrstyle.C");
  gROOT->ProcessLine("setTDRStyle();");
  std::cout<<"gStyle name : "<<gStyle->GetName()<<std::endl;
  // Variables used to store the data
  //Int_t totalSize = 0; // Sum of data size (in bytes) of all events

  // open the file
  TFile *f = TFile::Open(filename);
  if (f == 0) {
    // if we cannot open the file, print an error message and return immediatly
    printf("Error: cannot open data file.\n");
    return;
  }
  int xmax = 1000;
  TProfile* h1 = new TProfile("isJet1_bjet_all","Efficiency of bjet ; Quality ; Eff. of bjet",100,1,xmax);
  TProfile* h2 = new TProfile("isJet2_bjet_all","isbjet1_all",100,1,xmax);
  TProfile* h3 = new TProfile("isJet1or2_bjet_all","Efficiency of bjet1 or bjet2; Quality ; Eff. of bjet1 || bjet2",100,1,xmax);
  TProfile* h4 = new TProfile("isJet1and2_bjet_all","isbjet1_all",100,1,xmax);
  TProfile* h5 = new TProfile("isJet1_bjet_qcut","isbjet1_qcut",100,1,xmax);
  TProfile* h6 = new TProfile("isJet2_bjet_qcut","isbjet1_qcut",100,1,xmax);
  TProfile* h7 = new TProfile("isJet1or2_bjet_qcut","isbjet1_qcut",100,1,xmax);
  TProfile* h8 = new TProfile("isJet1and2_bjet_qcut","isbjet1_qcut",100,1,xmax);

  TH1F* h11   = new TH1F("Jet1-lepton pairing_all", "pair_j1l_all",11,-5,6);
  TH1F* h11_1 = new TH1F("Jet2-lepton pairing_all", "pair_j2l_all",11,-5,6);
  TH1F* h12   = new TH1F("Jet1-lepton pairing_qcut","pair_j1l_qcut",11,-5,6);
  TH1F* h12_1 = new TH1F("Jet2-lepton pairing_qcut", "pair_j2l_qcut",11,-5,6);

  TTreeReader myReader("qualityAna/KinSolverQuality", f);
  TTreeReaderArray<int> bjet_partonPdgId_all(myReader, "bjet_partonPdgId_all");
  TTreeReaderArray<int> bjet_partonPdgId_qcut(myReader, "bjet_partonPdgId_qcut");
  TTreeReaderArray<int> lepton_charge(myReader, "lepton_charge");
  TTreeReaderValue<Double_t> pair_quality_all(myReader,  "pair_quality_all.quality_all");
  TTreeReaderValue<Double_t> pair_quality_qcut(myReader, "pair_quality_qcut.quality_qcut");

  // Loop over all entries of the TTree or TChain.
  while (myReader.Next()) {
  double x = (*pair_quality_all)*1e5;
    if ( abs(bjet_partonPdgId_all[0])==5 || abs(bjet_partonPdgId_all[1])==5 ) h3->Fill(x,1);
    else h3->Fill(x,0);

    if ( abs(bjet_partonPdgId_all[0])==5 && abs(bjet_partonPdgId_all[1])==5 ) h4->Fill(x,1);
    else h4->Fill(x,0);

    if ( abs(bjet_partonPdgId_qcut[0])==5 || abs(bjet_partonPdgId_qcut[1])==5 ) h7->Fill(x,1);
    else h7->Fill(x,0);
  
    if ( abs(bjet_partonPdgId_qcut[0])==5 && abs(bjet_partonPdgId_qcut[1])==5 ) h8->Fill(x,1);
    else h8->Fill(x,0);
    
    int pair_j1_all = bjet_partonPdgId_all[0]*lepton_charge[0];
    int pair_j2_all = bjet_partonPdgId_all[1]*lepton_charge[1];
    int pair_j1_qcut = bjet_partonPdgId_qcut[0]*lepton_charge[0];
    int pair_j2_qcut = bjet_partonPdgId_qcut[1]*lepton_charge[1];

    if ( *pair_quality_all>0)  { 
      h11->Fill(pair_j1_all);
      h11_1->Fill(pair_j2_all);
    }
    if ( *pair_quality_qcut>0) {
      h12->Fill(pair_j1_qcut);
      h12_1->Fill(pair_j2_qcut);
    }



  }
  h3->SetLineColor(kRed);
  h3->SetMarkerColor(kRed);
  h4->SetLineColor(kRed);
  h4->SetMarkerColor(kRed);

  h7->SetLineColor(kBlue);
  h7->SetMarkerColor(kBlue);
  h8->SetLineColor(kBlue);
  h8->SetMarkerColor(kBlue);

  TCanvas* c1 = new TCanvas("comp_plot","compPlot");
  h3->Draw();
  h7->Draw("same");
  c1->SaveAs("compare_or.png");
    
  TCanvas* c2 = new TCanvas("co2","comparison plot2");
  h4->Draw();
  h8->Draw("same");
  c2->SaveAs("compare_and.png");

  TCanvas* c3 = new TCanvas("pdgId_jet1","pdgId_jet1");
  h11->SetLineColor(kRed);
  h11->SetMarkerColor(kRed);
  h12->SetLineColor(kBlue);
  h12->SetMarkerColor(kBlue);
  h11->Draw();
  h12->Draw("same");
  c3->SaveAs("pdgId_jet1_all_vs_qcut.png");

  TCanvas* c4 = new TCanvas("pdgId_jet2","pdgId_jet2");
  h11_1->SetLineColor(kRed);
  h11_1->SetMarkerColor(kRed);
  h12_1->SetLineColor(kBlue);
  h12_1->SetMarkerColor(kBlue);
  h11_1->Draw();
  h12_1->Draw("same");
  c4->SaveAs("pdgId_jet2_all_vs_qcut.png");

  TCanvas* c5 = new TCanvas("pdgId_jet1_norm","pdgId_jet1_norm");
  h11->Scale(1./h11->GetEntries());
  h12->Scale(1./h12->GetEntries());
  h11->Draw();
  h12->Draw("same");
  c5->SaveAs("pdgId_jet1_all_vs_qcut_norm.png");

  TCanvas* c6 = new TCanvas("pdgId_jet2","pdgId_jet2");
  h11_1->Scale(1./h11_1->GetEntries());
  h12_1->Scale(1./h12_1->GetEntries());
  h11_1->Draw();
  h12_1->Draw("same");
  c6->SaveAs("pdgId_jet2_all_vs_qcut_norm.png");
}

