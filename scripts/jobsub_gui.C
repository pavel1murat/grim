// Mainframe macro generated from application: root.exe
// By ROOT version 6.18/04 on 2020-05-11 18:09:54

#ifndef ROOT_TGDockableFrame
#include "TGDockableFrame.h"
#endif
#ifndef ROOT_TGMenu
#include "TGMenu.h"
#endif
#ifndef ROOT_TGMdiDecorFrame
#include "TGMdiDecorFrame.h"
#endif
#ifndef ROOT_TG3DLine
#include "TG3DLine.h"
#endif
#ifndef ROOT_TGMdiFrame
#include "TGMdiFrame.h"
#endif
#ifndef ROOT_TGMdiMainFrame
#include "TGMdiMainFrame.h"
#endif
#ifndef ROOT_TGMdiMenu
#include "TGMdiMenu.h"
#endif
#ifndef ROOT_TGListBox
#include "TGListBox.h"
#endif
#ifndef ROOT_TGNumberEntry
#include "TGNumberEntry.h"
#endif
#ifndef ROOT_TGScrollBar
#include "TGScrollBar.h"
#endif
#ifndef ROOT_TGComboBox
#include "TGComboBox.h"
#endif
#ifndef ROOT_TGuiBldHintsEditor
#include "TGuiBldHintsEditor.h"
#endif
#ifndef ROOT_TGuiBldNameFrame
#include "TGuiBldNameFrame.h"
#endif
#ifndef ROOT_TGFrame
#include "TGFrame.h"
#endif
#ifndef ROOT_TGFileDialog
#include "TGFileDialog.h"
#endif
#ifndef ROOT_TGShutter
#include "TGShutter.h"
#endif
#ifndef ROOT_TGButtonGroup
#include "TGButtonGroup.h"
#endif
#ifndef ROOT_TGCanvas
#include "TGCanvas.h"
#endif
#ifndef ROOT_TGFSContainer
#include "TGFSContainer.h"
#endif
#ifndef ROOT_TGuiBldEditor
#include "TGuiBldEditor.h"
#endif
#ifndef ROOT_TGColorSelect
#include "TGColorSelect.h"
#endif
#ifndef ROOT_TGButton
#include "TGButton.h"
#endif
#ifndef ROOT_TGFSComboBox
#include "TGFSComboBox.h"
#endif
#ifndef ROOT_TGLabel
#include "TGLabel.h"
#endif
#ifndef ROOT_TRootGuiBuilder
#include "TRootGuiBuilder.h"
#endif
#ifndef ROOT_TGTab
#include "TGTab.h"
#endif
#ifndef ROOT_TGListView
#include "TGListView.h"
#endif
#ifndef ROOT_TGSplitter
#include "TGSplitter.h"
#endif
#ifndef ROOT_TGStatusBar
#include "TGStatusBar.h"
#endif
#ifndef ROOT_TGListTree
#include "TGListTree.h"
#endif
#ifndef ROOT_TGuiBldGeometryFrame
#include "TGuiBldGeometryFrame.h"
#endif
#ifndef ROOT_TGToolTip
#include "TGToolTip.h"
#endif
#ifndef ROOT_TGToolBar
#include "TGToolBar.h"
#endif

#ifndef ROOT_TGuiBldDragManager
#include "TGuiBldDragManager.h"
#endif

#ifndef ROOT_TSystem
#include "TSystem.h"
#endif

#ifndef ROOT_TDatime
#include "TDatime.h"
#endif

#include "Riostream.h"

//-----------------------------------------------------------------------------
class JobSubGui {
  // RQ_OBJECT("JobSubGui")
public: 

  enum { 
    kIN_PROGRESS = 0,
    kSUBMITTED   = 1,
    kCOMPLETED   = 2
  };

  struct StageData_t {
    TString fStage;       // 
    TString fInputDs;
    TString fTime;
    TString fXRootd;
    TString fExtras;
  };

  struct MyTabElement_t {
    TGCompositeFrame*   fFrame;
    TGTextEntry*        fTime;
    TGTextEntry*        fExtras;
    TGTabElement*       fTab;
    int                 fStatus;
    Pixel_t             fColor;
  };

  TGMainFrame*        fMainFrame;
  TGTab *fTab ;

  TString             fProject;
  TString             fDsid;

  TString             fStage;
  TString             fIStage;
  TString             fTime;
  TString             fExtraParameters;

  TGTabElement*       fActiveTab;

  MyTabElement_t      fTabElement[100];
  int                 fNTabElements;
  int                 fActiveTabID;

  Pixel_t             fGreen;		// completed stage tab tip
  Pixel_t             fYellow;		// active tab tip
  Pixel_t             fTabColor;	// non-active tab tip
  Pixel_t             fSubmittedColor;

  StageData_t         fStageData[100];
  StageData_t*        fActiveStage;

  int                 fDebugLevel;
  
  JobSubGui(const char* Project, const char* Dsid, const TGWindow *p, UInt_t w, UInt_t h, int DebugLevel = 0);
  virtual ~JobSubGui();

  void     DoTab          (Int_t id);
  void     BuildTabElement(TGTab*& Tab, MyTabElement_t& TabElement, StageData_t* StageData);
  void     BuildGui       (const TGWindow *Parent, UInt_t Width, UInt_t Height);

  void     ExecuteCommand(const char* Cmd, int PrintOnly = 0);

  void     build_tarball      ();
  void     check_grid_output  ();
  void     list_pnfs_files    ();
  void     move_stage_output  ();
  void     move_dset_to_dcache();

  void     submit_stnmaker_job();
  void     catalog_stntuples  ();
  void     set_stage_ok       ();
  void     set_stage_status   (int Status);

  void     gen_fcl            ();
  void     submit_grid_job    ();
  void     jobsub_q           ();

}; 


//-----------------------------------------------------------------------------
// initialization with the project data - in its rudimentary form
//-----------------------------------------------------------------------------
JobSubGui::JobSubGui(const char* Project, const char* Dsid, const TGWindow *p, UInt_t w, UInt_t h, int DebugLevel) {

  fProject        = Project;
  fDsid           = Dsid;
  fDebugLevel     = DebugLevel;
  fSubmittedColor = 16724889;

  fStageData[0] = StageData_t{"s1:sim" ,"gen:50_200000","12h","xrootd","."};
  fStageData[1] = StageData_t{"s2:sim" ,"s1:mubeam"    ,"10h","xrootd","."};
  fStageData[2] = StageData_t{"s3:sim" ,"s2:mubeam"    , "3h","xrootd","."};
  fStageData[3] = StageData_t{"s3:stn" ,"s3:tgtstops"  , "3h","xrootd","."};

  fStageData[4] = StageData_t{"ts1:sim","pbar:vd91"    ,"12h","ifdh"  ,"."};
  fStageData[5] = StageData_t{"ts2:sim","ts1:mubeam"   , "6h","xrootd","."};
  fStageData[6] = StageData_t{"ts3:sim","ts2:mubeam"   , "6h","xrootd","."};
  fStageData[7] = StageData_t{"ts3:stn","ts3:mubeam"   ,"10h","xrootd","."};
  fStageData[8] = StageData_t{"ts4:sim","ts3:mubeam"   ,"10h","xrootd","."};
  fStageData[9] = StageData_t{"ts4:stn","ts4:tgtstops" ,"10h","xrootd","."};

  fNTabElements = 10;  // 0:9

  BuildGui(p,w,h);
}

//-----------------------------------------------------------------------------
JobSubGui::~JobSubGui() {
   fMainFrame->Cleanup();
}


//-----------------------------------------------------------------------------
void JobSubGui::ExecuteCommand(const char* Cmd, int PrintOnly) {

  TDatime x1;
  printf("# %s : -------------- JobSubGui::ExecuteCommand : executing cmd: %s\n",x1.AsSQLString(),Cmd);


  if (PrintOnly != 1) {
    char buf[10001];
    FILE* pipe = gSystem->OpenPipe(Cmd,"r");
    while (fgets(buf,10000,pipe)) { printf("%s",buf); }
    gSystem->ClosePipe(pipe);
  }

  TDatime x2;
  printf("# %s : -------------- JobSubGui::ExecuteCommand : DONE -------------------\n",x2.AsSQLString());
}

//-----------------------------------------------------------------------------
void JobSubGui::build_tarball() {
  TString cmd;

  // ts_warm_bore/scripts/grid_job.py --verbose=1 --project=ts_warm_bore --dsid=760_1022 --stage=ts2_sim  --job=build_tarball

  TString stage = fActiveStage->fStage.Data();
  stage.ReplaceAll(':','_');

  cmd = Form("setup gridexport; %s/scripts/grid_job.py --verbose=1 --project=%s --dsid=%s --stage=%s --job=build_tarball",
	     fProject.Data(),
	     fProject.Data(),
	     fDsid.Data(),
	     stage.Data());

  ExecuteCommand(cmd.Data(),fDebugLevel);
}

//-----------------------------------------------------------------------------
void JobSubGui::move_dset_to_dcache() {
  TString cmd;

  cmd = Form("%s/scripts/move_dset_to_dcache %s %s %s %s .: NOT IMPLEMENTED YET!",
	     fProject.Data(),
	     fProject.Data(),
	     fDsid.Data(),
	     fIStage.Data(),
	     fStage.Data());

  ExecuteCommand(cmd.Data(),fDebugLevel);
}

//-----------------------------------------------------------------------------
// check grid output
//-----------------------------------------------------------------------------
void JobSubGui::check_grid_output() {
  TString cmd;

  MyTabElement_t* tab = fTabElement+fActiveTabID;
  
  TString p_stage = fActiveStage->fStage.Data();
  p_stage.ReplaceAll('_',':');

  cmd = Form("%s/scripts/check_grid_output %s %s %s %s %s",
	     fProject.Data(),
	     fProject.Data(),
	     fDsid.Data(),
	     fActiveStage->fInputDs.Data(),
	     p_stage.Data(),
	     tab->fExtras->GetText());

  ExecuteCommand(cmd.Data(),fDebugLevel);
}

//-----------------------------------------------------------------------------
void JobSubGui::move_stage_output() {
  TString cmd;

  MyTabElement_t* tab = fTabElement+fActiveTabID;

  TString p_stage = fActiveStage->fStage.Data();
  p_stage.ReplaceAll('_',':');

  cmd = Form("%s/scripts/move_stage_output %s %s %s %s %s",
	     fProject.Data(),
	     fProject.Data(),
	     fDsid.Data(),
	     fActiveStage->fInputDs.Data(),
	     p_stage.Data(),
	     tab->fExtras->GetText());

  ExecuteCommand(cmd.Data(),fDebugLevel);
}

//-----------------------------------------------------------------------------
// list PNFS files
//-----------------------------------------------------------------------------
void JobSubGui::list_pnfs_files() {
  TString cmd;

  MyTabElement_t* tab = fTabElement+fActiveTabID;

  TString p_stage = fActiveStage->fStage.Data();
  p_stage.ReplaceAll('_',':');

  cmd = Form("%s/scripts/list_pnfs_files %s %s %s %s %s",
	     fProject.Data(),
	     fProject.Data(),
	     fDsid.Data(),
	     fActiveStage->fInputDs.Data(),
	     p_stage.Data(),
	     tab->fExtras->GetText());

  ExecuteCommand(cmd.Data(),fDebugLevel);
}

//-----------------------------------------------------------------------------
// check grid output
//-----------------------------------------------------------------------------
void JobSubGui::jobsub_q() {
  TString cmd;

  cmd = Form("time jobsub_q --user murat");

  ExecuteCommand(cmd.Data(),fDebugLevel);
}

//-----------------------------------------------------------------------------
// generate fcl
//-----------------------------------------------------------------------------
void JobSubGui::gen_fcl() {
  TString cmd;

  MyTabElement_t* tab = fTabElement+fActiveTabID;

  TString p_stage = fActiveStage->fStage.Data();
  p_stage.ReplaceAll("_",":");

  cmd = Form("%s/scripts/gen_fcl %s %s %s %s .",
	     fProject.Data(),
	     fProject.Data(),
	     fDsid.Data(),
	     fActiveStage->fInputDs.Data(),
	     p_stage.Data());

  ExecuteCommand(cmd.Data(),fDebugLevel);
}

//-----------------------------------------------------------------------------
void JobSubGui::submit_grid_job() {
  TString cmd;

  MyTabElement_t* tab = fTabElement+fActiveTabID;

  TString p_stage = fActiveStage->fStage.Data();
  p_stage.ReplaceAll("_",":");

  cmd = Form("%s/scripts/submit_grid_job %s %s %s %s %s .",
	     fProject.Data(),
	     fProject.Data(),
	     fDsid.Data(),
	     fActiveStage->fInputDs.Data(),
	     p_stage.Data(),
	     tab->fTime->GetText());

  TDatime x;

  // TString istage = fIStage.Data();
  // TString jstage = fStage.Data();
  // TString time   = fTime.Data();

  // istage.ReplaceAll(':','_');
  // jstage.ReplaceAll(':','_');

  printf("* <%s> * SUBMITTED* : %s.%s.%s.%s      %s \n",x.AsSQLString(),fProject.Data(),fDsid.Data(),fActiveStage->fInputDs.Data(),fActiveStage->fStage.Data(),tab->fTime->GetText());

  ExecuteCommand(cmd.Data(),fDebugLevel);

  tab->fColor = fSubmittedColor;
}

//-----------------------------------------------------------------------------
// so far, assume running interactively, otherwise - submit grid job 
//-----------------------------------------------------------------------------
void JobSubGui::submit_stnmaker_job() {
  TString cmd;

  cmd = Form("%s/scripts/submit_stnmaker_job %s %s %s %s . &",
	     fProject.Data(),
	     fProject.Data(),
	     fDsid.Data(),
	     fActiveStage->fInputDs.Data(),
	     fActiveStage->fStage.Data());

  ExecuteCommand(cmd.Data(),fDebugLevel);
}

//-----------------------------------------------------------------------------
// so far, always an interactive command
//-----------------------------------------------------------------------------
void JobSubGui::catalog_stntuples() {
  TString cmd;

  //  Stntuple/scripts/catalog_stntuples --bluearc -b ts_warm_bore -d ${dsid}_s3_tgtstops -p .stn -D /mu2e/data/users/murat/datasets/ts_warm_bore/$dsid/s3_stn_tgtstops --install  ;

  MyTabElement_t* tab = fTabElement+fActiveTabID;


  TString istage = fActiveStage->fInputDs.Data();
  istage.ReplaceAll(':','_');

  TObjArray* ist           = istage.Tokenize("_");
  TString    input_stage   = ((TObjString*) ist->At(0))->GetString().Data();
  TString    input_dataset = ((TObjString*) ist->At(1))->GetString().Data();

  TString jstage = fActiveStage->fStage.Data();
  jstage.ReplaceAll(':','_');

  TObjArray* jst       = jstage.Tokenize("_");
  TString    job_stage = ((TObjString*) jst->At(0))->GetString().Data();
  TString    job_type  = ((TObjString*) jst->At(1))->GetString().Data();

  printf("input_stage: %s input_dataset: %s job_stage: %s job_type: %s\n",
	 input_stage.Data(),input_dataset.Data(),
	 job_stage.Data(),job_type.Data());
	 

  cmd = Form("Stntuple/scripts/catalog_stntuples --bluearc -b %s -d %s.%s -p nts.%s -D /mu2e/data/users/murat/datasets/%s/%s/%s_%s_%s --install %s",
	     fProject.Data(),
	     fDsid.Data(),
	     istage.Data(),
	     gSystem->Getenv("USER"),
	     fProject.Data(),
	     fDsid.Data(),
	     job_stage.Data(),
	     job_type.Data(),
	     input_dataset.Data(),
	     "/publicweb/m/murat/cafdfc");

  ExecuteCommand(cmd.Data(),fDebugLevel);
}

//-----------------------------------------------------------------------------
// so far, assume running interactively, otherwise - submit grid job 
//-----------------------------------------------------------------------------
void JobSubGui::set_stage_ok() {
  set_stage_status(kCOMPLETED);
}


//-----------------------------------------------------------------------------
void JobSubGui::set_stage_status(int Status) {
  TString cmd;

  TString jstage = fActiveStage->fStage.Data();
  jstage.ReplaceAll(':','_');

  TString fn=Form("%s/%s/status/%s",fProject.Data(),fDsid.Data(),jstage.Data());

  FILE* f = fopen(fn.Data(),"w");

  if (Status == kCOMPLETED) {
    fputs("COMPLETED",f);
    fTabElement[fActiveTabID].fColor = fGreen;
    fTabElement[fActiveTabID].fTab->ChangeBackground(fGreen);
  }
  else if (Status == kSUBMITTED) {
    fputs("SUBMITTED",f);
    fTabElement[fActiveTabID].fColor = fSubmittedColor;
    fTabElement[fActiveTabID].fTab->ChangeBackground(fSubmittedColor);
  }

  fclose(f);

  fTabElement[fActiveTabID].fStatus = Status;
}

//-----------------------------------------------------------------------------
// set new active tab
//-----------------------------------------------------------------------------
void JobSubGui::DoTab(Int_t id) {


  if (id != fActiveTabID) {
    int old_active = fActiveTabID;

    TGTabElement *tabel = fTab->GetTabTab(id);

    if (fActiveTab != tabel) {
      if (fTabElement[id].fStatus != kCOMPLETED) {
	tabel->ChangeBackground(fYellow);
      }
      fActiveTab->ChangeBackground(fTabElement[old_active].fColor);
      fActiveTab = tabel;
    }

    fActiveTabID = id;
    fActiveStage = &fStageData[id];
  }

  printf("Tab ID: %3i stage: %-15s istage: %-15s time: %-15s extras: %-15s title: %-15s\n",
	 id,
	 fActiveStage->fStage.Data(),
	 fActiveStage->fInputDs.Data(),
	 fTabElement[id].fTime->GetText(),
	 fTabElement[id].fExtras->GetText(),
	 fActiveTab->GetText()->Data());
}


//-----------------------------------------------------------------------------
void JobSubGui::BuildTabElement(TGTab*& Tab, MyTabElement_t& TabElement, StageData_t* StageData) {

  const char* title=StageData->fStage.Data();
  const char* input=StageData->fInputDs.Data();

  //  printf("[JobSubGui::BuildTabElement] title: %s\n",title);

  TabElement.fFrame = Tab->AddTab(title);
  int ntabs = Tab->GetNumberOfTabs();
  TabElement.fFrame->SetLayoutManager(new TGVerticalLayout(TabElement.fFrame));
  TabElement.fTab  = Tab->GetTabTab(ntabs-1);
  TabElement.fColor = TabElement.fTab->GetBackground();

  TGGroupFrame* group = new TGGroupFrame(TabElement.fFrame,Form("%s:%s stage: %s %s parameters",fProject.Data(),fDsid.Data(),title,input));
  group->SetLayoutBroken(kTRUE);
//-----------------------------------------------------------------------------
// "time:xrootd" label
//-----------------------------------------------------------------------------
  TGLabel* label = new TGLabel(group,Form("time:xrootd"));
  label->SetTextJustify(1);
  label->SetMargins(0,0,0,0);
  label->SetWrapLength(-1);
  group->AddFrame(label, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
  label->MoveResize(20,25,60,25);
//-----------------------------------------------------------------------------
// "time:xrootd" text entry
//-----------------------------------------------------------------------------
  TGFont *ufont;         // will reflect user font changes
  ufont = gClient->GetFont("-*-helvetica-medium-r-*-*-12-*-*-*-*-*-iso8859-1");

  TGGC   *uGC;                          // will reflect user GC changes

					// graphics context changes
  GCValues_t valEntry_uGC;
  valEntry_uGC.fMask = kGCForeground | kGCBackground | kGCFillStyle | kGCFont | kGCGraphicsExposures;
  gClient->GetColorByName("#000000",valEntry_uGC.fForeground);
  gClient->GetColorByName("#e8e8e8",valEntry_uGC.fBackground);
  valEntry_uGC.fFillStyle = kFillSolid;
  valEntry_uGC.fFont = ufont->GetFontHandle();
  valEntry_uGC.fGraphicsExposures = kFALSE;
  uGC = gClient->GetGC(&valEntry_uGC, kTRUE);
  
  TabElement.fTime = new TGTextEntry(group, new TGTextBuffer(14),-1,uGC->GetGC(),ufont->GetFontStruct(),kSunkenFrame | kOwnBackground);
  TabElement.fTime->SetMaxLength(4096);
  TabElement.fTime->SetAlignment(kTextLeft);

  TString time = StageData->fTime+':'+StageData->fXRootd;
  TabElement.fTime->SetText(time.Data());
  TabElement.fTime->Resize(112,TabElement.fTime->GetDefaultHeight());
  group->AddFrame(TabElement.fTime, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
  TabElement.fTime->MoveResize(90,25,70,25);
//-----------------------------------------------------------------------------
// "extras" label and text entry
//-----------------------------------------------------------------------------
  label = new TGLabel(group,Form("extras"));
  label->SetTextJustify(1);
  label->SetMargins(0,0,0,0);
  label->SetWrapLength(-1);
  group->AddFrame(label, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
  label->MoveResize(180,25,60,25);

  TabElement.fExtras = new TGTextEntry(group, new TGTextBuffer(14),-1,uGC->GetGC(),ufont->GetFontStruct(),kSunkenFrame | kOwnBackground);
  TabElement.fExtras->SetMaxLength(4096);
  TabElement.fExtras->SetAlignment(kTextLeft);
  TabElement.fExtras->SetText(" . ");
  TabElement.fExtras->Resize(112,TabElement.fExtras->GetDefaultHeight());
  group->AddFrame(TabElement.fExtras, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
  TabElement.fExtras->MoveResize(250,25,70,25);
//-----------------------------------------------------------------------------
// determine the color 
//-----------------------------------------------------------------------------
  TabElement.fStatus = kIN_PROGRESS; // in progress

  TString fn = fProject+"/"+fDsid+"/status/"+StageData->fStage.ReplaceAll(":","_");
  FILE* f = fopen(fn.Data(),"r");
  if (f) {
					// status file exists, read it
    char buf[100];
    fscanf(f,"%s" ,buf);
    TString status = buf;
    status.ToUpper();
    if (status == "COMPLETED") {
      TabElement.fStatus = kCOMPLETED;
      TabElement.fColor  = fGreen;
      TabElement.fTab->ChangeBackground(fGreen);
    }
    else if (status == "SUBMITTED") {
      TabElement.fStatus = kSUBMITTED;
      TabElement.fColor  = fSubmittedColor;
      TabElement.fTab->ChangeBackground(fSubmittedColor);
    }
  }
//-----------------------------------------------------------------------------
// finish composition of the tab element
//-----------------------------------------------------------------------------
  TabElement.fFrame->AddFrame(group, new TGLayoutHints(kLHintsNormal));
  group->MoveResize(10,10,465,70);
}

void JobSubGui::BuildGui(const TGWindow *Parent, UInt_t Width, UInt_t Height) {

//-----------------------------------------------------------------------------
// main frame
//-----------------------------------------------------------------------------
   fMainFrame = new TGMainFrame(gClient->GetRoot(),Width,Height,kMainFrame | kVerticalFrame);
   fMainFrame->SetLayoutBroken(kTRUE);
   fMainFrame->SetWindowName(Form("%s:%s",fProject.Data(),fDsid.Data()));
   fMainFrame->SetName("MainFrame");


   gClient->GetColorByName("yellow", fYellow);
   gClient->GetColorByName("green", fGreen);

//-----------------------------------------------------------------------------
// add tab holder and multiple tabs (tab elements) 
//-----------------------------------------------------------------------------
   fTab = new TGTab(fMainFrame,380,40);
   fMainFrame->AddFrame(fTab, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));

   for (int i=0; i<fNTabElements; i++) {
     BuildTabElement(fTab,fTabElement[i],&fStageData[i]);
   }

   fTab->MoveResize(10,10,550,110);  // this defines the size of the tab below the tabs line
   fTab->Connect("Selected(Int_t)", "JobSubGui", this, "DoTab(Int_t)");
//-----------------------------------------------------------------------------
// buttons - common , they do not change
//-----------------------------------------------------------------------------
   int y0        = 125;
   int button_dx = 150;
   int button_sx = 150+10;
   int button_sy =  30;
//-----------------------------------------------------------------------------
// gen_fcl and submit_grid_job
//-----------------------------------------------------------------------------
   TGTextButton* fTextButton = new TGTextButton(fMainFrame,"build_tarball",-1,TGTextButton::GetDefaultGC()(),TGTextButton::GetDefaultFontStruct(),kRaisedFrame);
   fTextButton->SetTextJustify(36);
   fTextButton->SetMargins(0,0,0,0);
   fTextButton->SetWrapLength(-1);
   fTextButton->MoveResize(10,y0,button_dx,25);
   fMainFrame->AddFrame(fTextButton, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
   fTextButton->Connect("Pressed()", "JobSubGui", this, "build_tarball()");

   fTextButton = new TGTextButton(fMainFrame,"gen_fcl",-1,TGTextButton::GetDefaultGC()(),TGTextButton::GetDefaultFontStruct(),kRaisedFrame);
   fTextButton->SetTextJustify(36);
   fTextButton->SetMargins(0,0,0,0);
   fTextButton->SetWrapLength(-1);
   fTextButton->MoveResize(10,y0+button_sy,button_dx,25);
   fMainFrame->AddFrame(fTextButton, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
   fTextButton->Connect("Pressed()", "JobSubGui", this, "gen_fcl()");

   fTextButton = new TGTextButton(fMainFrame,"submit_grid_job",-1,TGTextButton::GetDefaultGC()(),TGTextButton::GetDefaultFontStruct(),kRaisedFrame);
   fTextButton->SetTextJustify(36);
   fTextButton->SetMargins(0,0,0,0);
   fTextButton->SetWrapLength(-1);
   fTextButton->MoveResize(10,y0+2*button_sy,button_dx,25);
   fMainFrame->AddFrame(fTextButton, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
   fTextButton->Connect("Pressed()", "JobSubGui", this, "submit_grid_job()");

   fTextButton = new TGTextButton(fMainFrame,"jobsub_q",-1,TGTextButton::GetDefaultGC()(),TGTextButton::GetDefaultFontStruct(),kRaisedFrame);
   fTextButton->SetTextJustify(36);
   fTextButton->SetMargins(0,0,0,0);
   fTextButton->SetWrapLength(-1);
   fTextButton->MoveResize(10,y0+button_sy*3,button_dx,25);
   fMainFrame->AddFrame(fTextButton, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
   fTextButton->Connect("Pressed()", "JobSubGui", this, "jobsub_q()");  
//-----------------------------------------------------------------------------
// check_grid_output etc
//-----------------------------------------------------------------------------
   fTextButton = new TGTextButton(fMainFrame,"check_grid_output",-1,TGTextButton::GetDefaultGC()(),TGTextButton::GetDefaultFontStruct(),kRaisedFrame);
   fTextButton->SetTextJustify(36);
   fTextButton->SetMargins(0,0,0,0);
   fTextButton->SetWrapLength(-1);
   fTextButton->MoveResize(10+button_sx,y0,button_dx,25);
   fMainFrame->AddFrame(fTextButton, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
   fTextButton->Connect("Pressed()", "JobSubGui", this, "check_grid_output()");

   fTextButton = new TGTextButton(fMainFrame,"move_stage_output",-1,TGTextButton::GetDefaultGC()(),TGTextButton::GetDefaultFontStruct(),kRaisedFrame);
   fTextButton->SetTextJustify(36);
   fTextButton->SetMargins(0,0,0,0);
   fTextButton->SetWrapLength(-1);
   fTextButton->MoveResize(10+button_sx,y0+button_sy,150,25);
   fMainFrame->AddFrame(fTextButton, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
   fTextButton->Connect("Pressed()", "JobSubGui", this, "move_stage_output()");

   fTextButton = new TGTextButton(fMainFrame,"list_pnfs_files",-1,TGTextButton::GetDefaultGC()(),TGTextButton::GetDefaultFontStruct(),kRaisedFrame);
   fTextButton->SetTextJustify(36);
   fTextButton->SetMargins(0,0,0,0);
   fTextButton->SetWrapLength(-1);
   fTextButton->MoveResize(10+button_sx,y0+button_sy*2,150,25);
   fMainFrame->AddFrame(fTextButton, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
   fTextButton->Connect("Pressed()", "JobSubGui", this, "list_pnfs_files()");
//-----------------------------------------------------------------------------
// submit_stnmaker_job and catalog_stntuples
//-----------------------------------------------------------------------------
   fTextButton = new TGTextButton(fMainFrame,"submit_stnmaker_job",-1,TGTextButton::GetDefaultGC()(),TGTextButton::GetDefaultFontStruct(),kRaisedFrame);
   fTextButton->SetTextJustify(36);
   fTextButton->SetMargins(0,0,0,0);
   fTextButton->SetWrapLength(-1);
   fTextButton->MoveResize(10+2*button_sx,y0,150,25);
   fMainFrame->AddFrame(fTextButton, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
   fTextButton->Connect("Pressed()", "JobSubGui", this, "submit_stnmaker_job()");

   fTextButton = new TGTextButton(fMainFrame,"catalog_stntuples",-1,TGTextButton::GetDefaultGC()(),TGTextButton::GetDefaultFontStruct(),kRaisedFrame);
   fTextButton->SetTextJustify(36);
   fTextButton->SetMargins(0,0,0,0);
   fTextButton->SetWrapLength(-1);
   fTextButton->MoveResize(10+2*button_sx,y0+button_sy,150,25);
   fMainFrame->AddFrame(fTextButton, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
   fTextButton->Connect("Pressed()", "JobSubGui", this, "catalog_stntuples()");

   fTextButton = new TGTextButton(fMainFrame,"ok",-1,TGTextButton::GetDefaultGC()(),TGTextButton::GetDefaultFontStruct(),kRaisedFrame);
   fTextButton->SetTextJustify(36);
   fTextButton->SetMargins(0,0,0,0);
   fTextButton->SetWrapLength(-1);
   fTextButton->MoveResize(10+2*button_sx,y0+2*button_sy,150,25);
   fMainFrame->AddFrame(fTextButton, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
   fTextButton->Connect("Pressed()", "JobSubGui", this, "set_stage_ok()");
//-----------------------------------------------------------------------------
// set active tab
//-----------------------------------------------------------------------------
   fActiveTabID = 0;
   fActiveStage = &fStageData[0];
   fTab->SetTab(fActiveTabID);

   fActiveTab = fTabElement[fActiveTabID].fTab; // fTab->GetTabTab(0);
   fTabColor  = fActiveTab->GetBackground();

   fActiveTab->ChangeBackground(fYellow);

   fMainFrame->SetMWMHints(kMWMDecorAll,
			   kMWMFuncAll,
			   kMWMInputModeless);
   fMainFrame->MapSubwindows();

   fMainFrame->Resize(fMainFrame->GetDefaultSize());
   fMainFrame->MapWindow();
   fMainFrame->Resize(590,y0+4*button_sy);  // window size 
}


//-----------------------------------------------------------------------------
void jobsub_gui(const char* Project, const char* Dsid, int DebugLevel = 0) {
  JobSubGui* x = new JobSubGui(Project,Dsid,gClient->GetRoot(),150,650,DebugLevel);
  //  return x;
}  
