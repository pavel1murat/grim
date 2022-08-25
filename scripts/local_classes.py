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

    def dsid_stub(self):
        return self.fID[0:5];

    def fileset(self,id):
        return self.fFileset[id];

    def id(self):
        return self.fID;

    def n_filesets(self):
        return len(self.fFileset);

#------------------------------------------------------------------------------
class Job:

    def __init__(self, name, stage = None):

        self.fName                    = name
        self.fStage                   = stage

        self.fDescription             = None
        self.fRunNumber               = -1;
        self.fType                    = ''
        self.fTarball                 = '';

        self.fInputDataset            = None;
        self.fInputFileset            = None;
        self.fNSegments               = None;
        self.fNInputFiles             =  1

        self.fAuxInputs               = None
        self.fBaseFcl                 = 'undefined.fcl'
        self.fMaxInputFilesPerSegment =  1
        self.fMaxSegments             = 500
        self.fNEventsPerSegment       = 10
        self.fResample                = 'no'   # yes/no
        self.fMaxMemory               = '2000MB'
        self.fRequestedTime           = '12h'
        self.fIfdh                    = 'xrootd' # ifdh/xrootd
        self.fOutputStream            = [];
        self.fOutputDsID              = [];
        self.fOutputFnPattern         = [];
        self.fOutputFormat            = [];
        self.fGridID                  = None;
        self.fVerbose                 = None;
        self.fCompletedStatus         = None;

        pattern = self.fStage.fProject.fProjectName+'.grid_output_dir';
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
        return self.fDescription

    def grid_id(self):
        return self.fGridID;

    def grid_output_dir(self):
        return self.fOutputDir+'/'+os.getenv('USER')+'/workflow/'+self.description()+'/outstage/'+self.grid_id()
       
    def input_dataset(self):
        return self.fInputDataset;

    def input_dsid(self):
        return self.input_dataset().id();

                                    # 5 characters of the input dataset ID
    def input_dsid_stub(self):
        return self.input_dsid()[0:5];

    def input_stream(self):
        return self.input_dsid()[7:8];

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
        self.fJob                = {}

    def name(self):
        return self.fName;

    def add_job(self, job):
        name = job.name()
        self.fJob[name] = job

    def new_job(self, name):
        self.fJob[name] = Job(name,self)
        return self.fJob[name]

    def job(self, name):
        return self.fJob[name]
