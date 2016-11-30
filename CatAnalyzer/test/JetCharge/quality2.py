#!/usr/bin/env python

from ROOT import *
import json, os, sys, math, getopt 
from CATTools.CatAnalyzer.histoHelper import *
gROOT.SetBatch(True)

gStyle.SetPalette(1)


xmax=100

def anaTree( tree ) :
  label="reco"

  pq_all_up = "(pair_quality_all>0)"
  pq_qcut_up = "(pair_quality_qcut>0)"

  matched_jet1_all = "&&(abs(bjet_partonPdgId_all[0])==5)"
  matched_jet1_qcut = "&&(abs(bjet_partonPdgId_qcut[0])==5)"
  matched_jet2_all = "&&(abs(bjet_partonPdgId_all[1])==5)"
  matched_jet2_qcut = "&&(abs(bjet_partonPdgId_qcut[1])==5)"

  matched_or_all = "&&(abs(bjet_partonPdgId_all[0])==5 || abs(bjet_partonPdgId_all[1])==5)"
  matched_or_qcut = "&&(abs(bjet_partonPdgId_qcut[0])==5 || abs(bjet_partonPdgId_qcut[1])==5)"
  matched_and_all = "&&(abs(bjet_partonPdgId_all[0])==5 && abs(bjet_partonPdgId_all[1])==5)"
  matched_and_qcut = "&&(abs(bjet_partonPdgId_qcut[0])==5 && abs(bjet_partonPdgId_qcut[1])==5)"

  matched_first_all = "&&(bjet_partonPdgId_all[0]*lepton_charge[0])"
  matched_first_qcut = "&&(bjet_partonPdgId_qcut[0]*lepton_charge[0])"
  

  largeCharge_all = "&&(lepton_charge[0]*bjet_charge_all[0]<-1)"
  largeCharge_qcut = "&&(lepton_charge[0]*bjet_charge_qcut[0]<-1)"
  
  diffCharge_all = "&&( abs(bjet_charge_all[0]-bjet_charge_all[1])>1)" 
  diffCharge_qcut = "&&( abs(bjet_charge_qcut[0]-bjet_charge_qcut[1])>1)" 
 
  c1 = makeCanvas("quality")



  h1 = getTH1("Quality for all jets", [100,1,xmax],tree,"pair_quality_all*1e5",pq_all_up)
  h1_1 = getTH1("Quality for all jets_largeCharge", [100,1,xmax],tree,"pair_quality_all*1e5",pq_all_up+largeCharge_all)
  h1_2 = getTH1("Quality for all jets_diffCharge", [100,1,xmax],tree,"pair_quality_all*1e5",pq_all_up+diffCharge_all)

  h2 = getTH1("Quality for qcut jets",[100,1,xmax],tree,"pair_quality_qcut*1e5",pq_qcut_up)
  h2_1 = getTH1("Quality for qcut jets_largeCharge",[100,1,xmax],tree,"pair_quality_qcut*1e5",pq_qcut_up+largeCharge_qcut)
  h2_2 = getTH1("Quality for qcut jets_diffCharge",[100,1,xmax],tree,"pair_quality_qcut*1e5",pq_qcut_up+diffCharge_qcut)


  h3 = getTH2("Quality vs Quality",[[100,1,xmax],[100,1,xmax]],tree,"pair_quality_qcut*1e5:pair_quality_all*1e5","pair_quality_qcut*pair_quality_all>0")

  h4 = getTH1("Correct_pair[OR]_for_all", [100,1,xmax],tree, "pair_quality_all*1e5",  pq_all_up   +matched_or_all)
  h4_1 = getTH1("Correct_pair[OR]_for_all_largeCharge", [100,1,xmax],tree, "pair_quality_all*1e5",  pq_all_up   +matched_or_all+largeCharge_all)
  h4_2 = getTH1("Correct_pair[OR]_for_all_diffCharge", [100,1,xmax],tree, "pair_quality_all*1e5",  pq_all_up   +matched_or_all+diffCharge_all)

  h5 = getTH1("Correct_pair[OR]_for_qcut",  [100,1,xmax],tree,"pair_quality_qcut*1e5",pq_qcut_up  +matched_or_qcut)
  h5_1 = getTH1("Correct_pair[OR]_for_qcut_largeCharge",  [100,1,xmax],tree,"pair_quality_qcut*1e5",pq_qcut_up  +matched_or_qcut+largeCharge_qcut)
  h5_2 = getTH1("Correct_pair[OR]_for_qcut_diffCharge",  [100,1,xmax],tree,"pair_quality_qcut*1e5",pq_qcut_up  +matched_or_qcut+diffCharge_qcut)

  h6 = getTH1("Candrect_pair[AND]_for_all", [100,1,xmax],tree, "pair_quality_all*1e5",  pq_all_up   +matched_and_all)
  h6_1 = getTH1("Candrect_pair[AND]_for_all_largeCharge", [100,1,xmax],tree, "pair_quality_all*1e5",  pq_all_up   +matched_and_all+largeCharge_all)
  h6_2 = getTH1("Candrect_pair[AND]_for_all_diffCharge", [100,1,xmax],tree, "pair_quality_all*1e5",  pq_all_up   +matched_and_all+diffCharge_all)

  h7 = getTH1("Candrect_pair[AND]_for_qcut",  [100,1,xmax],tree,"pair_quality_qcut*1e5",pq_qcut_up  +matched_and_qcut)
  h7_1 = getTH1("Candrect_pair[AND]_for_qcut_largeCharge",  [100,1,xmax],tree,"pair_quality_qcut*1e5",pq_qcut_up  +matched_and_qcut+largeCharge_qcut)
  h7_2 = getTH1("Candrect_pair[AND]_for_qcut_diffCharge",  [100,1,xmax],tree,"pair_quality_qcut*1e5",pq_qcut_up  +matched_and_qcut+diffCharge_qcut)

  h8   = getTH1("j1_pdgId_lq_all", [10,-5,6],tree, "bjet_partonPdgId_all[0]*lepton_charge[0]" ,pq_all_up)
  h8_1 = getTH1("j1_pdgId_lq_all_only_large_charge", [10,-5,6],tree, "bjet_partonPdgId_all[0]*lepton_charge[0]" ,pq_all_up + largeCharge_all)
  h8_2 = getTH1("j1_pdgId_lq_all_only_large_diffcharge", [10,-5,6],tree, "bjet_partonPdgId_all[0]*lepton_charge[0]" ,pq_all_up + diffCharge_all)

  h9     = getTH1("j1_pdgId_lq_qcut",  [10,-5,6],tree, "bjet_partonPdgId_qcut[0]*lepton_charge[0]",pq_qcut_up)
  h9_1   = getTH1("j1_pdgId_lq_qcut_only_large_charge",  [10,-5,6],tree, "bjet_partonPdgId_qcut[0]*lepton_charge[0]"  ,pq_qcut_up+largeCharge_qcut)
  h9_2 = getTH1("j1_pdgId_lq_qcut_only_large_diffcharge", [10,-5,6],tree, "bjet_partonPdgId_qcut[0]*lepton_charge[0]" ,pq_qcut_up+ diffCharge_qcut)

  h10 = getTH1("j2_pdgId_lq_no_qcut", [10,-5,6],tree, "bjet_partonPdgId_all[1]*lepton_charge[1]",pq_all_up)
  h11 = getTH1("j2_pdgId_lq_with_qcut",  [10,-5,6],tree, "bjet_partonPdgId_qcut[1]*lepton_charge[1]",pq_qcut_up)

  h12= getTH1("j1_pdgId_no_qcut", [10,-5,6],tree, "bjet_partonPdgId_all[0] ",pq_all_up)
  h13= getTH1("j1_pdgId_with_qcut",  [10,-5,6],tree, "bjet_partonPdgId_qcut[0]",pq_qcut_up)

  h14 = getTH1("j2_pdgId_no_qcut", [10,-5,6],tree, "bjet_partonPdgId_all[1] ",pq_all_up)
  h15 = getTH1("j2_pdgId_with_qcut",  [10,-5,6],tree, "bjet_partonPdgId_qcut[1]",pq_qcut_up)

  h16 = getTH1("pdgId_all",[5,0,6],tree,"abs(bjet_partonPdgId_all)",pq_all_up)
  h17 = getTH1("pdgId_qcut",[5,0,6],tree,"abs(bjet_partonPdgId_qcut)",pq_qcut_up)

  h18 = getTH1("bjet_charge",[11,-5,6],tree,"bjet_charge_all",pq_all_up+"&&bjet_partonPdgId_all==5")
  h19 = getTH1("bbarjet_charge",[11,-5,6],tree,"bjet_charge_all",pq_all_up+"&&bjet_partonPdgId_all==-5")
  h20 = getTH1("failedjet_charge",[11,-5,6],tree,"bjet_charge_all",pq_all_up+"&&bjet_partonPdgId_all==0")



  h1.SetLineColor(ROOT.kRed)
  h1.SetMarkerColor(ROOT.kRed)
  h1_1.SetLineColor(ROOT.kMagenta)
  h1_1.SetMarkerColor(ROOT.kMagenta)
  h1_2.SetLineColor(ROOT.kOrange)
  h1_2.SetMarkerColor(ROOT.kOrange)


  h2.SetLineColor(ROOT.kBlue)
  h2.SetMarkerColor(ROOT.kBlue)
  h2_1.SetLineColor(ROOT.kBlack)
  h2_1.SetMarkerColor(ROOT.kBlack)
  h2_2.SetLineColor(ROOT.kCyan)
  h2_2.SetMarkerColor(ROOT.kCyan)

  h4.SetLineColor(ROOT.kRed)
  h4.SetMarkerColor(ROOT.kRed)
  h4_1.SetLineColor(ROOT.kMagenta)
  h4_1.SetMarkerColor(ROOT.kMagenta)
  h4_2.SetLineColor(ROOT.kOrange)
  h4_2.SetMarkerColor(ROOT.kOrange)


  h5.SetLineColor(ROOT.kBlue)
  h5.SetMarkerColor(ROOT.kBlue)
  h5_1.SetLineColor(ROOT.kBlack)
  h5_1.SetMarkerColor(ROOT.kBlack)
  h5_2.SetLineColor(ROOT.kCyan)
  h5_2.SetMarkerColor(ROOT.kCyan)

  h6.SetLineColor(ROOT.kRed)
  h6.SetMarkerColor(ROOT.kRed)
  h6_1.SetLineColor(ROOT.kMagenta)
  h6_1.SetMarkerColor(ROOT.kMagenta)
  h6_2.SetLineColor(ROOT.kOrange)
  h6_2.SetMarkerColor(ROOT.kOrange)


  h7.SetLineColor(ROOT.kBlue)
  h7.SetMarkerColor(ROOT.kBlue)
  h7_1.SetLineColor(ROOT.kBlack)
  h7_1.SetMarkerColor(ROOT.kBlack)
  h7_2.SetLineColor(ROOT.kCyan)
  h7_2.SetMarkerColor(ROOT.kCyan)

  h1.Draw()
  h1_1.Draw("same")
  h1_2.Draw("same")
  h2.Draw("same")
  h2_1.Draw("same")
  h2_2.Draw("same")

  c1.BuildLegend(0.4,0.6,0.9,0.7)
  c1.SaveAs("pair_all_vs_qcut.png")

  c2 = makeCanvas("quality_versus")
  h3.Draw("colz")
  c2.SaveAs("pair_vs.png")
  
  
  h4.Divide(h1)  
  h4_1.Divide(h1_1)  
  h4_2.Divide(h1_2)  

  h5.Divide(h2)  
  h5_1.Divide(h2_1)  
  h5_2.Divide(h2_2)  

  h6.Divide(h1)  
  h6_1.Divide(h1_1)  
  h6_2.Divide(h1_2)  

  h7.Divide(h2)  
  h7_1.Divide(h2_1)  
  h7_2.Divide(h2_2)  
  

  h4.SetMaximum(1.2)
  h4.SetMinimum(0.5)
  h6.SetMaximum(0.8)
  h6.SetMinimum(0.)

  h4.Fit("pol0","S")
  h5.Fit("pol0","S")
  h6.Fit("pol0","S")
  h7.Fit("pol0","S")


  c4 = makeCanvas("Efficiency for quality OR")
  h4.Draw()
  h4_1.Draw("same")
  h4_2.Draw("same")
  h5.Draw("same")
  h5_1.Draw("same")
  h5_2.Draw("same")
  c4.BuildLegend()
  c4.SaveAs("eff_all.png")

  c5 = makeCanvas("Efficiency for quality AND")
  h6.Draw()
  h6_1.Draw("same")
  h6_2.Draw("same")
  h7.Draw("same")
  h7_1.Draw("same")
  h7_2.Draw("same")
  c5.BuildLegend()
  c5.SaveAs("eff_qcut.png")



  c6 = makeCanvas("Eff for first jet_max")
  h8.SetMarkerColor(ROOT.kRed)
  h8.SetLineColor(ROOT.kRed)
  h8_1.SetMarkerColor(ROOT.kMagenta)
  h8_1.SetLineColor(ROOT.kMagenta)
  h8_2.SetMarkerColor(ROOT.kOrange)
  h8_2.SetLineColor(ROOT.kOrange)

  h9.SetMarkerColor(ROOT.kBlue)
  h9.SetLineColor(ROOT.kBlue)
  h9_1.SetMarkerColor(ROOT.kBlack)
  h9_1.SetLineColor(ROOT.kBlack)
  h9_2.SetMarkerColor(ROOT.kCyan)
  h9_2.SetLineColor(ROOT.kCyan)

  h8.Draw() 
  h8_1.Draw("same") 
  h8_2.Draw("same") 
  h9.Draw("same")
  h9_1.Draw("same")
  h9_2.Draw("same")
  c6.BuildLegend()
  c6.SaveAs("pdgId_lepCharge_jet1.png")

  c7 = makeCanvas("Norm for first jet")
  h8.Scale( 1/h8.Integral(-10,10))
  h8_1.Scale( 1/h8_1.Integral(-10,10))
  h8_2.Scale( 1/h8_2.Integral(-10,10))
  h9.Scale( 1/h9.Integral(-10,10))
  h9_1.Scale( 1/h9_1.Integral(-10,10))
  h9_2.Scale( 1/h9_2.Integral(-10,10))
  h8.SetMaximum(1.0) 
  h8.Draw()
  h8_1.Draw("same")
  h8_2.Draw("same")
  h9.Draw("same")
  h9_1.Draw("same")
  h9_2.Draw("same")

  c7.BuildLegend()
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


  c14 = makeCanvas("cc")
  h16.SetMarkerColor(ROOT.kRed)
  h16.SetLineColor(ROOT.kRed)
  h17.SetMarkerColor(ROOT.kBlue)
  h17.SetLineColor(ROOT.kBlue)
  h16.Draw()
  h17.Draw("same")
  c14.SaveAs("pdgId_vs_vs.png")

  c15 = makeCanvas("cc_norm")
  h16.Scale(1./h16.GetEntries())
  h17.Scale(1./h17.GetEntries())
  h16.Draw()
  h17.Draw("same")
  c15.SaveAs("pdgId_vs_vs_norm.png")

  c16 = makeCanvas("Charge distribution")
  h18.SetFillColor(ROOT.kRed)
  h19.SetFillColor(ROOT.kBlue)
  h20.SetFillColor(ROOT.kBlack)

  h18.SetLineColor(ROOT.kRed)
  h19.SetLineColor(ROOT.kBlue)
  h20.SetLineColor(ROOT.kBlack)

  h18.SetFillStyle(3004)
  h19.SetFillStyle(3005)
  h20.SetFillStyle(3006)

  h18.Draw("hist")
  h19.Draw("hist same")
  h20.Draw("hist same")
  #c16.BuildLegend()
  c16.SaveAs("charge_dist.png") 

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
