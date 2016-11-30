#!/usr/bin/env python

from ROOT import *
import json, os, sys, math, getopt 
from CATTools.CatAnalyzer.histoHelper import *
gROOT.SetBatch(True)

gStyle.SetPalette(1)






def anaTree( tree ) :
  label="reco"
  c1 = makeCanvas("quality")
  h0 = getTH1("Efficiency of Quality ; Quality ; Eff.",[50,0,50], tree,"Solver","1")
  h1 = getTH1("Efficiency of Quality(AND) ; Quality ; Eff.",[50,0,50], tree,"Solver","abs(SolvedBJet_info.bjetPdgId[0])==5 && abs(SolvedBJet_info.bjetPdgId[1])==5")
  h2 = getTH1("Efficiency of Quality(OR) ; Quality ; Eff.",[50,0,50], tree,"Solver","abs(SolvedBJet_info.bjetPdgId[0])==5 || abs(SolvedBJet_info.bjetPdgId[1])==5")
  h1.Divide(h0)
  h1.SetLineColor(ROOT.kRed)
  h1.SetMarkerColor(ROOT.kRed)
  h2.Divide(h0)
  h2.SetLineColor(ROOT.kBlue)
  h2.SetMarkerColor(ROOT.kBlue)
  h2.SetMaximum(1.2)
  h2.SetMinimum(0)
  h2.Draw()
  h1.Draw("Same")
  c1.BuildLegend(0.3,0.2,0.8,0.3)
  c1.SaveAs("quality.png")

  c2 = makeCanvas("Top mass")
  h3 = getTH1("topMass",[200,50,250],tree,"top","1")
  f1 = TF1("BW",fBreitWigner,50,250)
  f1.SetParameter(0,1)
  f1.SetParameter(1,1)
  f1.SetParameter(2,1)
  #h3.Fit("BW","s")
  
  h3.Fit("gaus","s")
  print h3.GetBinCenter(h3.GetMaximumBin())
  h3.Draw()
  c2.SaveAs("topmass.png")

if __name__ == "__main__" :
  if len(sys.argv) != 2 :
    print "Wrong argument!"
    sys.exit(-1)
  else :
    file0 = TFile.Open(sys.argv[1])
    tree = file0.Get("cattree/reco_bjet_charge")
    anaTree(tree)
