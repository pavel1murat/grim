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

  TH1F* h = new TH1F(Dsid,Dsid,1000,0,100);
  
  t->Draw(Form("totwall/3600.>>%s.%s_%s",Dsid,Stage,Job));

  return 0;
}
