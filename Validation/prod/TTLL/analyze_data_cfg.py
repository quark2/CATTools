import FWCore.ParameterSet.Config as cms
process = cms.Process("CATeX")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(False) )

process.options.allowUnscheduled = cms.untracked.bool(True)
process.MessageLogger.cerr.FwkReport.reportEvery = 50000

process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring())
process.source.fileNames = [
    '/store/group/CAT/MuonEG/v8-0-0_Run2016B-PromptReco-v2/160807_174617/0000/catTuple_1.root',
]

process.load("CATTools.CatAnalyzer.filters_cff")
process.load("CATTools.Validation.ttllEventSelector_cff")
process.load("CATTools.Validation.validation_cff")
process.eventsTTLL.isMC = False
process.rec.isMC = False
if hasattr(process.eventsTTLL, "genWeight"): delattr(process.eventsTTLL, "genWeight")
if hasattr(process, "flatGenWeights"): delattr(process, "flatGenWeights")

process.TFileService = cms.Service("TFileService",
    fileName = cms.string("hist.root"),
)

process.p = cms.Path(
    process.filterLumi * process.removeLumisWithL1TCert
  * process.rec
  * process.eventsTTLL
)

## Customise with cmd arguments
import sys
if len(sys.argv) > 2:
    for l in sys.argv[2:]: exec('process.'+l)
