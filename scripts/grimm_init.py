#!/usr/bin/env python
#-------------------------------------------------------------------------------------------------
# interface to Andrei's generate_fcl
# 
# setup Mu2e offline before calling
#
# call: grim/scripts/grimm_init_project.py --project=pbar2m --stage=s1
# 
# --project      : project name
# --stage        : stage of the job (sometimes Mu2e uses multi-stage generation)
# --job          : 'sim' or 'stn' , more coming
#-------------------------------------------------------------------------------------------------
import socket, subprocess, shutil, glob, random, json
import sys, string, getopt, glob, os, time, re, array
import importlib

import  midas
import  midas.frontend 
import  midas.event, midas.client

import  TRACE
TRACE_NAME = "grimm"

from inspect import currentframe, getframeinfo

frameinfo = getframeinfo(currentframe())
#------------------------------------------------------------------------------
class Grimm:

    def __init__(self):
        # TRACE.Instance      = "grimm".encode();
        TRACE.TRACE(TRACE.TLVL_INFO,"-- START",TRACE_NAME)
        
        self.fProject       = None
        self.fProjectDir    = None
        self.fFamilyID      = None       # just to make up 
        self.fDsID          = None       # input dataset ID
        self.fJob           = None       # task to be executed
        self.fStage         = None
        self.fStageName     = None
        self.fJType         = None
        self.fFirstSubrun   = None;
        self.fMinSubrun     = None
        self.fMaxSubrun     = None
        self.fUser          = os.getenv('USER')
        self.fPileup        = '0';       # no pileup 
        self.fRecover       = None;
        self.fFileset       = None;
        self.fNSegments     = None;
        self.fConfig        = {}
        self.fIDsID         = None;

        self.fFclTarballDir     = '/pnfs/mu2e/scratch/users/'+os.getenv('USER')+'/fcl';
        self.fNotar             = None;
        self.fNEventsPerSegment = None;

        self.fOwner             = os.getenv('USER');
        if (self.fOwner == 'mu2epro'): self.fOwner = 'mu2e';
       

        self.fVerbose       = 0

        self.host      = 'localhost'; socket.gethostname().split('.')[0];
        self.expt_name = os.getenv("MIDAS_EXPT_NAME");

        TRACE.TRACE(TRACE.TLVL_INFO,f'self.host:{self.host} self.expt_name:{self.expt_name}',TRACE_NAME);
        
        self.client    = midas.client.MidasClient("grimm_init_project",self.host,self.expt_name,None)

        TRACE.TRACE(TRACE.TLVL_INFO,"-- END",TRACE_NAME)

# ---------------------------------------------------------------------
    def family_id(self,dsid):
        return dsid[0:7]

# ---------------------------------------------------------------------
    def odb_project_path(self,project):
        user = os.getenv("USER");
        return f'/Mu2e/Offline/{user}/grim_projects/'+project;

# ---------------------------------------------------------------------
    def Print(self,Name,level,Message):
        if (level > self.fVerbose): return 0;
        now = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
        message = now+' [ GenFcl::'+Name+' ] '+Message
        print(message)
        
#----------------------------------------------------------------------
# Parse the command-line parameters.
# the only required one is --project=$Project which defines the tiki page
# where the rest of the parameters can be found.  
# --verbose=0 only print necessary error messages etc.
# --verbose=1 (default) print some summary of what was done
# --verbose=2 print detailed summary of what was done
# --verbose=10 dump everything
#------------------------------------------------------------------------------
    def parse_parameters(self):
        name = 'parse_parameters'
        
        try:
            optlist, args = getopt.getopt(sys.argv[1:], '',
                    ['project=', 'verbose=', 'job=', 'notar', 'dsid=', 'fid=', 'stage=' ] )

        except getopt.GetoptError:
            TRACE.ERROR(f'failed to parse command line arguments:{sys.argv}',TRACE_NAME)
            return 110

        for key, val in optlist:

            # print('key,val = ',key,val)

            if key == '--project':
                self.fProject = val
            elif key == '--stage':
                self.fStageName = val
            elif key == '--fid':
                self.fFamilyID = val
            elif key == '--verbose':
                self.fVerbose = int(val)

        if (self.fVerbose > 0): 
            print(sys.version)
            self.Print(name,1, '%s' % sys.argv)

        self.Print(name,1,'Job        = %s' % self.fJob       )
        self.Print(name,1,'Project    = %s' % self.fProject   )
        self.Print(name,1,'StageName  = %s' % self.fStageName )
        self.Print(name,1,'Verbose    = %s' % self.fVerbose   )
        self.Print(name,1,'DsID       = %s' % self.fDsID      )

        if (self.fProject == None) :
            self.Print(name,0,'Error: Project not defined - exiting!')
            sys.exit(1)


        # self.Print(name,1,'Done')
        return 0

#------------------------------------------------------------------------------
# initialize project in ODB
#------------------------------------------------------------------------------
    def init(self):
        name = 'InitProject'
#------------------------------------------------------------------------------
# define directory from where to load init_project.py and perform initialization
#------------------------------------------------------------------------------
#         sys.path.append(self.fProjectDir) ; 
#         self.Print (name,1,'self.fProjectDir = %s,self.fDsID=%s'%(self.fProjectDir,self.fDsID));
#         import init_project

#        self.fConfig = init_project.Project(idsid=self.fDsID);

#        self.fStage  = self.fConfig.fStage[self.fStageName];

#        self.fJob    = self.fStage.job(self.fDsID,self.fJType);

#        self.fIDsID  = self.fJob.input_dataset().id();

#        if (self.fIDsID == None) : self.fIDsID = self.fFamilyID;

        # step 1: need to generate fcl files 
        projectName         = self.fProject;
        dsid                = self.fFamilyID;
        
        self.Print(name,1,'projectName   = %s' % self.fProject)
#        self.Print(name,1,'dsid          = %s' % self.fFamilyID)
#        self.Print(name,1,'stage         = %s' % self.fStage.name())
#        self.Print(name,1,'job           = %s' % self.fJob.name())

        return 0;

#------------------------------------------------------------------------------
# initialize ODB
#------------------------------------------------------------------------------
    def init_project_odb(self,project):

        TRACE.TRACE(TRACE.TLVL_INFO,f'-- START: project:{project}',TRACE_NAME)

        fn   = self.fProject+'.json'
        dict = json.loads(open(fn).read())
        print(f'dict:{dict}');

        odb_path = self.odb_project_path(project);

        exists = self.client.odb_exists(odb_path);
        print(f'exists:{exists}')

        if (not exists):
            self.client.odb_set(odb_path,dict);
        else:
            TRACE.TRACE(TRACE.TLVL_ERROR,f'project={project} already exists',TRACE_NAME)
            

        TRACE.TRACE(TRACE.TLVL_INFO,"-- END",TRACE_NAME)
        
#------------------------------------------------------------------------------
# project already initialized, init a given family
#------------------------------------------------------------------------------
    def init_family_odb(self,project,family):

        TRACE.TRACE(TRACE.TLVL_INFO,f'-- START: project:{project} family:{family}',TRACE_NAME)

        odb_project_path = self.odb_project_path(project);
        grim_project_dir = os.path.expandvars(self.client.odb_get(odb_project_path+'/GrimProjectDir'));

        sys.path.append(grim_project_dir+'/datasets/mixing') ; 
        sys.path.append(grim_project_dir+'/datasets/'+self.fFamilyID) ; 
#------------------------------------------------------------------------------
# self.fConfig is a configuration of the family
#------------------------------------------------------------------------------
        import init_project
        self.fConfig = init_project.Project(idsid=self.fDsID);

        self.fConfig.print();

        odb_family_path = odb_project_path+'/families/'+family;

        exists = self.client.odb_exists(odb_family_path);
        print(f'exists:{exists}')
#------------------------------------------------------------------------------
# a job in job_dict is identified by the two keys: job = job_dict[idsid][cfile]
# where cfile is a configuratin (.fcl) file
#------------------------------------------------------------------------------
        stage_dict = {}
        for k in self.fConfig.fStage.keys():
            stage = self.fConfig.fStage[k]
            stage.print()
            for idsid in stage.fJob.keys():
                print(f'idsid:{idsid}')
                if (idsid == 'undefined'): continue
                # jobs: a list of jobs with the same input dataset and different config (fcl) files
                jobs = stage.fJob[idsid]
                for cfile in jobs.keys():
                    print(f'cfile:{cfile} ');
                    job      = jobs[cfile];
                    job_dict = {}
                    job_dict['RunNumber']               = job.run_number()
                    job_dict['MaxInputFilesPerSegment'] = job.fMaxInputFilesPerSegment;
                    job_dict['Resample'               ] = job.resample()
                    job_dict['MaxMemory'              ] = job.fMaxMemory
                    job_dict['RequestedTime'          ] = job.fRequestedTime
                    job_dict['Ifdh'                   ] = job.fIfdh
                    job_dict['InputDsid'              ] = job.input_dsid()
                    job_dict['InputDefName'           ] = job.input_dataset().defname()
                    job_dict['BaseFcl'                ] = job.base_fcl()
#                    job_dict['AuxInputs'              ] = job.aux_inputs()
                    job_dict['Status'                 ] = job.status()
                    # fill job parameters

                    odb_job_path = odb_family_path+'/'+stage.name()+'_'+job.name()+'_'+idsid
                    self.client.odb_set(odb_job_path,job_dict);
            
                print(f'stage_dict:{stage_dict}');

               
        
        
        TRACE.TRACE(TRACE.TLVL_INFO,f'-- END: grim_project_dir:{grim_project_dir}',TRACE_NAME)

#------------------------------------------------------------------------------
# main program, just make a GridSubmit instance and call its methods
#------------------------------------------------------------------------------
if (__name__ == '__main__'):

    x = Grimm()
    x.parse_parameters()
    rc = x.init()

    if (rc == 0): 

        stage = x.fStage;
        # job   = stage.job(x.fDsID,x.fJType);
        if (x.fFamilyID == None):
            # initialize the project part
            rc    = x.init_project_odb(x.fProject)
        else:
            rc    = x.init_family_odb(x.fProject,x.fFamilyID)

    sys.exit(rc);


#------------------------------------------------------------------------------
def test1():
    
    x = Grimm();
    x.fProject   = 'pbar2m'
    x.fVerbose   = 1
    rc           = x.init_project_odb('pbar2m')
    
