#!/usr/bin/env python
import ROOT, CATTools.CatAnalyzer.CMS_lumi, json, os, getopt, sys, copy
from CATTools.CatAnalyzer.histoHelper import *
import DYestimation
ROOT.gROOT.SetBatch(True)


datalumi = 15.92 # Run2016 B & C & D & E, v8-0-1
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
        cut = arg
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
    
  mchist = makeTH1(rfname, tname, title, binning, plotvar, tcut, scale)
  mchist.SetLineColor(colour)
  mchist.SetFillColor(colour)
  mchistList.append(mchist)
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

outMassHist = ROOT.TFile.Open("invMass_%s%s.root"%(plotvar,suffix),"RECREATE")

bkgs = hs_bkg.GetStack().Last()
bkgs.SetName("bkg")
bkgs.Draw()
outMassHist.cd()
bkgs.Write()
print "bkg entries: ",bkgs.GetEntries()

dicPeakVsMass = {}
dSizeBin = 1.0 * ( binning[2] - binning[1] ) / binning[0]

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

  rfname = rootfileDir + topMass +".root"
  tfile = ROOT.TFile(rfname)
  wentries = tfile.Get("cattree/nevents").Integral()
  scale = scale/wentries
  print topMass, scale, wentries, colour, title
   
  mchist = makeTH1(rfname, tname, title, binning, plotvar, tcut, scale)
  mchist.SetLineColor(colour)
  mchist.SetFillColor(colour)
  print "topmass hsit : ",mchist.Integral()
  #overflow
  if overflow:
    if len(binning) == 3 : nbin = binning[0]
    else : nbin = len(binnin)-1
    mchist.SetBinContent(nbin, mchist.GetBinContent(nbin+1))

  #bin normalize
  if binNormalize and len(binning)!=3:
    for i in range(len(binning)):
      mchist.SetBinContent(i, mchist.GetBinContent(i)/mchist.GetBinWidth(i))
      mchist.SetBinError(i, mchist.GetBinError(i)/mchist.GetBinWidth(i))

  dMaxBinCont = -1048576.0
  nIdxBinMax = 0

  for i in range(binning[0]):
      dPointData = mchist.GetBinContent(i)
      if dMaxBinCont < dPointData: 
          dMaxBinCont = dPointData
          nIdxBinMax = i

  dXPeak = binning[1] + nIdxBinMax * dSizeBin
  print "X_Max = %lf (%i, %lf)"%(dXPeak, nIdxBinMax, dMaxBinCont)

  dMinFitR = dXPeak - 3 * dSizeBin
  if dMinFitR < 0 : dMinFitR = 0
  tf1 = ROOT.TF1("f1_data","gaus",dMinFitR, dXPeak + 3 * dSizeBin)
  #tf1 = ROOT.TF1("f1_data","crystalball",50,80)
  mchist.Fit(tf1, "", "", dMinFitR, dXPeak + 3 * dSizeBin)
  
  dicPeakVsMass[ massValue ] = {"value":tf1.GetParameter(1), "error":tf1.GetParError(1)}
  print "------ Peak : %f, Err : %f"%(tf1.GetParameter(1), tf1.GetParError(1))

  sum_hs.Add( mchist )
  masshist = sum_hs.GetStack().Last()
  masshist.Draw()
  print masshist.GetEntries()
  masshist.SetName("invMass_%s"%(massValue))
  masshist.SetTitle("Invariant mass; M_{l+D*};Entries/%f"%( masshist.GetBinWidth(1) ))
  outMassHist.cd()
  masshist.Write()
  mchist.SetName("ttbar_mtop%s"%(massValue))
  mchist.Write()
  #outMassHist.Write()

################################################################
##  Getting peaks of data samples
################################################################
#output = ROOT.TFile.Open("data_%s.root"%(plotvar),"RECREATE")
if len(binning) == 3:
  rdhist = ROOT.TH1D("Run2016", "RealData in 2016", binning[0], binning[1], binning[2])
else:
  rdhist = ROOT.TH1D("Run2016", "RealData in 2016", len(binning)-1, array.array('f', binning))
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

dMaxBinCont = -1048576.0
nIdxBinMax = 0

for i in range(binning[0]):
    dPointData = rdhist.GetBinContent(i)
    if dMaxBinCont < dPointData: 
        dMaxBinCont = dPointData
        nIdxBinMax = i

dXPeak = binning[1] + nIdxBinMax * ( 1.0 * ( binning[2] - binning[1] ) / binning[0] )
print "X_Max = %lf (%i, %lf)"%(dXPeak, nIdxBinMax, dMaxBinCont)
print "(%lf, %lf, %lf)"%(rdhist.GetBinContent(nIdxBinMax - 1), rdhist.GetBinContent(nIdxBinMax), rdhist.GetBinContent(nIdxBinMax + 1))

dMinFitR = dXPeak - 3 * dSizeBin
if dMinFitR < 0 : dMinFitR = 0
tf1 = ROOT.TF1("f1_data","gaus",dMinFitR, dXPeak + 3 * dSizeBin)
#tf1 = ROOT.TF1("f1_data","crystalball",50,80)
rdhist.Fit(tf1, "", "", dMinFitR, dXPeak + 3 * dSizeBin)

dicPeakVsMass[ "data" ] = {"value":tf1.GetParameter(1), "error":tf1.GetParError(1)}
print dicPeakVsMass

################################################################
##  Plotting the linear plot
################################################################
dBinMinPeak = 164.0
dBinMaxPeak = 180.0
dSizeBin = 0.5

histPeak = ROOT.TH1D("histPaek", "Peaks", int(( dBinMaxPeak - dBinMinPeak ) / dSizeBin), dBinMinPeak, dBinMaxPeak)
histPeak.SetLineColor(1)

dDatMinPeak =  1048576.0
dDatMaxPeak = -1048576.0

for strMass in dicPeakVsMass.keys() :
    dMass = 0.0
    
    if strMass == "data" : 
        print "data!"
        continue
    elif strMass == "nominal" : dMass = dMassNomial
    else: dMass = int(strMass) * 0.1
    
    dDatVal = dicPeakVsMass[ strMass ][ "value" ]
    dDatErr = dicPeakVsMass[ strMass ][ "error" ]
    
    print dMass, dDatVal, dDatErr
    
    nIdxBin = int(( dMass - dBinMinPeak ) / dSizeBin)
    histPeak.SetBinContent(nIdxBin, dDatVal)
    histPeak.SetBinError(nIdxBin, dDatErr)
    
    if dDatMinPeak > dDatVal: dDatMinPeak = dDatVal
    if dDatMaxPeak < dDatVal: dDatMaxPeak = dDatVal

dDatMean = ( dDatMaxPeak + dDatMinPeak ) / 2
print dDatMinPeak, dDatMean, dDatMaxPeak
histPeak.SetMinimum(dDatMinPeak - ( dDatMean - dDatMinPeak ) * 4.0)
histPeak.SetMaximum(dDatMaxPeak + ( dDatMaxPeak - dDatMean ) * 4.0)

tf1 = ROOT.TF1("f1_peaks", "pol1", dBinMinPeak, dBinMaxPeak)
histPeak.Fit(tf1)

outMassHist.cd()
histPeak.Write()

rdhist.Draw()
outMassHist.Write()
outMassHist.Close()

print ''
print ''
