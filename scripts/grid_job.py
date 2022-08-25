#!/user/bin/python

import os, json, datetime, subprocess

import local_classes

kJobFinishedBit    = 0x0001;
kStatusCheckedBit  = 0x0002;
kLogsCopiedBit     = 0x0004;
kListPnfsFilesBit  = 0x0008;
kFilesUploadedBit  = 0x0010;
kLocationsAddedBit = 0x0020;

#------------------------------------------------------------------------------
class GridJob:
    def __init__(self, fn):

        dict = json.loads(open(fn).read())

        self.fGridID    = dict['id']

        self.fServer    = '';
        if ('server' in dict.keys()): self.fServer = dict['server'];

        self.fProject   = dict['project' ]
        self.fFamilyID  = dict['familyid']
        self.fIDsid     = dict['idsid'   ]
        self.fStage     = dict['stage'   ]
        self.fJType     = dict['job_name']

        self.fFileset = -1;
        if ('fileset'  in dict.keys()) : self.fFileset  = dict['fileset' ]

        self.fRecover = None;
        if ('recover' in dict.keys()) : self.fRecover = dict['recover']

        self.fSubmTime  = dict['subm_time']
        self.fDate      = dict['subm_time'].split()[0]
        self.fTime      = dict['subm_time'].split()[1]

        self.fStatus = 0;
        if ('status' in dict.keys()) : self.fStatus = int(dict['status']);

        self.fNSegments     = dict['segments']   # total number of segments
        self.fNIdle         = 0;
        self.fNHeld         = 0;
        self.fNRunning      = 0;

        self.fNSuccess = None;
        if ('nsuccess' in dict.keys()) : self.fNSuccess = dict['nsuccess'];

        self.fProjectConfig = None;
        self.fStageConfig   = None;
        self.fConfig        = None;
        
        cmd = 'cat .grid_config | grep su2020.grid_output_dir | awk \'{print $2}\''
        p = subprocess.run(cmd,shell=True,capture_output=True,universal_newlines=True)

        self.fGridOutputDir = None;
        if (p.returncode == 0):
            self.fGridOutputDir = p.stdout.strip()
        else:
            print('ERROR in GridJob::init : couldnt determine the output directory')
            return -1
        
        # print ("GridJob::__init__ fGridOutputDir : ",self.fGridOutputDir)

        cmd = 'cat .grid_config | grep su2020.log_dir | awk \'{print $2}\''
        p = subprocess.run(cmd,shell=True,capture_output=True,universal_newlines=True)

        self.fLogDir = None;
        if (p.returncode == 0):
            self.fLogDir = p.stdout.strip()
        else:
            print('ERROR in GridJob::init : couldnt determine the log directory')
            return -1
        
        # print ("GridJob::__init__ fLogDir : ",self.fLogDir)

#------------------------------------------------------------------------------
# job status is defined only if its configuration is known
# otherwise, keep the job status fiel in 'active' directory, so it would be visible
#------------------------------------------------------------------------------
    def completed(self):
        if (self.fConfig):
            if (self.fConfig.fCompletedStatus):
                return (self.fStatus >= self.fConfig.fCompletedStatus)
            else:
                return (self.fStatus >= kLocationsAddedBit)
        else:
            return False;

    def description(self):
        desc = self.fIDsid+':'+self.fStage+':'+self.fJType;
        if (self.fRecover) : 
            desc = desc+'.'+self.fRecover
        elif (self.fFileset) : 
            desc = desc+'.'+self.fFileset
           
        return desc

    def grid_output_dir(self):
        desc = self.fProject+'.'+self.input_dsid()+'.'+self.stage()+'_'+self.name();
        od = self.fGridOutputDir+'/'+os.getenv('USER')+'/workflow/'+desc+'/outstage/'+self.id()
        print('od = ',od)
        return od

    def family_id(self):
        return self.fFamilyID;

    def fileset(self):
        return self.fFileset;

    def id(self):
        return str(self.fGridID);

    def input_dsid(self):
        return self.fIDsid;

    def is_running(self):
        return ((self.fStatus & 1) == 0)

    def log_dir(self):
        return self.fLogDir+'/'+self.input_dsid()+'.'+self.stage()+'_'+self.name();

    def name(self):
        return self.fJType;

    def n_alive_segments(self):
        return self.fNRunning+self.fNIdle+self.fNHeld;

    def n_idle_segments(self):
        return self.fNIdle;

    def n_held_segments(self):
        return self.fNHeld;

    def n_segments(self):
        return self.fNSegments;

    def project(self):
        return self.fProject;

    def project_name(self):
        return self.fProject;

    def recover(self):
        return self.fRecover;

    def server(self):
        return self.fServer;

    def stage(self):
        return self.fStage;

    def stage_name(self):
        return self.fStage;

#------------------------------------------------------------------------------
# check log files. asume they are copied into the output area
#------------------------------------------------------------------------------
    def write_status_file(self,status_fn):

        t               = datetime.datetime.now()

        r               = {}
        r['id'        ] = int(self.fGridID);
        r['server'    ] = self.fServer;
        r['project'   ] = self.fProject
        r['familyid'  ] = self.fFamilyID;
        r['idsid'     ] = self.input_dsid();
        r['stage'     ] = self.fStage
        r['job_name'  ] = self.fJType
        r['fileset'   ] = self.fFileset
        r['recover'   ] = self.fRecover
        r['segments'  ] = self.fNSegments

        r['nsuccess'  ] = self.fNSuccess;

        r['subm_time' ] = self.fSubmTime;
        r['compl_time'] = t.strftime("%Y-%m-%d %H:%M:%S CDT ")
        r['status'    ] = self.fStatus
        
        rj              = json.dumps(r)
        f               = open(status_fn,'w')
        f.write(rj)
        f.close()

        return 0;

