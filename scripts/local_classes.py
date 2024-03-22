#!/usr/bin/python

import os, subprocess;

#------------------------------------------------------------------------------
class Fileset:

    def __init__(self, dsid, defname):
        self.fID                      = dsid
        self.fDefName                = defname     # SAM dataset definition

        cmd = 'setup dhtools; samweb describe-definition '+self.fDefName+' | grep Dimensions:';
        p   = subprocess.run(cmd,shell=True,capture_output=True,universal_newlines=True);

        self.fDimensions = p.stdout.lstrip().rstrip().replace('Dimensions: ','')

    def defname(self):
        return self.fDefName;

    def dimensions(self):
        return self.fDimensions;

#------------------------------------------------------------------------------
# dsid is 'bpip0b0s21r0000'
# assume that 'defname' is the SAM dataset definition name, the assumption works so far
#------------------------------------------------------------------------------
class Dataset:

    def __init__(self, defname, dsid, catalog):
        self.fDefName                 = defname     # SAM dataset definition

        if (dsid != ''): self.fID     = dsid
        else           : self.fID     = defname.split('.')[2];

        self.fFileset                 = {}          # list of filesets
        self.fCatalog                 = catalog;    # 'sam' or 'local'

    def add_fileset(self,id,defname):
        self.fFileset[id] = Fileset(id,defname)

    def catalog(self):
        return self.fCatalog;

    def defname(self):
        return self.fDefName;

    def dsid(self):
        return self.fID;

    def family_id(self):
        return self.fID[0:7];

    def fileset(self,id):
        return self.fFileset[id];

    def id(self):
        return self.fID;

    def n_filesets(self):
        return len(self.fFileset);
#------------------------------------------------------------------------------
# output stream is a character: '1','2', etc, representing the output stream number
# assume N(output streams per job) < 9+26 , so a stream could be represented 
# by a single character, and capitalization ignored
#------------------------------------------------------------------------------
    def output_stream(self):
        return self.fID[9];

#------------------------------------------------------------------------------
# 'name' is the job name and, simultaneously, the name of the FCL file
#------------------------------------------------------------------------------
class Job:

    def __init__(self, name, stage = None, input_dsid = None):

        self.fName                    = name
        self.fStage                   = stage

        self.fDescription             = None
        self.fRunNumber               = -1;
        self.fType                    = ''
        self.fTarball                 = '';

        self.fInputDsID               = input_dsid;
        # print("Job.__init__ idsid: ",input_dsid)
        self.fInputDataset            = stage.project().dataset(input_dsid);
        self.fInputFileset            = None;
        self.fNSegments               = None;
        self.fNInputFiles             =  1
        self.fRecoVersion             = '00'

        self.fAuxInputs               = None

        self.fBaseFcl                 = stage.project().name()+'/datasets/'+self.family_id()+'/' + \
                                        stage.name()+'_'+name+'_'+self.family_id()+'.fcl'

        self.fMaxInputFilesPerSegment =  1
        self.fMaxSegments             = 500
        self.fNEventsPerSegment       = 10
        self.fResample                = 'no'          # yes/no
        self.fMaxMemory               = '2000MB'
        self.fRequestedTime           = '12h'
        self.fIfdh                    = 'xrootd'      # ifdh/xrootd
        self.fOutputStream            = [];
        self.fOutputDsID              = [];
        self.fOutputFnPattern         = [];
        self.fOutputFormat            = [];
        self.fGridID                  = None;
        self.fVerbose                 = None;
        self.fCompletedStatus         = None;

        pattern = self.fStage.fProject.fProjectName+'.grid_output_dir';

        # print('>>> pattern = ',pattern);

        cmd = 'cat .grid_config | grep '+pattern+' | awk \'{print $2}\''
        p = subprocess.run(cmd,shell=True,capture_output=True,universal_newlines=True)

        self.fOutputDir = None;
        if (p.returncode == 0):
            self.fOutputDir = p.stdout.strip()
        else:
            print('ERROR in GridJob::init : couldnt determine the output directory')
            return -1
        
            # print ("local_classes.Job::__init__ fOutputDir : ",self.fOutputDir)

    def base_fcl(self):
        return self.fBaseFcl

    def description(self):
        return self.stage().project().name()+'.'+self.input_dataset().id()+'.'+self.stage().name()+'_'+self.name()

    def old_description(self):
        return self.fDescription

    def family_id(self):
        return self.input_dsid()[0:7];

    def grid_id(self):
        return self.fGridID;

    def grid_output_dir(self):
        return self.fOutputDir+'/'+os.getenv('USER')+'/workflow/'+self.description()+'/outstage/'+self.grid_id()
       
    def input_dataset(self):
        return self.fInputDataset;

    def input_dsid(self):
        return self.fInputDsID;

                                    # 7 characters of the input dataset ID
    def input_dsid_stub(self):
        return self.input_dsid()[0:7];

    def input_stream(self):
        print("Job::input_stream called, dont know what it should be doing\n");
        return self.input_dsid()[8:9];

    def max_memory(self):
        return self.fMaxMemory;

    def name(self):
        return self.fName;
        
    def n_segments(self):
        # this will work for generators 
        return self.fNInputFiles;

    def n_output_streams(self):
        return len(self.fOutputStream);

    def output_dsid(self,i):
        return self.fOutputDsID[i];

    def output_fn_pattern(self,i):
        return self.fOutputFnPattern[i];

    def output_stream(self,i):
        return self.fOutputStream[i];
                                                  # like 'r01'
    def reco_version(self):
        return 'r'+self.fRecoVersion;

    def stage(self):
        return self.fStage;

#------------------------------------------------------------------------------
    def aprint(self):
        print('--- name        :',self.fName);
        print('--- description :',self.fDescription);

    def type(self):
        return self.fType;

#------------------------------------------------------------------------------
class Stage:

    def __init__(self, name, project = None):
        self.fName               = name
        self.fProject            = project
        self.fInputDataset       = {}
        self.fJob                = {}
        self.fJob['undefined']   = {}

    def name(self):
        return self.fName;

    def add_job(self, job):
        name  = job.name()
        idsid = job.input_dataset().id();
        if (idsid):
            if ((idsid in self.fJob.keys()) == False): self.fJob[idsid] = {}
            self.fJob[idsid][name] = job;
        else:
            self.fJob['undefined'][name] = job;
                
#------------------------------------------------------------------------------
# define a new job with a given 'name' and input DSID = 'idsid'
# what do we do for the generator jobs ?
#------------------------------------------------------------------------------
    def new_job(self, job_name, idsid = "undefined"):

        job = Job(job_name,self,idsid)                                  # ,input_ds);
        if ((idsid in self.fJob.keys()) == False): 
            self.fJob[idsid] = {}

        self.fJob[idsid][job_name] = job;

        return job

#------------------------------------------------------------------------------
# return job with a given name and an input dataset id 
# TODO: isn't everything defined just by the job name? 
#------------------------------------------------------------------------------
    def job(self,idsid,name):
        # print("stage::job: name,idsid:",name,idsid);
        # print("self.fJob:",self.fJob);
        try:
            return self.fJob[idsid][name];
        except:
            print("ERROR in local_classes.py Stage::job : job with name:",name," idsid:",idsid," doesnt exist. Defined jobs:"); 
            self.print();
            return None;

    def print(self) :
        print("----------- Stage printout: name=",self.fName);
        # print("fInputDataset = ",self.fInputDataset);
        # print("fJob          = ",self.fJob);
        for key in self.fJob.keys():
            job = self.fJob[key];
            for jname in job.keys():
                print("job:%-10s"%jname, "input dsid:",key);

    def project(self):
        return self.fProject;

#------------------------------------------------------------------------------
class ProjectBase:

    def __init__(self, project = 'undefined', family_id='xxxxxbx',idsid='xxxxxbxxsxxrxxxx'):
        self.fProjectName        = project;
        self.fFamilyID           = family_id;
        self.fStage              = {}
        self.fDataset            = {};
        self.fIDsID              = idsid;
        self.fInputDataset       = None;
        self.add_dataset(Dataset('undefined'                   ,'xxxxxbxsxxrxxxx','local'))
#------------------------------------------------------------------------------
# no need to have config files, can do initialization in python directly
#------------------------------------------------------------------------------
    def new_stage(self,name):
        self.fStage[name]            = Stage(name,self);
        return self.fStage[name]

    def dataset(self,dsid):
        # print("dsid = ",dsid)
        return self.fDataset[dsid];

    def add_dataset(self,ds):
        self.fDataset[ds.id()] = ds;
#------------------------------------------------------------------------------
# returns the name of the FCL file corresponding to the job - to be used by gen_fcl
#------------------------------------------------------------------------------
    def base_fcl(self,job,fcl_name):
        fmid = self.fFamilyID;              # familyID
        return self.fProjectName+'/datasets/'+fmid+'/'+job.stage().name()+'_'+fcl_name+'_'+fmid+'.fcl'

    def job_description(self,job):
        return self.fProjectName+'.'+job.input_dataset().id()+'.'+job.stage().name()+'_'+job.name()

    def name(self):
        return self.fProjectName;

    def print_datasets(self):
        for ds in self.fDataset:
            print("dsid:",ds.id())
#
