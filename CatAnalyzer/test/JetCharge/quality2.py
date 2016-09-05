#!/usr/bin/env python

from ROOT import *
import json, os, sys, math, getopt 
from CATTools.CatAnalyzer.histoHelper import *
gROOT.SetBatch(True)

gStyle.SetPalette(1)


xmax=1000

def anaTree( tree ) :
  label="reco"

  matched_jet1_all = "abs(bjet_partonPdgId_all[0])==5"
  matched_jet1_qcut = "abs(bjet_partonPdgId_qcut[0])==5"
  matched_jet2_all = "abs(bjet_partonPdgId_all[1])==5"
  matched_jet2_qcut = "abs(bjet_partonPdgId_qcut[1])==5"

  matched_or_all = "abs(bjet_partonPdgId_all[0])==5 || abs(bjet_partonPdgId_all[1])==5"
  matched_or_qcut = "abs(bjet_partonPdgId_qcut[0])==5 || abs(bjet_partonPdgId_qcut[1])==5"
  matched_and_all = "abs(bjet_partonPdgId_all[0])==5 && abs(bjet_partonPdgId_all[1])==5"
  matched_and_qcut = "abs(bjet_partonPdgId_qcut[0])==5 && abs(bjet_partonPdgId_qcut[1])==5"

  matched_first_all = "bjet_partonPdgId_all[0]*lepton_charge[0]"
  matched_first_qcut = "bjet_partonPdgId_qcut[0]*lepton_charge[0]"
  
  pq_all_up = "pair_quality_all>0"
  pq_qcut_up = "pair_quality_qcut>0"
  
  c1 = makeCanvas("quality")



  h1 = getTH1("Quality for all jets", [100,1,xmax],tree,"pair_quality_all*1e5","pair_quality_all>0")
  h2 = getTH1("Quality for qcut jets",[100,1,xmax],tree,"pair_quality_qcut*1e5","1")
  h3 = getTH2("Quality vs Quality",[[100,1,xmax],[100,1,xmax]],tree,"pair_quality_qcut*1e5:pair_quality_all*1e5","1")

  h4 = getTH1("b Matched without qcut", [100,1,xmax],tree, "pair_quality_all*1e5",matched_or_all)
  h5 = getTH1("Quality for qcut jets",  [100,1,xmax],tree,"pair_quality_qcut*1e5",matched_or_qcut)

  h6 = getTH1("b Matched without qcut", [100,1,xmax],tree, "pair_quality_all*1e5",matched_and_all)
  h7 = getTH1("Quality for qcut jets",  [100,1,xmax],tree,"pair_quality_qcut*1e5",matched_and_qcut)

  h8 = getTH1("j1_pdgId_lq_no_qcut", [10,-5,6],tree, "bjet_partonPdgId_all[0]*lepton_charge[0]" ,pq_all_up)
  h9 = getTH1("j1_pdgId_lq_with_qcut",  [10,-5,6],tree, "bjet_partonPdgId_qcut[0]*lepton_charge[0]",pq_qcut_up)

  h10 = getTH1("j2_pdgId_lq_no_qcut", [10,-5,6],tree, "bjet_partonPdgId_all[1]*lepton_charge[1]",pq_all_up)
  h11 = getTH1("j2_pdgId_lq_with_qcut",  [10,-5,6],tree, "bjet_partonPdgId_qcut[1]*lepton_charge[1]",pq_qcut_up)

  h12= getTH1("j1_pdgId_no_qcut", [10,-5,6],tree, "bjet_partonPdgId_all[0] ",pq_all_up)
  h13= getTH1("j1_pdgId_with_qcut",  [10,-5,6],tree, "bjet_partonPdgId_qcut[0]",pq_qcut_up)

  h14 = getTH1("j2_pdgId_no_qcut", [10,-5,6],tree, "bjet_partonPdgId_all[1] ",pq_all_up)
  h15 = getTH1("j2_pdgId_with_qcut",  [10,-5,6],tree, "bjet_partonPdgId_qcut[1]",pq_qcut_up)

  h1.SetLineColor(ROOT.kRed)
  h1.SetMarkerColor(ROOT.kRed)
  h2.SetLineColor(ROOT.kBlue)
  h2.SetMarkerColor(ROOT.kBlue)
  #h2.SetMaximum(1.2)
  #h2.SetMinimum(0)
  h2.Draw()
  h1.Draw("Same")
  c1.BuildLegend(0.4,0.6,0.9,0.7)
  c1.SaveAs("pair_all_vs_qcut.png")

  c2 = makeCanvas("quality_versus")
  h3.Draw("colz")
  c2.SaveAs("pair_vs.png")
  
  h4.Divide(h1)  
  h5.Divide(h2)  
  
  h6.Divide(h1)
  h7.Divide(h2)

  h4.SetMaximum(1.2)
  h4.SetMinimum(0)
  h5.SetMaximum(1.2)
  h5.SetMinimum(0)
  h6.SetMaximum(1.2)
  h6.SetMinimum(0)
  h7.SetMaximum(1.2)
  h7.SetMinimum(0)

  h4.Fit("pol0","S")
  h5.Fit("pol0","S")
  h6.Fit("pol0","S")
  h7.Fit("pol0","S")


  c4 = makeCanvas("Efficiency for quality max")
  h4.SetMarkerColor(ROOT.kRed)
  h6.SetMarkerColor(ROOT.kBlue)
  h4.Draw()
  h6.Draw("same")
  

  c4.SaveAs("eff_max.png")

  c5 = makeCanvas("Efficiency for quality qcut")
  h5.SetMarkerColor(ROOT.kRed)
  h7.SetMarkerColor(ROOT.kBlue)
  h5.Draw()
  h7.Draw("same")
  c5.SaveAs("eff_qcut.png")

  c6 = makeCanvas("Eff for first jet_max")
  h8.SetMarkerColor(ROOT.kRed)
  h8.SetLineColor(ROOT.kRed)
  h9.SetMarkerColor(ROOT.kBlue)
  h9.SetLineColor(ROOT.kBlue)
 
  h8.Draw() 
  h9.Draw("same")
  c6.SaveAs("pdgId_lepCharge_jet1.png")

  c7 = makeCanvas("Norm for first jet")
  h8.Scale( 1/h8.Integral(-10,10))
  h9.Scale( 1/h9.Integral(-10,10))
  h8.Draw()
  h9.Draw("same")
  c7.SaveAs("pdgId_lepCharge_jet1_norm.png")

  c8 = makeCanvas("Eff for second jet_max")
  h10.SetMarkerColor(ROOT.kRed)
  h10.SetLineColor(ROOT.kRed)
  h11.SetMarkerColor(ROOT.kBlue)
  h11.SetLineColor(ROOT.kBlue)
 
  h10.Draw() 
  h11.Draw("same")
  c8.SaveAs("pdgId_lepCharge_jet2.png")

  c9 = makeCanvas("Norm for second jet")
  h10.Scale( 1/h10.Integral(-10,10))
  h11.Scale( 1/h11.Integral(-10,10))
  h10.Draw()
  h11.Draw("same")
  c9.SaveAs("pdgId_lepCharge_jet2_norm.png")

  c10 = makeCanvas("jet1_pdgId")
  h12.SetMarkerColor(ROOT.kRed)
  h12.SetLineColor(ROOT.kRed)
  h13.SetMarkerColor(ROOT.kBlue)
  h13.SetLineColor(ROOT.kBlue)
 
  h12.Draw() 
  h13.Draw("same")
  c10.SaveAs("pdgId_jet1.png")

  c11 = makeCanvas("Norm jet1_pdgId")
  h12.Scale( 1/h12.Integral(-10,10))
  h13.Scale( 1/h13.Integral(-10,10))
  h12.Draw()
  h13.Draw("same")
  c11.SaveAs("pdgId_jet1_norm.png")

  c12 = makeCanvas("jet2_pdgId")
  h14.SetMarkerColor(ROOT.kRed)
  h14.SetLineColor(ROOT.kRed)
  h15.SetMarkerColor(ROOT.kBlue)
  h15.SetLineColor(ROOT.kBlue)
 
  h14.Draw() 
  h15.Draw("same")
  c12.SaveAs("pdgId_jet2.png")

  c13 = makeCanvas("Norm jet2_pdgId")
  h14.Scale( 1/h14.Integral(-10,10))
  h15.Scale( 1/h15.Integral(-10,10))
  h14.Draw()
  h15.Draw("same")
  c13.SaveAs("pdgId_jet2_norm.png")

  print h1.Integral(1,101)
  print h2.Integral(1,101)




if __name__ == "__main__" :
  if len(sys.argv) != 2 :
    print "Wrong argument!"
    sys.exit(-1)
  else :
    file0 = TFile.Open(sys.argv[1])
    tree = file0.Get("qualityAna/KinSolverQuality")
    anaTree(tree)
