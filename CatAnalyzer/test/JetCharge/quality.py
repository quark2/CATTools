#!/usr/bin/env python

from ROOT import *
import json, os, sys, math, getopt 
from CATTools.CatAnalyzer.histoHelper import *
gROOT.SetBatch(True)

gStyle.SetPalette(1)

def anaTree( tree ) :
  label="reco"
  c1 = makeCanvas("quality")

  cut = "lepton_charge[0]*(bjet_charge[0]-bjet_charge[1])<0"
  h0 = getTH1("Efficiency of Quality for original ; Quality ; Eff.",[50,0,50], tree,"pair_quality*1e5","1")
  h0_1 = getTH1("Efficiency of Quality for original with charge cut; Quality ; Eff.",[50,0,50], tree,"pair_quality*1e5","%s"%(cut))
  h1 = getTH1("Efficiency of Quality(AND) ; Quality ; Eff.",[50,0,50], tree,"pair_quality*1e5","abs(bjet_partonPdgId[0])==5 && abs(bjet_partonPdgId[1])==5")
  h2 = getTH1("Efficiency of Quality(OR)  ; Quality ; Eff.",[50,0,50], tree,"pair_quality*1e5","abs(bjet_partonPdgId[0])==5 || abs(bjet_partonPdgId[1])==5")
  h3 = getTH1("Efficiency of Quality(AND) with chargeCut ; Quality ; Eff.",[50,0,50], tree,"pair_quality*1e5","%s&&(abs(bjet_partonPdgId[0])==5 && abs(bjet_partonPdgId[1])==5)"%cut)
  h4 = getTH1("Efficiency of Quality(OR) with chargeCut  ; Quality ; Eff.",[50,0,50], tree,"pair_quality*1e5","%s&&(abs(bjet_partonPdgId[0])==5 || abs(bjet_partonPdgId[1])==5)"%cut)

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

  h3.Divide(h0_1)
  h3.SetLineColor(ROOT.kMagenta)
  h3.SetMarkerColor(ROOT.kMagenta)
  h4.Divide(h0_1)
  h4.SetLineColor(ROOT.kOrange)
  h4.SetMarkerColor(ROOT.kOrange)
  h3.Draw("Same")
  h4.Draw("Same")


  c1.BuildLegend(0.3,0.2,0.8,0.3)
  c1.SaveAs("pair_quality.png")

  """
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
  """

if __name__ == "__main__" :
  if len(sys.argv) != 2 :
    print "Wrong argument!"
    sys.exit(-1)
  else :
    file0 = TFile.Open(sys.argv[1])
    tree = file0.Get("qualityAna/KinSolverQuality")
    anaTree(tree)
