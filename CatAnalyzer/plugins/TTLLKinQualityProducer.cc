#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "CATTools/DataFormats/interface/Muon.h"
#include "CATTools/DataFormats/interface/Electron.h"
#include "CATTools/DataFormats/interface/Jet.h"
#include "CATTools/DataFormats/interface/MET.h"
#include "CATTools/DataFormats/interface/SecVertex.h"

#include "CATTools/CatAnalyzer/interface/KinematicSolvers.h"
#include "DataFormats/Candidate/interface/LeafCandidate.h"
//#include "DataFormats/Candidate/interface/CompositeCandidate.h"
//#include "DataFormats/Candidate/interface/CompositeRefCandidate.h"
#include "DataFormats/Candidate/interface/CompositePtrCandidate.h"
#include "FWCore/ServiceRegistry/interface/Service.h"

using namespace std;

namespace cat {

class TTLLKinQualityProducer : public edm::stream::EDProducer<>
{
public:
  TTLLKinQualityProducer(const edm::ParameterSet& pset);
  virtual ~TTLLKinQualityProducer() {};
  void beginLuminosityBlock(const edm::LuminosityBlock& lumi, const edm::EventSetup&) override;
  void produce(edm::Event & event, const edm::EventSetup&) override;

private:
  edm::EDGetTokenT<edm::View<reco::CandidatePtr> > leptonPtrToken_;
  edm::EDGetTokenT<edm::View<reco::CandidatePtr> > jetPtrToken_;
  edm::EDGetTokenT<edm::View<reco::Candidate> > leptonToken_;
  edm::EDGetTokenT<edm::View<reco::Candidate> > jetToken_;
  edm::EDGetTokenT<float> metToken_, metphiToken_;
  double applyJetCharge_;

private:
  typedef reco::Candidate::LorentzVector LV;
  typedef reco::LeafCandidate Cand;
  typedef std::vector<Cand> CandColl;
  typedef std::vector<float> floats;


  typedef std::pair<Cand,Cand> CandPair;
  typedef std::pair<double ,CandPair> QCP;
  typedef std::vector< QCP > QCPs;



  std::unique_ptr<KinematicSolver> solver_;

};

}

using namespace cat;

TTLLKinQualityProducer::TTLLKinQualityProducer(const edm::ParameterSet& pset)
{
  leptonPtrToken_ = mayConsume<edm::View<reco::CandidatePtr> >(pset.getParameter<edm::InputTag>("leptons"));
  leptonToken_ = mayConsume<edm::View<reco::Candidate> >(pset.getParameter<edm::InputTag>("leptons"));
  jetPtrToken_ = mayConsume<edm::View<reco::CandidatePtr> >(pset.getParameter<edm::InputTag>("jets"));
  jetToken_ = mayConsume<edm::View<reco::Candidate> >(pset.getParameter<edm::InputTag>("jets"));
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

  produces<QCPs>();

}

void TTLLKinQualityProducer::beginLuminosityBlock(const edm::LuminosityBlock& lumi, const edm::EventSetup&)
{
  if ( dynamic_cast<DESYSmearedSolver*>(solver_.get()) != 0 ) {
    edm::Service<edm::RandomNumberGenerator> rng;
    CLHEP::HepRandomEngine& engine = rng->getEngine(lumi.index());
    dynamic_cast<DESYSmearedSolver*>(solver_.get())->setRandom(&engine);
  }
}

void TTLLKinQualityProducer::produce(edm::Event& event, const edm::EventSetup&)
{
  std::auto_ptr<QCPs> candPairs(new QCPs);

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

  std::vector<reco::CandidatePtr> jets;
  edm::Handle<edm::View<reco::CandidatePtr> > jetPtrHandle;
  edm::Handle<edm::View<reco::Candidate> > jetHandle;
  if ( event.getByToken(jetPtrToken_, jetPtrHandle) ) {
    for ( auto x : *jetPtrHandle ) jets.push_back(x);
  }
  else {
    event.getByToken(jetToken_, jetHandle);
    for ( int i=0, n=jetHandle->size(); i<n; ++i ) jets.push_back(reco::CandidatePtr(jetHandle, i));
  }

  edm::Handle<float> metHandle;
  event.getByToken(metToken_, metHandle);
  const float met = *metHandle;
  event.getByToken(metphiToken_, metHandle);
  const float metphi = *metHandle;
  const LV metLV(met*cos(metphi), met*sin(metphi), 0, met);

  do {
    // Check objects to exist
    if ( leptons.size() < 2 ) break;
    if ( jets.size() < 2 ) break;

    // Pick leading leptons.
    const auto lep1 = leptons.at(0);
    const auto lep2 = leptons.at(1);
    const LV lep1LV = lep1->p4();
    const LV lep2LV = lep2->p4();
    LV inputLV[5] = {metLV, lep1LV, lep2LV};
    LV nu1LV, nu2LV;
    double quality = -1e9; // Default quality value

    // Run the solver with all jet combinations
    reco::CandidatePtr selectedJet1, selectedJet2;
    for ( auto jet1 : jets )
    {
      inputLV[3] = jet1->p4();
      for ( auto jet2 : jets )
      {
        if ( jet1 == jet2 ) continue;
        inputLV[4] = jet2->p4();

        solver_->solve(inputLV);
          
        quality = solver_->quality();
        if ( quality <= -1e9 ) break; // failed to get solution
        selectedJet1 = jet1;
        selectedJet2 = jet2;
        Cand j1 = Cand(selectedJet1->charge(), selectedJet1->p4()); 
        Cand j2 = Cand(selectedJet2->charge(), selectedJet2->p4()); 

        CandPair jp = make_pair(j1, j2);
        QCP qjp = make_pair(quality,jp);
        candPairs->push_back(qjp);
      }
    }

  }while(false);


  event.put(candPairs);
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(TTLLKinQualityProducer);

