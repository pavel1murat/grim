// #!/usr/bin/env root.exe

#include "TTree.h"

int grid_time_ana(const char* Project, const char* Stage, const char* Job, const char* Dsid = "bmup4b0s36r0000", 
                  const char* Fileset = nullptr) {

  TTree* t = new TTree("a","a");

  TString fn = Form("/exp/mu2e/data/projects/%s/log/%s.%s_%s/",Project,Dsid,Stage,Job);
  if (Fileset) fn += Form("%s/",Fileset);
  fn += Form("timing_data/%s.%s.%s_%s.txt",Project,Dsid,Stage,Job);

  // char* fn = Form("/exp/mu2e/data/projects/%s/log/%s.s4_digi_trig/000/timing_data/%s.%s.s4_digi_trig.txt",
  //                 Project,Dsid,Project,Dsid);
  //  t->ReadFile("/exp/mu2e/data/projects/pipenu/log/bmup4b0s36r0000.s4_digi_trig/000/timing_data/pipenu.bmup4b0s36r0000.s4_digi_trig.txt");
  t->ReadFile(fn.Data());

  TString hist_name;
  if (Fileset == nullptr) hist_name = Form("%s.%s_%s",Dsid,Stage,Job);
  else                    hist_name = Form("%s.%s.%s_%s",Dsid,Fileset,Stage,Job);
  TH1F* h = new TH1F(hist_name.Data(),hist_name.Data(),1000,0,100);
  h->GetXaxis()->SetTitle("segment wall time, hours");
  
  t->Draw(Form("totwall/3600.>>%s",hist_name.Data()));

  // c1->Print("pipenu/datasets/bmup4b0/timing_data/pipenu.bmup4b0s46r0000.000.s5_reco_kk.timing_data.png")

  return 0;
}
