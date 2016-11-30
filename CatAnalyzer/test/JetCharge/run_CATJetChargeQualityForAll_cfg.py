import FWCore.ParameterSet.Config as cms
process = cms.Process("TtbarDiLeptonAnalyzer")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("CATTools.CatAnalyzer.ttll.ttbarDileptonKinSolutionProducer_cfi")
process.load("CATTools.CatAnalyzer.ttll.ttbarDileptonKinSolutionAlgos_cff")
process.load("CATTools.Validation.ttllEventSelector_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(False) )

process.options.allowUnscheduled = cms.untracked.bool(True)
#process.options.allowUnscheduled = cms.untracked.bool(False)


## setting up arguements
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing ('python')
options.register('isTT',False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "isTT: 0  default")
options.parseArguments()

process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring())
#process.source.fileNames = ['/store/user/jhgoh/CATTools/sync/v7-6-3/MuonEG_Run2015D-16Dec2015-v1.root',]
#process.source.fileNames = ['file:/xrootd/store/user/jhgoh/CATTools/sync/v7-6-3/TT_TuneCUETP8M1_13TeV-powheg-pythia8.root',]
#process.source.fileNames = ['file:../../../catdata_20160315/catTuple.root']
process.source.fileNames = ['root://cms-xrdr.sdfarm.kr:1094///xrd/store/group/CAT/TTTo2L2Nu_13TeV-powheg/v8-0-0_RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0_ext1-v1/160705_215520/0000/catTuple_1.root']

#process.MessageLogger.debugModules = cms.untracked.vstring('cattree')
#process.MessageLogger.destinations = cms.untracked.vstring('detailInfo')
#process.MessageLogger.detailInfo = cms.untracked.PSet( threshold = cms.untracked.string('DEBUG'))

from CATTools.CatAnalyzer.leptonSF_cff import *

process.load("CATTools.CatAnalyzer.filters_cff")
process.load("CATTools.CatAnalyzer.ttll.ttllGenFilters_cff")

process.load("CATTools.CatAnalyzer.flatGenWeights_cfi")
process.agen = cms.EDAnalyzer("CATGenTopAnalysis",
    weightIndex = cms.int32(-1),
    weight = cms.InputTag("flatGenWeights"),
    channel = cms.InputTag("partonTop","channel"),
    modes = cms.InputTag("partonTop", "modes"),
    partonTop = cms.InputTag("partonTop"),
    pseudoTop = cms.InputTag("pseudoTop"),
    filterTaus = cms.bool(False),
)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string("cmskin_quality_forAll.root")
)
process.qualityAna = cms.EDAnalyzer("TTLLKinQualityAnalyzerForAll",
    #solver = cms.PSet(algo = cms.string("CMSKin"),), 
    leptons = cms.InputTag("eventsTTLL", "leptons"), ## lepton in LorentzVector
    jets = cms.InputTag("eventsTTLL", "jets"), ## jet in LorentzVector
    met = cms.InputTag("eventsTTLL", "met"), ## MET pt in float 
    metphi = cms.InputTag("eventsTTLL", "metphi"), ## MET phi in float
    applyJetCharge = cms.double(1.0),
)

process.qualityAna.solver = process.ttbarDileptonKinAlgoPSetCMSKin

process.eventsTTLL.filters.ignoreTrig = cms.bool(True)

"""
if ( options.isTT ) : 
  print "This is TT Samples. Run agen and filter parto."
  process.p = cms.Path(
      process.agen + process.filterPartonTTLL* process.eventsTTLL * process.qualityAna
  )
else : 
"""
process.p = cms.Path( process.eventsTTLL * process.qualityAna)

if ( process.maxEvents.input <0 or process.maxEvents > 5000) :
  process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.options.wantSummary = True



