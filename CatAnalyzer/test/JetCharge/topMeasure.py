#!/usr/bin/env python

from ROOT import *
import json, os, sys, math, getopt 
from CATTools.CatAnalyzer.histoHelper import *
gROOT.SetBatch(True)

gStyle.SetPalette(1)

def anaTree( tree ) :
  label="reco"
  c1 = makeCanvas("quality")
  h0 = getTH1("Efficiency of Quality ; Quality ; Eff.",[100,0,50], tree,"Solver","1")
  h1 = getTH1("Efficiency of Quality ; Quality ; Eff.(And)",[100,0,50], tree,"Solver","abs(SolvedBJet_info.bjetPdgId[0])==5 && abs(SolvedBJet_info.bjetPdgId[1])==5")
  h2 = getTH1("Efficiency of Quality ; Quality ; Eff.(Or)",[100,0,50], tree,"Solver","abs(SolvedBJet_info.bjetPdgId[0])==5 || abs(SolvedBJet_info.bjetPdgId[1])==5")
  h1.Divide(h0)
  h1.SetLineColor(ROOT.kRed)
  h2.Divide(h0)
  h2.SetLineColor(ROOT.kBlue)
  h1.Draw()
  h2.Draw("Same")
  c1.SaveAs("quality.png")

  c2 = makeCanvas("Top mass")
  h3 = getTH1("",[],tree,"","")


if __name__ == "__main__" :
  if len(sys.argv) != 2 :
    print "Wrong argument!"
    sys.exit(-1)
  else :
    file0 = TFile.Open(sys.argv[1])
    tree = file0.Get("cattree/reco_bjet_charge")
    anaTree(tree)
