#!/usr/bin/env python

from ROOT import *
import json, os, sys, math, getopt 
from CATTools.CatAnalyzer.histoHelper import *
gROOT.SetBatch(True)

gStyle.SetPalette(1)

def loopTree( tree ) :
  h1 = getTH1("b Matched without qcut", [50,1,51],tree,"pair_quality_all*1e5",matched_or)

  for event in tree :
    pass
    #print event.pair_quality_all*1e5


def anaTree( tree ) :
  label="reco"
  matched_or_all = "abs(bjet_partonPdgId_all[0])==5 || abs(bjet_partonPdgId_all[1])==5"
  matched_or_qcut = "abs(bjet_partonPdgId_qcut[0])==5 || abs(bjet_partonPdgId_qcut[1])==5"
  matched_and_all = "abs(bjet_partonPdgId_all[0])==5 && abs(bjet_partonPdgId_all[1])==5"
  matched_and_qcut = "abs(bjet_partonPdgId_qcut[0])==5 && abs(bjet_partonPdgId_qcut[1])==5"

  matched_first_all = "bjet_partonPdgId_all[0]*lepton_charge[0]"
  matched_first_qcut = "bjet_partonPdgId_qcut[0]*lepton_charge[0]"
  
  c1 = makeCanvas("quality")

  h1 = getTH1("Quality for all jets", [100,1,101],tree,"pair_quality_all*1e5","1")
  h2 = getTH1("Quality for qcut jets",[100,1,101],tree,"pair_quality_qcut*1e5","1")
  h3 = getTH2("Quality vs Quality",[[100,1,101],[100,1,101]],tree,"pair_quality_qcut*1e5:pair_quality_all*1e5","1")

  h4 = getTH1("b Matched without qcut", [100,1,101],tree, "pair_quality_all*1e5",matched_or_all)
  h5 = getTH1("Quality for qcut jets",  [100,1,101],tree,"pair_quality_qcut*1e5",matched_or_qcut)

  h6 = getTH1("b Matched without qcut", [100,1,101],tree, "pair_quality_all*1e5",matched_and_all)
  h7 = getTH1("Quality for qcut jets",  [100,1,101],tree,"pair_quality_qcut*1e5",matched_and_qcut)

  h8 = getTH1("b Matched without qcut", [3,-1,2],tree, "bjet_partonPdgId_all[0]/5*lepton_charge[0]","1")
  h9 = getTH1("Quality for qcut jets",  [3,-1,2],tree, "bjet_partonPdgId_qcut[0]/5*lepton_charge[0]","1")


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
  c6.SaveAs("pdgId.png")



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
    #loopTree(tree)
