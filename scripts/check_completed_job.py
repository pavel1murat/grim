#!/usr/bin/env python
# interface to Andrei's generate_fcl
# call: check_completed_job.py --project=su2020 --grid_id=11122234
#-------------------------------------------------------------------------------------------------

import configparser, subprocess, shutil, json
import sys, string, getopt, glob, os, time, re, array, copy

import grid_job

class JobStatus:
    def __init__(self):
        self.fNSegments = None; 
        self.Status     = [];    # array of segment statuses

#------------------------------------------------------------------------------
class Tool:

    def __init__(self):
        self.fProject       = None
        self.fProjectDir    = None
        self.fDsid          = 'xxx_xxxx' # just to make up 
        self.fDoit          = 1
        self.fJob           = None       # task to be executed
        self.fStageName     = None
        self.fStage         = None
        self.fJType         = None
        self.fUser          = os.getenv('USER')
        self.fGridJobID     = None;
        self.fConfig        = None

        self.fOutputPath    = {}
        self.fOutputStreams = None

        self.fVerbose       = 0

        self.fRunningDir    = None;
        self.fCompletedDir  = None;
        self.fGridJob       = None;

        self.fUseRunningDir = 1
        self.fOutputCheck   = 1

# ---------------------------------------------------------------------
    def Print(self,Name,level,Message):
        if(level>self.fVerbose): return 0;
        now     = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
        message = now+' [ GridSubmit::'+Name+' ] '+Message
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
                                          ['project=', 'verbose=', 'grid_id=', 'use-running-dir=', 'output-check='] )
 
        except getopt.GetoptError:
            self.Print(name,0,'%s' % sys.argv)
            self.Print(name,0,'Errors arguments did not parse')
            return 110

        for key, val in optlist:

            # print('key,val = ',key,val)

            if key == '--project':
                self.fProject = val
            elif key == '--grid_id':
                self.fGridJobID = val.split(',')
            elif key == '--use-running-dir':
                self.fUseRunningDir = int(val)
            elif key == '--output-check':
                self.fOutputCheck = int(val)
            elif key == '--verbose':
                self.fVerbose = int(val)

        self.Print(name,1,'Done')
        return 0

#------------------------------------------------------------------------------
    def init(self, gridID):
        name = 'InitProject'

        #------------------------------------------------------------------------------
        self.Print(name,1,'GridJobID = %s' % gridID)

        # read job status file

        self.fRunningDir   = 'tmp/'+self.fProject+'/grid_job_status';
        self.fCompletedDir = 'tmp/'+self.fProject+'/completed_jobs'

        fn              = self.fRunningDir+'/'+gridID;
        if (self.fUseRunningDir == 0):
            fn          = self.fCompletedDir+'/'+gridID;
            
        self.fGridJob   = grid_job.GridJob(fn);

        # dict            = json.loads(open(fn).read())

        self.fProject   = self.fGridJob.project()
        self.fDsid      = self.fGridJob.input_dsid()[0:5]
        self.fStageName = self.fGridJob.stage()
        self.fJType     = self.fGridJob.name()
        self.fFileset   = self.fGridJob.fileset()

        self.Print(name,1,'Project      = %s' % self.fProject     )
        self.Print(name,1,'Verbose      = %s' % self.fVerbose     )
        self.Print(name,1,'StageName    = %s' % self.fGridJob.stage()   )
        self.Print(name,1,'JobName      = %s' % self.fGridJob.name() )
        self.Print(name,1,'Dsid         = %s' % self.fGridJob.input_dsid()        )
        self.Print(name,1,'GridJobID    = %s' % self.fGridJob.id() )
        self.Print(name,1,'Recover      = %s' % self.fGridJob.recover()   )

        if (self.fProject == None) :
            self.Print(name,0,'Error: Project not defined - exiting!')
            sys.exit(1)

        self.fProjectDir = self.fProject+'/datasets/'+self.fDsid[0:5];
        sys.path.append(self.fProjectDir) ; 

        self.Print(name,1,'ProjectDir   = %s' % self.fProjectDir  )

        import init_project
        #------------------------------------------------------------------------------
        # read project config file
        #------------------------------------------------------------------------------
        self.fConfig         = init_project.Project(); 

        self.fStage          = self.fConfig.fStage[self.fStageName];
        self.fJob            = copy.deepcopy(self.fStage.fJob[self.fJType]);
        self.fJob.fGridID    = gridID;

        self.fJob.fNSegments = self.fGridJob.n_segments()  # could be a recovery job

        projectName          = self.fProject;
        dsid                 = self.fDsid;
        
        self.Print(name,1,'projectName   = %s' % projectName)
        self.Print(name,1,'dsid          = %s' % dsid)
        self.Print(name,1,'self.fStage   = %s' % self.fGridJob.stage())
        self.Print(name,1,'self.fJType   = %s' % self.fGridJob.name())
        self.Print(name,1,'nsegments     = %s' % self.fGridJob.n_segments())

        return;

#------------------------------------------------------------------------------
# segment_dir : output directory of the failed segment
# job         :
# next_fcl_dir: destination for the failed segment FCL files
# fcl_file    : file to be copied
#------------------------------------------------------------------------------
    def handle_failed_segment(self,segment_dir,job,next_fcl_dir,segment_fcl):

        # make sure output files in the failed segment directory are not used
        ns = len(job.fOutputStream)
        for i in range(0,ns):
            for ext in job.fOutputFormat[i].split(':'):
                list = glob.glob(segment_dir+'/*.'+ext)
                for fn in list:
                    shutil.move(fn,fn+'.save')

        # copy fcl file of the failed segment to the destination to be tarred up for the recovery job
        if (next_fcl_dir):
            dst = next_fcl_dir+'/'+os.path.basename(segment_fcl);
            shutil.copyfile(segment_fcl, dst)

#------------------------------------------------------------------------------
# check status, job = JOB
#------------------------------------------------------------------------------
    def check_completed_job(self,job):
        name = 'check_completed_job'

        grid_output_dir = job.grid_output_dir();
        print('grid_output_dir:',grid_output_dir)
        # assume that the directory with FCL files still exist

        base_dir = os.getcwd()+'/tmp/'+self.fProject+'/fcl/'+job.input_dsid()+'.'+self.fGridJob.stage()+'_'+job.name();
        fcl_dir  = base_dir;

        if   (self.fGridJob.recover() ): fcl_dir = fcl_dir +'.'+self.fGridJob.recover();
        elif (self.fFileset ): fcl_dir = base_dir+'.'+self.fFileset;

        self.Print(name,1,'fcl_dir   = %s' % fcl_dir)

        fcl_list = glob.glob(fcl_dir+'/'+'*.fcl')
        fcl_list.sort();
        nseg     = len(fcl_list)      

        # in case next recovery step is needed
        next_fcl_dir = base_dir+'.'+job.grid_id();

        if (not os.path.exists(next_fcl_dir)): 
            os.makedirs(next_fcl_dir,exist_ok=True);

        nsuccess = 0;
        for i in range(0,nseg):
            dd = grid_output_dir+'/00/'+'%05i'%i
            self.Print(name,1,'dd   = %s' % dd)  # print('dd = ',dd)
            if (not os.path.exists(dd)):
                print('>> segment %5i: ERROR'%i,' GRID output directory doesn\'t exist, fcl: ',fcl_list[i])
                if (next_fcl_dir):
                    dst = next_fcl_dir+'/'+os.path.basename(fcl_list[i]);
                    shutil.copyfile(fcl_list[i], dst)
                continue
            #------------------------------------------------------------------------------
            # directory exists, look at the log file

            logs = glob.glob(dd+'/'+'*.log')
            if (len(logs) != 1):
                print('>> segment %5i: ERROR'%i,' no log file, fcl: ',fcl_list[i])

                self.handle_failed_segment(dd,job,next_fcl_dir,fcl_list[i])

                # # make sure output files in the failed segment directory are not used
                # ns = len(job.fOutputStream)
                # for i in range(0,ns):
                #     for ext in job.fOutputFormat[i].split(':'):
                #         list = glob.glob(dd+'/*.'+ext)
                #         for fn in list:
                #             shutil.move(fn,fn+'.save')
                # # copy fcl file of the failed segment to the destination to be tarred up for the recovery job
                # if (next_fcl_dir):
                #     dst = next_fcl_dir+'/'+os.path.basename(fcl_list[i]);
                #     shutil.copyfile(fcl_list[i], dst)

                continue;

            #------------------------------------------------------------------------------
            # this is what one expects - one log file. 
            # 1. check ART return code

            logfile = logs[0]
            cmd = 'cat '+logfile+' | grep "Art has completed"'
            self.Print(name,1,'executing cmd:%s'%cmd)
            out=os.popen(cmd).readlines()
            self.Print(name,1,'output:%s'%out)
            if (len(out) == 0):
                print('>> segment %5i: ERROR: no art return code'%i)

                self.handle_failed_segment(dd,job,next_fcl_dir,fcl_list[i]);
                # if (next_fcl_dir):
                #    dst = next_fcl_dir+'/'+os.path.basename(fcl_list[i]);
                #    shutil.copyfile(fcl_list[i], dst)
                continue;
            #------------------------------------------------------------------------------
            # art return code present , analyze it
            split_out=out[0].split();
            rc  = split_out[8].strip('.');
            if (rc != '0'):
                print('>> segment %5i: art ERROR'%i,' rc = ',rc,' fcl:',fcl_list[i])
                self.handle_failed_segment(dd,job,next_fcl_dir,fcl_list[i]);
                # if (next_fcl_dir):
                #     dst = next_fcl_dir+'/'+os.path.basename(fcl_list[i]);
                #     shutil.copyfile(fcl_list[i], dst)
                continue;

            #------------------------------------------------------------------------------
            # 2. check MU2EGRID return code

            cmd = 'cat '+logfile+' | grep "mu2egrid exit status" | awk \'{print $4}\''
            self.Print(name,1,'executing cmd:%s'%cmd)
            out=os.popen(cmd).readlines()
            self.Print(name,1,'grep mu2egrid output:%s'%out)
            if (len(out) == 0):
                print('>> segment %5i: ERROR: no mu2eprodsys return code'%i)
                self.handle_failed_segment(dd,job,next_fcl_dir,fcl_list[i]);
                # if (next_fcl_dir):
                #     dst = next_fcl_dir+'/'+os.path.basename(fcl_list[i]);
                #     shutil.copyfile(fcl_list[i], dst)
                continue;
            else:
                rc = out[0].strip()
                if (rc != '0'):
                    print('>> segment %5i: ERROR: mu2eprodsys return code not 0'%i)
                    self.handle_failed_segment(dd,job,next_fcl_dir,fcl_list[i]);
                    # if (next_fcl_dir):
                    #     dst = next_fcl_dir+'/'+os.path.basename(fcl_list[i]);
                    #     shutil.copyfile(fcl_list[i], dst)
                    continue;
            #------------------------------------------------------------------------------
            # mu2egrid return code = 0

            #------------------------------------------------------------------------------
            # seemingly, success. need to check for presence of all output files though
            #                        print('>> segment %5i:      '%i,' rc = ',rc)

            error = 0

            if (self.fOutputCheck != 0):
                nos = len(job.fOutputStream)        # number of output streams
                for stream in range(0,nos):
                    odsid    = job.fOutputDsID[stream]
                    oformats = job.fOutputFormat[stream].split(':')
                    for ext in oformats:
                        files = glob.glob(dd+'/*'+odsid+'*.'+ext)
                        nf = len(files)
                        if (nf != 1):
                            print('>> segment %5i: ERROR'%i,' wrong number of files for stream ',odsid, ' : ',nf)
                            error = error+1

            if (error == 0):
                nsuccess = nsuccess+1;
                if (self.fVerbose > 1):
                    print('>> segment %5i: OK'%i)
            else:
                self.handle_failed_segment(dd,job,next_fcl_dir,fcl_list[i]);

        #------------------------------------------------------------------------------
        # check completed, move status file to tmp/$project/completed
        #------------------------------------------------------------------------------
        self.fGridJob.fNSuccess = nsuccess;

        self.fGridJob.fStatus |= grid_job.kStatusCheckedBit ;

        if (self.fUseRunningDir == 1):
            fn_old = self.fRunningDir  +'/'+str(self.fGridJob.id());
            fn_new = self.fRunningDir+'/'+str(self.fGridJob.id())+'.tmp';

            rc     = self.fGridJob.write_status_file(fn_new);
            if (rc == 0): os.replace(fn_new,fn_old);
        else:
            fn_old = self.fCompletedDir+'/'+str(self.fGridJob.id());
            fn_new = self.fCompletedDir+'/'+str(self.fGridJob.id())+'.tmp';

            rc     = self.fGridJob.write_status_file(fn_new);
            if (rc == 0): os.replace(fn_new,fn_old);

        # print('--------------------------------------');
        print('N(total  ): ',nseg);
        print('N(success): ',nsuccess);
#------------------------------------------------------------------------------
# main program, just make a GridSubmit instance and call its methods
# assume that the initial job is listed first
#------------------------------------------------------------------------------
if (__name__ == '__main__'):

    x = Tool()
    x.ParseParameters()

    for item in x.fGridJobID:
        # allow full names 
        grid_id = item.split('@')[0]
        x.Print('main',1,'gridID::%s'%grid_id);
        x.init(grid_id)
        x.check_completed_job(x.fJob)

    sys.exit(0);
