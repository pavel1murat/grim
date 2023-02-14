#!/usr/bin/env python
#
# call examples: 
#               grim/scripts/submit_job.py --project=su2020 --dsid=cele0 --stage=s4 --job=sim [--doit=[yes/d]] [--fileset=...]
#
# --doit=d         : 'dry_run' mode of mu2eprodsys (this is the default)
# --doit=xrd_debug : turns on XROOTD client debugging and adds a lot of printout
#-------------------------------------------------------------------------------------------------

import subprocess, shutil, datetime
import sys, string, getopt, glob, os, time, re, array
import json

#------------------------------------------------------------------------------
class Tool:

    def __init__(self):
        self.fProject       = None
        self.fProjectDir    = None
        self.fFamilyID      = None
        self.fInputDsid     = 'xxx_xxxx'  # just to make it up 
        self.fDoit          = 'd'
        self.fStageName     = "undefined" # stage name
        self.fStage         = None;       # configuraton of the stage
        self.fJob           = None;       # configuration of the job to be run
        self.fJType         = None
        self.fIStage        = None;
        self.fIStream       = None;
        self.fUser          = os.getenv('USER')
        self.fGridJobID     = None;
        self.fRecover      = None;
        self.fFileset       = None;
        self.fConfig        = {}

        self.fOutputPath    = {}
        self.fOutputStreams = None

        self.fVerbose       = 1

# ---------------------------------------------------------------------
    def FamilyID(self,dsid):
        return dsid[0:7]

# ---------------------------------------------------------------------
    def Print(self,Name,level,Message):
        if(level>self.fVerbose): return 0;
        now = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
        message = now+' [ GridTool::'+Name+' ] '+Message
        print(message)
        
#----------------------------------------------------------------------
# Parse the command-line parameters.
# the only required one is --project=$Project which defines the tiki page
# where the rest of the parameters can be found.  Set --doit=0 to
# only compute what would be done, and not actually do it.
# --verbose=0 only print necessary error messages etc.
# --verbose=1 (default) print some summary of what was done
# --verbose=2 print detailed summary of what was done
# --verbose=10 dump everything
#------------------------------------------------------------------------------
    def ParseParameters(self):
        name = 'ParseParameters'
        
        self.Print(name,2,'Starting')
        self.Print(name,2, '%s' % sys.argv)

        try:
            optlist, args = getopt.getopt(sys.argv[1:], '',
                     ['project=', 'verbose=', 'job=', 'doit=', 'dsid=', 'fileset=', 'recover=', 'stage=' ] )
 
        except getopt.GetoptError:
            self.Print(name,0,'%s' % sys.argv)
            self.Print(name,0,'Errors arguments did not parse')
            return 110

        for key, val in optlist:

            # print('key,val = ',key,val)

            if key == '--project':
                self.fProject = val
            elif key == '--doit':
                self.fDoit = val
            elif key == '--dsid':
                self.fDsID     = val                   # 'cele0b2s51r02'
                self.fFamilyID = self.FamilyID(val);   # 'cele0b2'
            elif key == '--job':
                self.fJType = val
            elif key == '--fileset':
                self.fFileset = val
            elif key == '--recover':
                self.fRecover = val  # this is ID of the job being recovered
            elif key == '--stage':
                self.fStageName = val
            elif key == '--verbose':
                self.fVerbose = int(val)

        if (self.fRecover):
            # read parameters of the job being recovered

            fn              = 'tmp/'+self.fProject+'/grid_job_status/'+self.fRecover;
            dict            = json.loads(open(fn).read())

            self.fProject   = dict['project'  ]
            self.fFamilyID  = dict['family_id']
            self.fInputDsid = dict['idsid'    ]
            self.fStageName = dict['stage'    ]
            self.fJType     = dict['job_name' ]
            self.fFileset   = dict['fileset'  ]


        self.fProjectDir = self.fProject+'/datasets/'+self.fFamilyID;

        self.Print(name,1,'Project      = %s' % self.fProject)
        self.Print(name,1,'Verbose      = %s' % self.fVerbose)
        self.Print(name,1,'Doit         = %s' % self.fDoit)
        self.Print(name,1,'FamilyID     = %s' % self.fFamilyID)
        self.Print(name,1,'InputDsid    = %s' % self.fInputDsid)
        self.Print(name,1,'ProjectDir   = %s' % self.fProjectDir)
        self.Print(name,1,'Recover      = %s' % self.fRecover)
        self.Print(name,1,'Fileset      = %s' % self.fFileset)

        if (self.fProject == None) :
            self.Print(name,0,'Error: Project not defined - exiting !')
            sys.exit(1)

        self.Print(name,1,'------------------------------------- Done')
        return 0

#------------------------------------------------------------------------------
    def InitProject(self):
        name = 'InitProject'

        sys.path.append(self.fProjectDir)
        import init_project

        #------------------------------------------------------------------------------
        # read project config file
        self.fConfig = init_project.Project(); # init_project.init(self.fConfig)

        self.fStage         = self.fConfig.fStage[self.fStageName]
        self.fJob           = self.fStage.job(self.fDsID,self.fJType);
#------------------------------------------------------------------------------
# check log files. asume they are copied into the output area
#------------------------------------------------------------------------------
    def submit_grid_job(self,stage,job):
        name = 'submit_grid_job'


        cmd = 'cat .grid_config | grep '+self.fProject+'.code_tarball | awk \'{print $2}\''
        p = subprocess.run(cmd,shell=True,capture_output=True,universal_newlines=True)

        code_tarball = None;
        if (p.returncode == 0):
            code_tarball = p.stdout.strip()
        else:
            print('ERROR: couldnt determine the code tarball')
            return -1

#------------------------------------------------------------------------------
# for the tarball name, recover and fileset are mutually exclusive:
# - fileset is included into the name of the original tarball, 
# - recover=original grid job id is included into the name of the recovery tarball
#------------------------------------------------------------------------------
        if (self.fUser == 'mu2epro'): name_stub = 'mu2e'
        else                        : name_stub = self.fUser;

        sub_stub     = self.fStageName+'_'+self.fJType
        fcl_tb_bn    = 'cnf.'+name_stub+'.'+job.input_dataset().id()+'.'+sub_stub+'.'+self.fProject;

        if   (self.fRecover): fcl_tb_bn = fcl_tb_bn +'.'+self.fRecover;
        elif (self.fFileset): fcl_tb_bn = fcl_tb_bn +'.'+self.fFileset;

        fcl_tb_bn   += '.fcl.tbz';

        fcl_tarball  = '/pnfs/mu2e/resilient/users/'+self.fUser+'/'+self.fProject+'/'+fcl_tb_bn;

        # 
        cmd          = 'tar -tjf '+fcl_tarball+' | wc -l'

        self.Print(name,1,'executing :'+cmd)

        p            = subprocess.run(cmd,shell=True,capture_output=True,universal_newlines=True)
        nsegments    = int(p.stdout.strip())

        self.Print(name,1,'nsegments: %i'%nsegments)

        dsconf       = self.fProject
        work_project = self.fProject+'.'+job.input_dataset().id()+'.'+sub_stub
        script       = 'grim/scripts/submit_grid_job'
        stage_job    = stage.name()+':'+job.name();

        if (self.fFileset):
            stage_job = stage_job+':'+self.fFileset;

        # need to account for the potential presence of a fileset 
        if (self.fRecover):
            stage_job = stage_job+':'+self.fRecover;

        parms    = [script,
                    self.fProject,
                    job.input_dsid(),
                    stage_job,
                    job.max_memory()+':'+job.fRequestedTime+':'+job.fIfdh];

        if (self.fDoit):
            parms.append(self.fDoit)

        print('submit_grid_job: parms:',parms);

        process = subprocess.run(parms, capture_output=True, universal_newlines=True)

        if (process.returncode == 0):
            submission_record = process.stdout.split('\n')
            print(submission_record)
            # extract the grid job ID and save the output 
            jobid  = 'xxxxxxxx';
            server = 'yyyyyyyy';
            for line in submission_record:
                print(line)
                if line != '':
                    w = line.split()
                    if (w[0] == 'JobsubJobId') : 
                        jobid  = w[4].split('.')[0]
                        server = w[4].split('@')[1]
                        break
    
            # print('jobid:',jobid)

            if (jobid != 'xxxxxxxx'):
                #------------------------------------------------------------------------------
                # now, that we have the grid job ID, append it to the status file - eventually, 
                # when the daa format is figured out, that will go to the DB

                job_status_dir = 'tmp/'+self.fProject+'/grid_job_status'

                if (not os.path.exists(job_status_dir)): 
                    os.mkdir(job_status_dir);

                job_stub        = self.fProject+'.'+job.input_dsid()+'.'+stage.name()+'_'+job.name();
                status_bn       = format("%8s"%jobid) ;
                status_fn       = job_status_dir+'/'+status_bn;
                t               = datetime.datetime.now()

                r               = {}
                r['id'        ] = int(jobid)
                r['server'    ] = server
                r['project'   ] = self.fProject
                r['family_id' ] = self.fFamilyID;
                r['idsid'     ] = job.input_dsid();
                r['stage'     ] = stage.name()
                r['job_name'  ] = job.name()
                r['fileset'   ] = self.fFileset
                r['recover'   ] = self.fRecover

                self.Print(name,1,'jobid: %s , writing to json nsegments = %s'%(jobid,nsegments))
                r['segments'  ] = nsegments

                r['subm_time' ] = t.strftime("%Y-%m-%d %H:%M:%S CDT ")
                r['status'    ] = 0

                rj              = json.dumps(r)

                f               = open(status_fn,'w')
                f.write(rj)
                f.close()
        else:
            print(process.stderr)

            #------------------------------------------------------------------------------
            # also want to save a grid submission loginto a separate file
            #  dir = self.fProject+'/'+self.fDsid+'/log'
            #  fn = dir+'/'+bn+'.'+jobid
            #  f = open(fn,'w')
            #  for line in fubmission_record:
            #      f.write(line)
            #  
            #  f.close();
            #  
            #  # finally, add one line to a grid submittion summary
            #  fn = dir+'/AAA_grid_submission_summary.org'
            
           
#------------------------------------------------------------------------------
# main program, just make a GridSubmit instance and call its methods
#------------------------------------------------------------------------------
if (__name__ == '__main__'):

    x = Tool()
    x.ParseParameters()
    x.InitProject()

    stage = x.fStage;
    job   = stage.job(x.fDsID,x.fJType);

    x.submit_grid_job(stage,job)

    sys.exit(0);
