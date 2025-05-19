#include <TH1.h>
#include <TF1.h>
#include <TFitResultPtr.h>
#include <TFitResult.h>
#include "CEventRec.hh"
#include <TChain.h>
#include "TCanvas.h"
#include <iostream>
#include <string>
#include <boost/format.hpp>
#include "CAnalysisManager.hh"
#include <TPaveText.h>
#include "TFile.h"
#include <TLine.h>


using std::vector, std::cout, std::endl;

int main(int argc, char * argv[])
{

  //prepare reconstronstructed event
  CEventRec* Event = new CEventRec;
  TChain * TreeRec = new TChain("TreeRec");
  TreeRec->SetBranchAddress("Rec", &Event);
  TreeRec->Add(argv[1]);
  TreeRec->GetEntry(0);

  //constructing NTracks histogram
  TH1D* HNHits = new TH1D("HNHits", "n tof hits", 100, 0, 100);
  HNHits->SetLineWidth(3);
  HNHits->SetLineColor(kRed);
  HNHits->SetXTitle("n tof hits");
  HNHits->SetYTitle("n");

  vector<int> volume_ids;
  int n_tof_hits = 0;

  for (uint i = 0; i < TreeRec->GetEntries(); i++) {
    n_tof_hits =0;
    TreeRec->GetEntry(i);
    for(unsigned int k = 0; k < Event->GetTotalEnergyDeposition().size(); k++) {
        unsigned int VolumeId = Event->GetVolumeId().at(k);
    

        if (VolumeId >= 200000000) { //hit in tracker
        continue;
        }
        else {
            n_tof_hits++;
        }
    }
    HNHits->Fill(n_tof_hits);   
  }


  //canvas for NTracks histogram
    TCanvas* CNHits = new TCanvas("HNHits", "HNHits", 200, 10, 900, 900);
    CNHits->SetLeftMargin(0.11);
    CNHits->SetRightMargin(0.04);
    CNHits->SetTopMargin(0.08);
    CNHits->SetLogy();
    HNHits->Draw("HIST");
    CNHits->SaveAs("n_tof_hits.pdf");
}
