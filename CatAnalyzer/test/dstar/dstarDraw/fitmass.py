#!/usr/bin/env python
import ROOT, CATTools.CatAnalyzer.CMS_lumi, json, os, getopt, sys, copy
from CATTools.CatAnalyzer.histoHelper import *
import DYestimation
ROOT.gROOT.SetBatch(True)

ROOT.gSystem.Load("libRooFit")


def myGetPosMaxHist(hist, nNumBin):
  dMaxBinCont = -1048576.0
  nIdxBinMax = 0

  for i in range(nNumBin):
    dPointData = hist.GetBinContent(i)
    if dMaxBinCont < dPointData: 
      dMaxBinCont = dPointData
      nIdxBinMax = i

  return nIdxBinMax


# -- For half-Gaussian distribution
def myFitInvMassWithHalfGaussian(hist, suffix, binning):
  dSizeBin = 1.0 * ( binning[2] - binning[1] ) / binning[0]
  dXPeak = binning[1] + myGetPosMaxHist(hist, binning[0]) * dSizeBin
  dMaxFitRange = dXPeak + 4 * dSizeBin
  
  tf1 = ROOT.TF1("f1_fit","gaus", 0, dMaxFitRange)
  hist.Fit(tf1)
  
  x = ROOT.RooRealVar("invmass",hist.GetXaxis().GetTitle(), binning[1], binning[2])
  xfitarg = ROOT.RooArgList(x, "invmass")
  dh = ROOT.RooDataHist("dh","data histogram", xfitarg, hist)
  
  dSigma = tf1.GetParameter(2)
  dSigmaError = tf1.GetParError(2) * 10.0

  CB_mean   = ROOT.RooRealVar("mean","mean", dXPeak, dXPeak - dSizeBin, dXPeak + dSizeBin)
  CB_sigma  = ROOT.RooRealVar("sigma","sigma",dSigma, dSigma - dSigmaError, dSigma + dSigmaError)
  
  sig_pdf   = ROOT.RooGaussian("sig_fit","signal p.d.f",x, CB_mean, CB_sigma)
  model = sig_pdf
  
  fitResult = model.fitTo(dh, ROOT.RooFit.Extended(False), ROOT.RooFit.Save(), 
    ROOT.RooFit.Range(0, dMaxFitRange))
  
  top_mass_frame = x.frame()
  dh.plotOn(top_mass_frame)

  model.plotOn(top_mass_frame)
  model.plotOn(top_mass_frame, ROOT.RooFit.Components(ROOT.RooArgSet(sig_pdf)),
    ROOT.RooFit.LineColor(ROOT.kRed), ROOT.RooFit.LineStyle(ROOT.kDashed))
  
  return {"frame":top_mass_frame, "peak_val":CB_mean.getVal(), "peak_err":CB_mean.getError(), 
    "sigma_val":CB_sigma.getVal(), "sigma_err":CB_sigma.getError()}


# -- For Landau distribution
def myFitInvMassWithLandau(hist, suffix, binning):
  tf1 = ROOT.TF1("f1_fit","landau", binning[1], binning[2])
  hist.Fit(tf1)
  
  x = ROOT.RooRealVar("invmass",hist.GetXaxis().GetTitle(), binning[1], binning[2])
  xfitarg = ROOT.RooArgList(x, "invmass")
  dh = ROOT.RooDataHist("dh","data histogram", xfitarg, hist)
  
  dSigma = tf1.GetParameter(2)
  dSigmaError = tf1.GetParError(2) * 10.0

  CB_MPV    = ROOT.RooRealVar("mean" + suffix,"mean" + suffix, 
    tf1.GetParameter(1), binning[1], binning[2])
  CB_sigma  = ROOT.RooRealVar("sigma" + suffix,"sigma" + suffix, 
    dSigma, dSigma - dSigmaError, dSigma + dSigmaError)
  
  sig_pdf   = ROOT.RooLandau("sig_fit","signal p.d.f",x, CB_MPV, CB_sigma)
  model = sig_pdf
  
  fitResult = model.fitTo(dh, ROOT.RooFit.Extended(False), ROOT.RooFit.Save())
  
  top_mass_frame = x.frame()
  dh.plotOn(top_mass_frame)
  
  model.paramOn(top_mass_frame, ROOT.RooFit.Format("NELU", ROOT.RooFit.AutoPrecision(2)), 
    ROOT.RooFit.Layout(0.1, 0.4, 0.9))

  model.plotOn(top_mass_frame)
  model.plotOn(top_mass_frame, ROOT.RooFit.Components(ROOT.RooArgSet(sig_pdf)),
    ROOT.RooFit.LineColor(ROOT.kRed), ROOT.RooFit.LineStyle(ROOT.kDashed))
  
  return {"frame":top_mass_frame, "peak_val":CB_MPV.getVal(), "peak_err":CB_MPV.getError(), 
    "sigma_val":CB_sigma.getVal(), "sigma_err":CB_sigma.getError()}


def myFitInvMass(hist, suffix, binning):
  return myFitInvMassWithLandau(hist, suffix, binning)
  #return myFitInvMassWithHalfGaussian(hist, suffix, binning)


################################################################
## Reading the configuration file
################################################################
try:
  if len(sys.argv) is 1 : 
    print "Usage : %s [rootfilename]"
    sys.exit(2)

  fileDicHists = open(sys.argv[1])
  dicHists = json.load(fileDicHists)
  fileDicHists.close()
except IOError:
    print "Usage : %s [rootfilename]  # rootfilename must be correct"
    sys.exit(2)

################################################################
## Initializing the result root file
################################################################
rootHists = ROOT.TFile.Open(dicHists["rootfilename"])
rootFits = ROOT.TFile.Open("fittings_" + dicHists["rootfilename"],"RECREATE")

binning = dicHists["binning"]
x_name = dicHists["x_name"]
y_name = dicHists["y_name"]

ROOT.gStyle.SetOptFit(1111)

################################################################
##  Getting peaks of TT samples
################################################################
for strKey in dicHists.keys():
  if "type" not in dicHists[ strKey ] : continue
  if dicHists[ strKey ][ "type" ] not in ["TT_onlytt", "TT_withbkg", "data"] : continue
  
  # If str is missing, since strKey is in unicode type, it yields an error.
  histCurr = ROOT.TH1D(rootHists.Get(str(strKey)))
  
  strSuffix = ""
  if dicHists[ strKey ][ "type" ] in ["TT_onlytt", "TT_withbkg"] : 
    strSuffix = "_%0.1f"%(dicHists[ strKey ][ "mass" ])
  
  # -- Fitting by RooFit (no bkg)
  print ""
  print "#####################################################"
  print "### Fitting (%s) by RooFit is beginning"%(strKey)
  print "#####################################################"
  
  dicHists[ strKey ][ "fitres" ] = myFitInvMass(histCurr, strSuffix, binning)
  
  # -- Setting the name and shapes of histogram
  dicHists[ strKey ][ "fitres" ][ "frame" ].SetName(strKey)
  dicHists[ strKey ][ "fitres" ][ "frame" ].SetTitle(histCurr.GetTitle())
  
  setDefAxis(dicHists[ strKey ][ "fitres" ][ "frame" ].GetXaxis(), x_name, 1)
  setDefAxis(dicHists[ strKey ][ "fitres" ][ "frame" ].GetYaxis(), y_name, 1.2)
  dicHists[ strKey ][ "fitres" ][ "frame" ].SetMinimum(0)
  
  # -- Saving the histogram and the fitting curve
  rootFits.cd()
  dicHists[ strKey ][ "fitres" ][ "frame" ].Write()

  # -- Dumping
  print "------ Peak (no bkg) by RooFit : %f, Err : %f"%(dicHists[ strKey ][ "fitres" ]["peak_val"], 
    dicHists[ strKey ][ "fitres" ]["peak_err"])
  print "------      (sigma : %f, %f)"%(dicHists[ strKey ][ "fitres" ][ "sigma_val" ], 
    dicHists[ strKey ][ "fitres" ][ "sigma_err" ])

################################################################
##  Prepare to draw the linear plot
################################################################
dBinMinPeak = 164.0
dBinMaxPeak = 180.0
dSizeBin = 0.1

dDatMinPeak =  1048576.0
dDatMaxPeak = -1048576.0

for strKey in dicHists.keys() :
  if "type" not in dicHists[ strKey ] : continue
  if dicHists[ strKey ][ "type" ] not in ["TT_onlytt", "TT_withbkg"] : continue
  
  dDatVal = dicHists[ strKey ][ "fitres" ][ "peak_val" ]
  dDatErr = dicHists[ strKey ][ "fitres" ][ "peak_err" ]
  
  if dDatMinPeak > dDatVal - dDatErr : dDatMinPeak = dDatVal - dDatErr
  if dDatMaxPeak < dDatVal + dDatErr : dDatMaxPeak = dDatVal + dDatErr

dDatMean = ( dDatMaxPeak + dDatMinPeak ) / 2
dDatMinPeak = dDatMinPeak - ( dDatMean - dDatMinPeak ) * 1.6
dDatMaxPeak = dDatMaxPeak + ( dDatMaxPeak - dDatMean ) * 1.6
print "Range in linear plot : ", dDatMinPeak, dDatMean, dDatMaxPeak

################################################################
##  Plotting the linear plot by RooFit (without bkg)
################################################################
print "##### Fitting by RooFit (no bkg)"

histPeak_nb = ROOT.TH1D("histPeak_onlyTT", "Peaks (no bkg)", int(( dBinMaxPeak - dBinMinPeak ) / dSizeBin), dBinMinPeak, dBinMaxPeak)
histPeak_nb.SetLineColor(1)

for strKey in dicHists.keys() :
  if "type" not in dicHists[ strKey ] : continue
  if dicHists[ strKey ][ "type" ] != "TT_onlytt" : continue
  
  dMass = dicHists[ strKey ][ "mass" ]
  dDatVal = dicHists[ strKey ][ "fitres" ][ "peak_val" ]
  dDatErr = dicHists[ strKey ][ "fitres" ][ "peak_err" ]
  
  print dMass, "(" + strKey + ")", dDatVal, dDatErr
  
  nIdxBin = int(( dMass - dBinMinPeak ) / dSizeBin)
  histPeak_nb.SetBinContent(nIdxBin, dDatVal)
  histPeak_nb.SetBinError(nIdxBin, dDatErr)

histPeak_nb.SetMinimum(dDatMinPeak)
histPeak_nb.SetMaximum(dDatMaxPeak)

tf1 = ROOT.TF1("f1_peaks_RooFit_nobkg", "pol1", dBinMinPeak, dBinMaxPeak)
histPeak_nb.Fit(tf1)

setDefAxis(histPeak_nb.GetXaxis(), "M_{top} [GeV/c^2]", 1)
setDefAxis(histPeak_nb.GetYaxis(), x_name, 1.2)

rootFits.cd()
ROOT.gStyle.SetOptFit(1111)
histPeak_nb.Draw()
histPeak_nb.Write()

################################################################
##  Plotting the linear plot by RooFit
################################################################
print "##### Fitting by RooFit (bkg)"

histPeak = ROOT.TH1D("histPeak_withbkg", "Peaks", int(( dBinMaxPeak - dBinMinPeak ) / dSizeBin), dBinMinPeak, dBinMaxPeak)
histPeak.SetLineColor(1)

for strKey in dicHists.keys() :
  if "type" not in dicHists[ strKey ] : continue
  if dicHists[ strKey ][ "type" ] != "TT_withbkg" : continue
  
  dMass = dicHists[ strKey ][ "mass" ]
  dDatVal = dicHists[ strKey ][ "fitres" ][ "peak_val" ]
  dDatErr = dicHists[ strKey ][ "fitres" ][ "peak_err" ]
  
  print dMass, "(" + strKey + ")", dDatVal, dDatErr
  
  nIdxBin = int(( dMass - dBinMinPeak ) / dSizeBin)
  histPeak.SetBinContent(nIdxBin, dDatVal)
  histPeak.SetBinError(nIdxBin, dDatErr)

histPeak.SetMinimum(dDatMinPeak)
histPeak.SetMaximum(dDatMaxPeak)

tf1 = ROOT.TF1("f1_peaks_RooFit", "pol1", dBinMinPeak, dBinMaxPeak)
histPeak.Fit(tf1)

setDefAxis(histPeak.GetXaxis(), "M_{top} [GeV/c^2]", 1)
setDefAxis(histPeak.GetYaxis(), x_name, 1.2)

rootFits.cd()
ROOT.gStyle.SetOptFit(1111)
histPeak.Draw()
histPeak.Write()

################################################################
##  Everything is over; closing the file
################################################################

rootFits.Write()
rootFits.Close()
rootHists.Close()

print ''
print ''
