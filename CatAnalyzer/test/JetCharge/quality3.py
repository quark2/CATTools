#!/usr/bin/env python

from ROOT import *
import json, os, sys, math, getopt 
from CATTools.CatAnalyzer.histoHelper import *
gROOT.SetBatch(True)

gStyle.SetPalette(1)


xmax=100

def anaTree( tree ) :
  label="reco"

  pq_up = "(quality>0)"

  matched_jet1 = "&&(abs(bjet_partonPdgId[0])==5)"
  matched_jet2 = "&&(abs(bjet_partonPdgId[1])==5)"

  matched_or = "&&(abs(bjet_partonPdgId[0])==5 || abs(bjet_partonPdgId[1])==5)"
  matched_and = "&&(abs(bjet_partonPdgId[0])==5 && abs(bjet_partonPdgId[1])==5)"

  matched_first = "&&(bjet_partonPdgId[0]*lep_charge[0])"
  

  largeCharge = "&&(lep_charge[0]*bjet_charge[0]<-1)"
  
  diffCharge = "&&( abs(bjet_charge[0]-bjet_charge[1])>1)" 

  btagged = "&&(bjet_btag[0]&&bjet_btag[1])"

 

  h1 = getTH1("Quality", [100,1,xmax],tree,"quality*1e5",pq_up)
  h1_1 = getTH1("Quality with largeCharge", [100,1,xmax],tree,"quality*1e5",pq_up+largeCharge)
  h1_2 = getTH1("Quality with diffCharge", [100,1,xmax],tree,"quality*1e5",pq_up+diffCharge)
  h2 = getTH1("Efficiency [OR]", [100,1,xmax],tree,"quality*1e5",pq_up+matched_or)
  h2_1 = getTH1("Efficiency [OR] with largeCharge", [100,1,xmax],tree,"quality*1e5",pq_up+largeCharge+matched_or)
  h2_2 = getTH1("Efficiency [OR] with diffCharge", [100,1,xmax],tree,"quality*1e5",pq_up+diffCharge+matched_or)




  c1 = makeCanvas("Quality for matched [or] for all")
  h2.SetMarkerColor(ROOT.kRed)
  h2.SetLineColor(ROOT.kRed)
  h2_1.SetMarkerColor(ROOT.kMagenta)
  h2_1.SetLineColor(ROOT.kMagenta)
  h2_2.SetMarkerColor(ROOT.kOrange)
  h2_2.SetLineColor(ROOT.kOrange)

  h2.Draw() 
  h2_1.Draw("same") 
  h2_2.Draw("same") 
  c1.BuildLegend()
  c1.SaveAs("quality_dist_or_all.png")

  c2 = makeCanvas("Eff for matched [or] for all")
  h2.Divide(h1)
  h2_1.Divide(h1_1)
  h2_2.Divide(h1_2)

  h2.Draw() 
  h2_1.Draw("same") 
  h2_2.Draw("same") 
  c2.BuildLegend()
  c2.SaveAs("eff_dist_or_all.png")


if __name__ == "__main__" :
  if len(sys.argv) != 2 :
    print "Wrong argument!"
    sys.exit(-1)
  else :
    file0 = TFile.Open(sys.argv[1])
    tree = file0.Get("qualityAna/KinSolverQualityForAllJet")
    anaTree(tree)
