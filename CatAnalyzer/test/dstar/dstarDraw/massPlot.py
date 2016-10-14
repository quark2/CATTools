#!/usr/bin/env python
import ROOT, CATTools.CatAnalyzer.CMS_lumi, json, os, getopt, sys, copy
from CATTools.CatAnalyzer.histoHelper import *
import DYestimation
ROOT.gROOT.SetBatch(True)


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
strFilename = "invMass_%s%s"%(plotvar,suffix)
outMassHist = ROOT.TFile.Open(strFilename + ".root","RECREATE")
dicListHist = {"rootfilename":strFilename + ".root", "x_name":x_name, "y_name":y_name, "binning":binning}

################################################################
## Saving MC histograms for backgrounds
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
  
  mchist.SetName("hist_bkg_" + mcname)
  outMassHist.cd()
  mchist.Write()

  dicListHist[mchist.GetName()] = {"type":"bkg_part"}
  
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

bkgs.SetName("hist_bkg")
bkgs.Draw()

outMassHist.cd()
bkgs.Write()

dicListHist[bkgs.GetName()] = {"type":"bkg"}

print "bkg entries: ",bkgs.GetEntries()

################################################################
##  Saving TT samples
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
  
  outMassHist.cd()
  mchist.SetName("hist_TT_onlytt_%s"%(massValue))
  mchist.Write()
  
  dicListHist[mchist.GetName()] = {"type":"TT_onlytt", "mass":dMassCurr}
  
  outMassHist.cd()
  masshist.SetName("hist_TT_withbkg_%s"%(massValue))
  masshist.Write()
  
  dicListHist[masshist.GetName()] = {"type":"TT_withbkg", "mass":dMassCurr}

################################################################
##  Saving data samples
################################################################
#output = ROOT.TFile.Open("data_%s.root"%(plotvar),"RECREATE")
if len(binning) == 3:
  rdhist = ROOT.TH1D("hist_data", "RealData in 2016", binning[0], binning[1], binning[2])
else:
  rdhist = ROOT.TH1D("hist_data", "RealData in 2016", len(binning)-1, array.array('f', binning))
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

outMassHist.cd()
rdhist.Write()

dicListHist[rdhist.GetName()] = {"type":"data"}

outMassHist.Write()
outMassHist.Close()

################################################################
##  Saving informations about histograms
################################################################

fileDicHist = open(strFilename + ".json", "w")
fileDicHist.write(json.dumps(dicListHist))
fileDicHist.close()

print ''
print ''
