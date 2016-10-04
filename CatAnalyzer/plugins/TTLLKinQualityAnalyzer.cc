#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "CATTools/DataFormats/interface/Muon.h"
#include "CATTools/DataFormats/interface/Electron.h"
#include "CATTools/DataFormats/interface/Jet.h"
#include "CATTools/DataFormats/interface/MET.h"
#include "CATTools/DataFormats/interface/SecVertex.h"

#include "CATTools/CatAnalyzer/interface/KinematicSolvers.h"
#include "DataFormats/Candidate/interface/LeafCandidate.h"
#include "DataFormats/Candidate/interface/CompositePtrCandidate.h"
#include "FWCore/ServiceRegistry/interface/Service.h"

#include<TTree.h>


using namespace std;

namespace cat {

class TTLLKinQualityAnalyzer : public edm::one::EDAnalyzer<edm::one::SharedResources,edm::one::WatchLuminosityBlocks> 
{
public:
  TTLLKinQualityAnalyzer(const edm::ParameterSet& pset);
  virtual ~TTLLKinQualityAnalyzer() {};
  void analyze(const edm::Event & event, const edm::EventSetup&) override;
  void bookingBranch() { 
    ttree_->Branch("bjet1_all","TLorentzVector",&(this->j1_));
    ttree_->Branch("bjet2_all","TLorentzVector",&(this->j2_));
    ttree_->Branch("bjet1_qcut","TLorentzVector",&(this->j3_));
    ttree_->Branch("bjet2_qcut","TLorentzVector",&(this->j4_));
    ttree_->Branch("lep_charge", &(lepton_charge_[0]),"lep_charge[2]/I");
    ttree_->Branch("bjet_charge_all", &(bjet_charge_all_[0]),"bjet_charge_all[2]/I");
    ttree_->Branch("bjet_charge_qcut", &(bjet_charge_qcut_[0]),"bjet_charge_qcut[2]/I");
    ttree_->Branch("bjet_ntracks_all", &(bjet_ntracks_all_[0]),"bjet_ntracks_all[2]/I");
    ttree_->Branch("bjet_ntracks_qcut", &(bjet_ntracks_qcut_[0]),"bjet_ntracks_qcut[2]/I");
    ttree_->Branch("bjet_partonPdgId_all", &(bjet_partonPdgId_all_[0]),"bjet_partonPdgId_all[2]/I");
    ttree_->Branch("bjet_partonPdgId_qcut", &(bjet_partonPdgId_qcut_[0]),"bjet_partonPdgId_qcut[2]/I");
    ttree_->Branch("pair_quality_all",&(quality_all_),"quality_all/D");
    ttree_->Branch("pair_quality_qcut",&(quality_qcut_),"quality_qcut/D");

  }
  void resetBranch() {
    j1_ = TLorentzVector();
    j2_ = TLorentzVector();
    j3_ = TLorentzVector();
    j4_ = TLorentzVector();
    for ( int i= 0 ; i<2; ++i) {
      lepton_charge_[i]=-999;
      bjet_charge_all_[i]=-999;
      bjet_charge_qcut_[i]=-999;
      bjet_ntracks_all_[i] = 0;
      bjet_ntracks_qcut_[i] = 0;
      bjet_partonPdgId_all_[i] = 0;
      bjet_partonPdgId_qcut_[i] = 0;
    }
    quality_all_  = -1e9;
    quality_qcut_ = -1e9;
  }
  bool findPairUsingJetCharge( int lep1_charge, cat::Jet j1, cat::Jet j2 ) {
    if ( abs(j1.charge() - j2.charge())>0 ) return true;
    else return false; 
  }

private:
  void beginLuminosityBlock(const edm::LuminosityBlock& lumi, const edm::EventSetup&) final;
  void endLuminosityBlock(const edm::LuminosityBlock&, const edm::EventSetup&) override {};
  edm::EDGetTokenT<edm::View<reco::CandidatePtr> > leptonPtrToken_;
  edm::EDGetTokenT<edm::View<reco::Candidate> > leptonToken_;
  edm::EDGetTokenT<cat::JetCollection > jetToken_;
  edm::EDGetTokenT<float> metToken_, metphiToken_;
  double applyJetCharge_;
  
  typedef reco::Candidate::LorentzVector LV;
  typedef reco::LeafCandidate Cand;
  typedef std::vector<Cand> CandColl;
  typedef std::vector<float> floats;


  typedef std::pair<Cand,Cand> CandPair;
  typedef std::pair<double ,CandPair> QCP;
  typedef std::vector< QCP > QCPs;

  TTree* ttree_;
  TLorentzVector j1_,j2_,j3_,j4_;
  int lepton_charge_[2];
  int bjet_charge_all_[2];
  int bjet_charge_qcut_[2];
  int bjet_ntracks_all_[2];
  int bjet_ntracks_qcut_[2];
  int bjet_partonPdgId_all_[2];
  int bjet_partonPdgId_qcut_[2];
  double quality_all_;
  double quality_qcut_;


  std::unique_ptr<KinematicSolver> solver_;

};

}

using namespace cat;

void TTLLKinQualityAnalyzer::beginLuminosityBlock(const edm::LuminosityBlock& lumi, const edm::EventSetup&)
{
  if ( dynamic_cast<DESYSmearedSolver*>(solver_.get()) != 0 ) {
    edm::Service<edm::RandomNumberGenerator> rng;
    CLHEP::HepRandomEngine& engine = rng->getEngine(lumi.index());
    dynamic_cast<DESYSmearedSolver*>(solver_.get())->setRandom(&engine);
  }
}

TTLLKinQualityAnalyzer::TTLLKinQualityAnalyzer(const edm::ParameterSet& pset)
{
  leptonPtrToken_ = mayConsume<edm::View<reco::CandidatePtr> >(pset.getParameter<edm::InputTag>("leptons"));
  leptonToken_ = mayConsume<edm::View<reco::Candidate> >(pset.getParameter<edm::InputTag>("leptons"));
  jetToken_ = mayConsume<cat::JetCollection>(pset.getParameter<edm::InputTag>("jets"));
  metToken_ = consumes<float>(pset.getParameter<edm::InputTag>("met"));
  metphiToken_ = consumes<float>(pset.getParameter<edm::InputTag>("metphi"));
  applyJetCharge_ = pset.getParameter<double>("applyJetCharge");

  auto solverPSet = pset.getParameter<edm::ParameterSet>("solver");
  auto algoName = solverPSet.getParameter<std::string>("algo");
  std::transform(algoName.begin(), algoName.end(), algoName.begin(), ::toupper);
  if      ( algoName == "CMSKIN" ) solver_.reset(new CMSKinSolver(solverPSet));
  else if ( algoName == "DESYMASSLOOP" ) solver_.reset(new DESYMassLoopSolver(solverPSet));
  else if ( algoName == "DESYSMEARED" ) solver_.reset(new DESYSmearedSolver(solverPSet));
  else if ( algoName == "MT2"    ) solver_.reset(new MT2Solver(solverPSet));
  else if ( algoName == "MAOS"   ) solver_.reset(new MAOSSolver(solverPSet));
  else if ( algoName == "DEFAULT" ) solver_.reset(new TTDileptonSolver(solverPSet));
  else {
    cerr << "The solver name \"" << solverPSet.getParameter<std::string>("algo") << "\" is not known please check spellings.\n";
    cerr << "Fall back to the default dummy solver\n";
    solver_.reset(new TTDileptonSolver(solverPSet)); // A dummy solver
  }
  usesResource("TFileService");
  edm::Service<TFileService> fs;

  ttree_ = fs->make<TTree>("KinSolverQuality","KinSolverQuality");
  resetBranch();
  bookingBranch();

}


void TTLLKinQualityAnalyzer::analyze(const edm::Event& event, const edm::EventSetup&)
{

  std::vector<reco::CandidatePtr> leptons;
  edm::Handle<edm::View<reco::CandidatePtr> > leptonPtrHandle;
  edm::Handle<edm::View<reco::Candidate> > leptonHandle;
  if  ( event.getByToken(leptonPtrToken_, leptonPtrHandle) ) {
    for ( auto x : *leptonPtrHandle ) leptons.push_back(x);
  }
  else {
    event.getByToken(leptonToken_, leptonHandle);
    for ( int i=0, n=leptonHandle->size(); i<n; ++i ) leptons.push_back(reco::CandidatePtr(leptonHandle, i));
  }

  //std::vector<cat::Jet> jets;
  edm::Handle<cat::JetCollection> jets;
  event.getByToken(jetToken_, jets);

  edm::Handle<float> metHandle;
  event.getByToken(metToken_, metHandle);
  const float met = *metHandle;
  event.getByToken(metphiToken_, metHandle);
  const float metphi = *metHandle;
  const LV metLV(met*cos(metphi), met*sin(metphi), 0, met);

  do {
    // Check objects to exist
    if ( leptons.size() < 2 ) break;
    if ( (*jets).size() < 2 ) break;

    // Pick leading leptons.
    const auto lep1 = leptons.at(0);
    const auto lep2 = leptons.at(1);
    const LV lep1LV = lep1->p4();
    const LV lep2LV = lep2->p4();
    LV inputLV[5] = {metLV, lep1LV, lep2LV};
    LV nu1LV, nu2LV;

    // Run the solver with all jet combinations
    reco::CandidatePtr selectedJet1, selectedJet2;
    resetBranch();

    lepton_charge_[0] = lep1->charge();
    lepton_charge_[1] = lep2->charge();

    for ( auto jet1 : *jets )
    {
      inputLV[3] = jet1.p4();
      for ( auto jet2 : *jets )
      {
        if ( dynamic_cast<reco::LeafCandidate*>(&jet1) == dynamic_cast<reco::LeafCandidate*>(&jet2) ) continue;
        inputLV[4] = jet2.p4();

        solver_->solve(inputLV);
          
        auto quality = solver_->quality();
        //std::cout<<"Quality : "<<quality<<std::endl;
        if ( quality <= -1e9 ) break; // failed to get solution

        if ( quality > quality_all_) {
          j1_ = TLorentzVector( jet1.px(), jet1.py(), jet1.pz(), jet1.energy());
          j2_ = TLorentzVector( jet2.px(), jet2.py(), jet2.pz(), jet2.energy());
          bjet_charge_all_[0] = jet1.charge();
          bjet_charge_all_[1] = jet2.charge();
          bjet_partonPdgId_all_[0] = jet1.partonPdgId();
          bjet_partonPdgId_all_[1] = jet2.partonPdgId();
          quality_all_ = quality;
        }
        if ( quality > quality_qcut_ && findPairUsingJetCharge(lepton_charge_[0], jet1, jet2)  ) {
          j3_ = TLorentzVector( jet1.px(), jet1.py(), jet1.pz(), jet1.energy());
          j4_ = TLorentzVector( jet2.px(), jet2.py(), jet2.pz(), jet2.energy());
          bjet_charge_qcut_[0] = jet1.charge();
          bjet_charge_qcut_[1] = jet2.charge();
          bjet_partonPdgId_qcut_[0] = jet1.partonPdgId();
          bjet_partonPdgId_qcut_[1] = jet2.partonPdgId();
          quality_qcut_ = quality;
        }
      }
    }
  ttree_->Fill();
  }while(false);
}

DEFINE_FWK_MODULE(TTLLKinQualityAnalyzer);

