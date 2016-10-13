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


# -- For Landau distribution
def myFitInvMass(hist, binning):
  tf1 = ROOT.TF1("f1_fit","landau", binning[1], binning[2])
  hist.Fit(tf1)
  
  x = ROOT.RooRealVar("invmass",hist.GetXaxis().GetTitle(), binning[1], binning[2])
  xfitarg = ROOT.RooArgList(x, "invmass")
  dh = ROOT.RooDataHist("dh","data histogram", xfitarg, hist)
  
  dSigma = tf1.GetParameter(2)
  dSigmaError = tf1.GetParError(2) * 10.0

  CB_MPV    = ROOT.RooRealVar("mean","mean", tf1.GetParameter(1), binning[1], binning[2])
  CB_sigma  = ROOT.RooRealVar("sigma","sigma",dSigma, dSigma - dSigmaError, dSigma + dSigmaError)
  
  sig_pdf   = ROOT.RooLandau("sig_fit","signal p.d.f",x, CB_MPV, CB_sigma)
  model = sig_pdf
  
  fitResult = model.fitTo(dh, ROOT.RooFit.Extended(False), ROOT.RooFit.Save())
  
  top_mass_frame = x.frame()
  dh.plotOn(top_mass_frame)

  model.plotOn(top_mass_frame)
  model.plotOn(top_mass_frame, ROOT.RooFit.Components(ROOT.RooArgSet(sig_pdf)),
    ROOT.RooFit.LineColor(ROOT.kRed), ROOT.RooFit.LineStyle(ROOT.kDashed))
  
  return {"frame":top_mass_frame, "peak_val":CB_MPV.getVal(), "peak_err":CB_MPV.getError(), 
    "sigma_val":CB_sigma.getVal(), "sigma_err":CB_sigma.getError()}


datalumi = 15.92 # Run2016 B & C & D & E, v8-0-1 (F and latters cannot be used; ICHEP)
CMS_lumi.lumi_sqrtS = "%.1f fb^{-1}, #sqrt{s} = 13 TeV"%(datalumi)
datalumi = datalumi*1000 # due to fb

#topMassList = ['TT_powheg_mtop1665','TT_powheg_mtop1695','TT_powheg_mtop1715','TT_powheg_mtop1735','TT_powheg_mtop1755','TT_powheg_mtop1785','TT_powheg']
topMassList = ['TT_powheg_mtop1695','TT_powheg_mtop1755','TT_powheg'] # it will be filled fully
mcfilelist = ['WJets', 'SingleTbar_tW', 'SingleTop_tW', 'ZZ', 'WW', 'WZ', 'DYJets', 'DYJets_10to50']
rdfilelist = ['MuonEG_Run2016','DoubleEG_Run2016','DoubleMuon_Run2016']
#rootfileDir = "/xrootd/store/user/tt8888tt/v763_desy/TtbarDiLeptonAnalyzer_"
#rootfileDir = "/cms/scratch/geonmo/for2016KPS_Ana/src/CATTools/CatAnalyzer/test/cattools/cattree_"
rootfileDir = "/xrootd/store/user/quark2930/dilepton_mass_v801_16092901/cattree_"
channel_name = ['Combined', 'MuEl', 'ElEl', 'MuMu']

dMassNomial = 173.07

datasets = json.load(open("%s/src/CATTools/CatAnalyzer/data/dataset/dataset.json" % os.environ['CMSSW_BASE']))

################################################################
## defalts
################################################################
step = 1
channel = 3
cut = 'tri!=0&&filtered==1'
# In DYJet, genweight yields negative value in histogram(!!!)
weight = 'genweight*puweight*mueffweight*eleffweight*tri*topPtWeight'
binning = [60, 20, 320]
plotvar = 'll_m'
x_name = 'mass [GeV]'
y_name = 'Events'
dolog = False
overflow = False
binNormalize = False
suffix = ''

################################################################
## get input
################################################################
try:
    opts, args = getopt.getopt(sys.argv[1:],"hdnoc:w:b:p:x:y:a:s:f:",["binNormalize","overflow","cut","weight","binning","plotvar","x_name","y_name","dolog","channel","step","suffix"])
except getopt.GetoptError:          
    print 'Usage : ./.py -c <cut> -w <weight> -b <binning> -p <plotvar> -x <x_name> -y <y_name> -d <dolog> -f <suffix>'
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print 'Usage : ./topDraw.py -c <cut> -w <weight> -b <binning> -p <plotvar> -x <x_name> -y <y_name> -d <dolog> -f <suffix>'
        sys.exit()
    elif opt in ("-c", "--cut"):
        #cut = arg
        cut = "%s&&%s"%(cut,arg)
    elif opt in ("-a", "--channel"):
        channel = int(arg)
    elif opt in ("-s", "--step"):
        step = int(arg)
    elif opt in ("-w", "--weight"):
        weight = arg
    elif opt in ("-b", "--binning"):
        binning = eval(arg)
    elif opt in ("-p", "--plotvar"):
        plotvar = arg
    elif opt in ("-x", "--x_name"):
        x_name = arg
    elif opt in ("-y", "--y_name"):
        y_name = arg
    elif opt in ("-d", "--dolog"):
        dolog = True
    elif opt in ("-o", "--overflow"):
        overflow = True
    elif opt in ("-n", "--binNormalize"):
        binNormalize = True
    elif opt in ("-f", "--suffix"):
        suffix = "_"+arg

tname = "cattree/nom"

################################################################
## cut define
################################################################
#if   channel == 1: ttother_tcut = "!(gen_partonChannel==2 && ((gen_partonMode1==1 && gen_partonMode2==2) || (gen_partonMode1==2 && gen_partonMode2==1)))"
#elif channel == 2: ttother_tcut = "!(gen_partonChannel==2 && (gen_partonMode1==2 && gen_partonMode2==2))"
#elif channel == 3: ttother_tcut = "!(gen_partonChannel==2 && (gen_partonMode1==1 && gen_partonMode2==1))"
stepch_tcut =  'step>=%i'%(step)
if channel != 0: stepch_tcut = '%s&&channel==%i'%(stepch_tcut,channel)
tcut = '(%s&&%s)*(%s)'%(stepch_tcut,cut,weight)
#ttother_tcut = '(%s&&%s&&%s)*(%s)'%(stepch_tcut,cut,ttother_tcut,weight)
rd_tcut = '%s&&%s'%(stepch_tcut,cut)
print "TCut =",tcut

################################################################
## namming
################################################################
x_name = "Dilepton channel "+x_name
if len(binning) <= 3:
    num = (binning[2]-binning[1])/float(binning[0])
    if num != 1:
        if x_name.endswith(']'):
            unit = "["+x_name.split('[')[1]
        else: unit = ""
        y_name = y_name + "/%g%s"%(num,unit)

################################################################
## DYestimation
################################################################
if not os.path.exists('./DYFactor.json'):
	DYestimation.printDYFactor(rootfileDir, tname, datasets, datalumi, cut, weight, rdfilelist)# <------ This will create 'DYFactor.json' on same dir.
dyratio=json.load(open('./DYFactor.json'))

################################################################
## Initializing the result root file
################################################################
outMassHist = ROOT.TFile.Open("invMass_%s%s.root"%(plotvar,suffix),"RECREATE")

################################################################
## saving mc histos for only backgrounds
################################################################
mchistList = []
for i, mcname in enumerate(mcfilelist):
  data = findDataSet(mcname, datasets)
  scale = datalumi*data["xsec"]
  colour = data["colour"]
  title = data["title"]
  if 'DYJets' in mcname:
    scale = scale*dyratio[channel][step]

  rfname = rootfileDir + mcname +".root"
  tfile = ROOT.TFile(rfname)
  wentries = tfile.Get("cattree/nevents").Integral()
  scale = scale/wentries
  print "Bkg scales : ", mcname, scale
    
  mchist = makeTH1(rfname, tname, title, binning, plotvar, tcut, scale)
  mchist.SetLineColor(colour)
  mchist.SetFillColor(colour)
  mchistList.append(mchist)
  
  mchist.SetName("bkg_" + mcname)
  outMassHist.cd()
  mchist.Write()
  
#overflow
if overflow:
  if len(binning) == 3 : nbin = binning[0]
  else : nbin = len(binnin)-1
  for hist in mchistList:
    hist.SetBinContent(nbin, hist.GetBinContent(nbin+1))

#bin normalize
if binNormalize and len(binning)!=3:
  for hist in mchistList:
    for i in range(len(binning)):
      hist.SetBinContent(i, hist.GetBinContent(i)/hist.GetBinWidth(i))
      hist.SetBinError(i, hist.GetBinError(i)/hist.GetBinWidth(i))

hs_bkg = ROOT.THStack("bkg_hs","bkg_hs")
for hist in mchistList :
  hs_bkg.Add( hist)
hs_bkg.Draw()

bkgs = hs_bkg.GetStack().Last()
bkgs.SetName("bkg")
bkgs.Draw()
outMassHist.cd()
bkgs.Write()
print "bkg entries: ",bkgs.GetEntries()

dicPeakVsMass = {}
dSizeBin = 1.0 * ( binning[2] - binning[1] ) / binning[0]
nNumFitRangeL = 1000
nNumFitRangeR = 2

################################################################
##  Getting peaks of TT samples
################################################################
for topMass in topMassList :
  if ( topMass.find("mtop") != -1 ) :  massValue = topMass.split("mtop")[-1]
  else : massValue = "nominal" 
  sum_hs =  hs_bkg.Clone()
  data = findDataSet(topMass, datasets)
  scale = datalumi*data["xsec"]
  colour = data["colour"]
  title = data["title"]

  dMassCurr = 0.0
  if massValue != "nominal" : dMassCurr = int(massValue) * 0.1
  else : dMassCurr = dMassNomial

  rfname = rootfileDir + topMass +".root"
  tfile = ROOT.TFile(rfname)
  wentries = tfile.Get("cattree/nevents").Integral()
  scale = scale/wentries
  print topMass, scale, wentries, colour, title
   
  mchist = makeTH1(rfname, tname, title, binning, plotvar, tcut, scale)
  mchist.SetLineColor(colour)
  mchist.SetFillColor(colour)
  print "topmass hsit : ",mchist.Integral()
  # -- Overflow
  if overflow:
    if len(binning) == 3 : nbin = binning[0]
    else : nbin = len(binnin)-1
    mchist.SetBinContent(nbin, mchist.GetBinContent(nbin+1))

  # -- Bin normalize
  if binNormalize and len(binning)!=3:
    for i in range(len(binning)):
      mchist.SetBinContent(i, mchist.GetBinContent(i)/mchist.GetBinWidth(i))
      mchist.SetBinError(i, mchist.GetBinError(i)/mchist.GetBinWidth(i))

  # -- Getting the plot 
  sum_hs.Add( mchist )
  masshist = sum_hs.GetStack().Last()
 
  # -- Saving results into the root file
  masshist.Draw()
  print masshist.GetEntries()

  """
  # -- Fitting by TH1.Fit() (no bkg)
  dXPeak = binning[1] + myGetPosMaxHist(mchist, binning[0]) * dSizeBin
  print "X_Max (no bkg) = %lf"%(dXPeak)
  dMinFitRange = dXPeak - nNumFitRangeL * dSizeBin
  if dMinFitRange < 0 : dMinFitRange = 0
  
  print ""
  print "#####################################################"
  print "### Fitting (%s, no bkg) by TH1.Fit() is beginning"%(massValue)
  print "#####################################################"
  
  #tf1 = ROOT.TF1("f1_TT_nobkg","gaus",dMinFitRange, dXPeak + nNumFitRangeR * dSizeBin)
  tf1 = ROOT.TF1("f1_TT_nobkg","landau", binning[1], binning[2])
  #mchist.Fit(tf1, "", "", dMinFitRange, dXPeak + nNumFitRangeR * dSizeBin)
  mchist.Fit(tf1, "", "11111111111")
  
  dicPeakVsMass[ massValue + "_TH1_nobkg" ] = {"m":dMassCurr, 
    "value":tf1.GetParameter(1), "error":tf1.GetParError(1)}
  print "------ Peak (no bkg) by TH1.Fit() : %f, Err : %f"%(tf1.GetParameter(1), tf1.GetParError(1))

  # -- Fitting by TH1.Fit() (with bkg)
  dXPeak = binning[1] + myGetPosMaxHist(masshist, binning[0]) * dSizeBin
  print "X_Max = %lf"%(dXPeak)
  dMinFitRange = dXPeak - nNumFitRangeL * dSizeBin
  if dMinFitRange < 0 : dMinFitRange = 0
  
  print ""
  print "#####################################################"
  print "### Fitting (%s) by TH1.Fit() is beginning"%(massValue)
  print "#####################################################"
  
  #tf1 = ROOT.TF1("f1_TT","gaus",dMinFitRange, dXPeak + nNumFitRangeR * dSizeBin)
  tf1 = ROOT.TF1("f1_TT","landau", binning[1], binning[2])
  #masshist.Fit(tf1, "", "", dMinFitRange, dXPeak + nNumFitRangeR * dSizeBin)
  masshist.Fit(tf1, "", "11111111111")
  
  dicPeakVsMass[ massValue + "_TH1" ] = {"m":dMassCurr, "value":tf1.GetParameter(1), "error":tf1.GetParError(1)}
  print "------ Peak by TH1.Fit() : %f, Err : %f"%(tf1.GetParameter(1), tf1.GetParError(1))
  
  outMassHist.cd()
  masshist.SetName("invMass_%s"%(massValue))
  masshist.SetTitle("Invariant mass; M_{l+D*};Entries/%f"%( masshist.GetBinWidth(1) ))
  masshist.Write()
  
  outMassHist.cd()
  mchist.SetName("ttbar_mtop%s"%(massValue))
  mchist.Write()
  """
  
  # -- Fitting by RooFit (no bkg)
  print ""
  print "#####################################################"
  print "### Fitting (%s, no bkg) by RooFit is beginning"%(massValue)
  print "#####################################################"
  
  roofitres_nobkg = myFitInvMass(mchist, binning)
  dicPeakVsMass[ massValue + "_RooFit_nobkg" ] = {"m":dMassCurr, 
    "value":roofitres_nobkg[ "peak_val" ], "error":roofitres_nobkg[ "peak_err" ]}

  print "------ Peak (no bkg) by RooFit : %f, Err : %f"%(roofitres_nobkg["peak_val"], roofitres_nobkg["peak_err"])
  print "------      (sigma : %f, %f)"%(roofitres_nobkg[ "sigma_val" ], roofitres_nobkg[ "sigma_err" ])
  
  # -- Fitting by RooFit (with bkg)
  print ""
  print "#####################################################"
  print "### Fitting (%s) by RooFit is beginning"%(massValue)
  print "#####################################################"
  
  roofitres_mass = myFitInvMass(masshist, binning)
  dicPeakVsMass[ massValue + "_RooFit" ] = {"m":dMassCurr, 
    "value":roofitres_mass[ "peak_val" ], "error":roofitres_mass[ "peak_err" ]}

  print "------ Peak by RooFit : %f, Err : %f"%(roofitres_mass["peak_val"], roofitres_mass["peak_err"])
  print "------      (sigma : %f, %f)"%(roofitres_mass[ "sigma_val" ], roofitres_mass[ "sigma_err" ])
  
  outMassHist.cd()
  roofitres_nobkg[ "frame" ].SetName("ttbar_mtop%s"%(massValue))
  roofitres_nobkg[ "frame" ].SetTitle("M_{l+D} in only TT;Entries/%f"%( masshist.GetBinWidth(1) ))
  roofitres_nobkg[ "frame" ].Write()
  
  outMassHist.cd()
  roofitres_mass[ "frame" ].SetName("invMass_%s_byRooFit"%(massValue))
  roofitres_mass[ "frame" ].SetTitle("Invariant mass; M_{l+D};Entries/%f"%( masshist.GetBinWidth(1) ))
  roofitres_mass[ "frame" ].Write()

################################################################
##  Getting peaks of data samples
################################################################
#output = ROOT.TFile.Open("data_%s.root"%(plotvar),"RECREATE")
if len(binning) == 3:
  rdhist = ROOT.TH1D("Run2016_dummy", "RealData in 2016", binning[0], binning[1], binning[2])
else:
  rdhist = ROOT.TH1D("Run2016_dummy", "RealData in 2016", len(binning)-1, array.array('f', binning))
for i, rdfile in enumerate(rdfilelist):
  rfname = rootfileDir + rdfile +".root"
  rdtcut = 'channel==%d&&%s&&%s'%((i+1),stepch_tcut,cut)
  rdhist_tmp = makeTH1(rfname, tname, 'data', binning, plotvar, rdtcut)
  rdhist.SetLineColor(1)
  rdhist.Add(rdhist_tmp)
#overflow
if overflow:
  if len(binning) == 3 : nbin = binning[0]
  else : nbin = len(binnin)-1
  rdhist.SetBinContent(nbin, rdhist.GetBinContent(nbin+1))
if binNormalize and len(binning)!=3:
  for i in range(len(binning)):
    rdhist.SetBinContent(i, rdhist.GetBinContent(i)/rdhist.GetBinWidth(i))
    rdhist.SetBinError(i, rdhist.GetBinError(i)/rdhist.GetBinWidth(i))

# Fitting
"""
dXPeak = binning[1] + myGetPosMaxHist(rdhist, binning[0]) * dSizeBin
print "X_Max (data) = %lf"%(dXPeak)
dMinFitRange = dXPeak - nNumFitRangeL * dSizeBin
if dMinFitRange < 0 : dMinFitRange = 0

tf1 = ROOT.TF1("f1_data","gaus",dMinFitRange, dXPeak + nNumFitRangeR * dSizeBin)
#tf1 = ROOT.TF1("f1_data","crystalball",50,80)
rdhist.Fit(tf1, "", "", dMinFitRange, dXPeak + nNumFitRangeR * dSizeBin)

dicPeakVsMass[ "data" ] = {"value":tf1.GetParameter(1), "error":tf1.GetParError(1)}
print dicPeakVsMass

outMassHist.cd()
rdhist.Draw()
"""
# Fitting by RooFit
print ""
print "#####################################################"
print "### Fitting data by RooFit is beginning"
print "#####################################################"

roofitres_data = myFitInvMass(rdhist, binning)
dicPeakVsMass[ "data" ] = {"value":roofitres_data[ "peak_val" ], "error":roofitres_data[ "peak_err" ]}

print "------ Peak by RooFit : %f, Err : %f"%(roofitres_data[ "peak_val" ], roofitres_data[ "peak_err" ])
print "------      (sigma : %f, %f)"%(roofitres_data[ "sigma_val" ], roofitres_data[ "sigma_err" ])

outMassHist.cd()
roofitres_data[ "frame" ].SetName("Run2016")
roofitres_data[ "frame" ].SetTitle("RealData in 2016")
roofitres_data[ "frame" ].Write()

################################################################
##  Prepare to draw the linear plot
################################################################
dBinMinPeak = 164.0
dBinMaxPeak = 180.0
dSizeBin = 0.1

dDatMinPeak =  1048576.0
dDatMaxPeak = -1048576.0

for strMass in dicPeakVsMass.keys() :
    #if strMass == "data" : continue
    
    dDatVal = dicPeakVsMass[ strMass ][ "value" ]
    dDatErr = dicPeakVsMass[ strMass ][ "error" ]
    
    if dDatMinPeak > dDatVal - dDatErr : dDatMinPeak = dDatVal - dDatErr
    if dDatMaxPeak < dDatVal + dDatErr : dDatMaxPeak = dDatVal + dDatErr

dDatMean = ( dDatMaxPeak + dDatMinPeak ) / 2
dDatMinPeak = dDatMinPeak - ( dDatMean - dDatMinPeak ) * 1.0
dDatMaxPeak = dDatMaxPeak + ( dDatMaxPeak - dDatMean ) * 1.0
print "Range in linear plot : ", dDatMinPeak, dDatMean, dDatMaxPeak

"""
################################################################
##  Plotting the linear plot by TH1.Fit() (without bkg)
################################################################
print "##### Fitting by TH1.Fit() (no bkg)"

histPeak_nb = ROOT.TH1D("histPeak_TH1_nobkg", "Peaks (no bkg)", int(( dBinMaxPeak - dBinMinPeak ) / dSizeBin), dBinMinPeak, dBinMaxPeak)
histPeak_nb.SetLineColor(1)

for strMass in dicPeakVsMass.keys() :
    if strMass == "data" : continue
    if "_TH1" not in strMass : continue
    if "_nobkg" not in strMass : continue
    
    dMass = dicPeakVsMass[ strMass ][ "m" ]
    dDatVal = dicPeakVsMass[ strMass ][ "value" ]
    dDatErr = dicPeakVsMass[ strMass ][ "error" ]
    
    print dMass, "(" + strMass + ")", dDatVal, dDatErr
    
    nIdxBin = int(( dMass - dBinMinPeak ) / dSizeBin)
    histPeak_nb.SetBinContent(nIdxBin, dDatVal)
    histPeak_nb.SetBinError(nIdxBin, dDatErr)

histPeak_nb.SetMinimum(dDatMinPeak)
histPeak_nb.SetMaximum(dDatMaxPeak)

tf1 = ROOT.TF1("f1_peaks_TH1_nobkg", "pol1", dBinMinPeak, dBinMaxPeak)
histPeak_nb.Fit(tf1)

outMassHist.cd()
histPeak_nb.Write()

################################################################
##  Plotting the linear plot by TH1.Fit()
################################################################
print "##### Fitting by TH1.Fit() (bkg)"

histPeak = ROOT.TH1D("histPeak_TH1", "Peaks", int(( dBinMaxPeak - dBinMinPeak ) / dSizeBin), dBinMinPeak, dBinMaxPeak)
histPeak.SetLineColor(1)

for strMass in dicPeakVsMass.keys() :
    if strMass == "data" : continue
    if "_TH1" not in strMass : continue
    if "_nobkg" in strMass : continue
    
    dMass = dicPeakVsMass[ strMass ][ "m" ]
    dDatVal = dicPeakVsMass[ strMass ][ "value" ]
    dDatErr = dicPeakVsMass[ strMass ][ "error" ]
    
    print dMass, "(" + strMass + ")", dDatVal, dDatErr
    
    nIdxBin = int(( dMass - dBinMinPeak ) / dSizeBin)
    histPeak.SetBinContent(nIdxBin, dDatVal)
    histPeak.SetBinError(nIdxBin, dDatErr)

histPeak.SetMinimum(dDatMinPeak)
histPeak.SetMaximum(dDatMaxPeak)

tf1 = ROOT.TF1("f1_peaks_TH1", "pol1", dBinMinPeak, dBinMaxPeak)
histPeak.Fit(tf1)

outMassHist.cd()
histPeak.Write()
"""

################################################################
##  Plotting the linear plot by RooFit (without bkg)
################################################################
print "##### Fitting by RooFit (no bkg)"

histPeak_nb = ROOT.TH1D("histPeak_RooFit_nobkg", "Peaks (no bkg)", int(( dBinMaxPeak - dBinMinPeak ) / dSizeBin), dBinMinPeak, dBinMaxPeak)
histPeak_nb.SetLineColor(1)

for strMass in dicPeakVsMass.keys() :
    if strMass == "data" : continue
    if "_RooFit" not in strMass : continue
    if "_nobkg" not in strMass : continue
    
    dMass = dicPeakVsMass[ strMass ][ "m" ]
    dDatVal = dicPeakVsMass[ strMass ][ "value" ]
    dDatErr = dicPeakVsMass[ strMass ][ "error" ]
    
    print dMass, "(" + strMass + ")", dDatVal, dDatErr
    
    nIdxBin = int(( dMass - dBinMinPeak ) / dSizeBin)
    histPeak_nb.SetBinContent(nIdxBin, dDatVal)
    histPeak_nb.SetBinError(nIdxBin, dDatErr)

histPeak_nb.SetMinimum(dDatMinPeak)
histPeak_nb.SetMaximum(dDatMaxPeak)

tf1 = ROOT.TF1("f1_peaks_RooFit_nobkg", "pol1", dBinMinPeak, dBinMaxPeak)
histPeak_nb.Fit(tf1)

outMassHist.cd()
histPeak_nb.Write()

################################################################
##  Plotting the linear plot by RooFit
################################################################
print "##### Fitting by RooFit (bkg)"

histPeak = ROOT.TH1D("histPeak_RooFit", "Peaks", int(( dBinMaxPeak - dBinMinPeak ) / dSizeBin), dBinMinPeak, dBinMaxPeak)
histPeak.SetLineColor(1)

for strMass in dicPeakVsMass.keys() :
    if strMass == "data" : continue
    if "_RooFit" not in strMass : continue
    if "_nobkg" in strMass : continue
    
    dMass = dicPeakVsMass[ strMass ][ "m" ]
    dDatVal = dicPeakVsMass[ strMass ][ "value" ]
    dDatErr = dicPeakVsMass[ strMass ][ "error" ]
    
    print dMass, "(" + strMass + ")", dDatVal, dDatErr
    
    nIdxBin = int(( dMass - dBinMinPeak ) / dSizeBin)
    histPeak.SetBinContent(nIdxBin, dDatVal)
    histPeak.SetBinError(nIdxBin, dDatErr)

histPeak.SetMinimum(dDatMinPeak)
histPeak.SetMaximum(dDatMaxPeak)

tf1 = ROOT.TF1("f1_peaks_RooFit", "pol1", dBinMinPeak, dBinMaxPeak)
histPeak.Fit(tf1)

outMassHist.cd()
histPeak.Write()

################################################################
##  Everything is over; closing the file
################################################################

outMassHist.Write()
outMassHist.Close()

print ''
print ''
