#!/usr/bin/env python
#------------------------------------------------------------------------------
# call: grim/scripts/copy_log_files.py --project=su2020 --grid_id=35469055[,xxxxxx,[yyy]]
#       can specify a list of comma-separated grid ID's (need to go in the right order)
#------------------------------------------------------------------------------

import subprocess, shutil, json, copy
import sys, string, getopt, glob, os, time, re, array

import grid_job
#------------------------------------------------------------------------------
class CopyLogFiles:

    def __init__(self):
        self.fProject       = None
        self.fProjectDir    = None
        self.fFamilyID      = 'xxx_xxxx' # just to make up 
        self.fFileTypes     = 'log'      # or 'log,fcl' , comma-separated

        self.fUser          = os.getenv('USER')
        self.fGridIDList    = None;

        self.fOutputPath    = {}
        self.fOutputStreams = None

        self.fVerbose       = 0

        self.fRunningDir    = None;
        self.fCompletedDir  = None;
        self.fGridJob       = None;

        self.fUseRunningDir = 1
# ---------------------------------------------------------------------
    def Print(self,Name,level,Message):
        if(level>self.fVerbose): return 0;
        now     = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
        message = now+' [ CopyLogFiles::'+Name+' ] '+Message
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
    def ParseParameters(self):
        name = 'ParseParameters'
        
        self.Print(name,2,'Starting')
        self.Print(name,2, '%s' % sys.argv)

        try:
            optlist, args = getopt.getopt(sys.argv[1:], '',
                                          ['project=', 'verbose=', 'jobid=', 'grid_id=', 'use-running-dir='] )
 
        except getopt.GetoptError:
            self.Print(name,0,'%s' % sys.argv)
            self.Print(name,0,'Errors arguments did not parse')
            return 110

        for key, val in optlist:

            # print('key,val = ',key,val)

            if key == '--project':
                self.fProject = val
            elif key == '--jobid':
                self.fGridIDList = val.split(',')
            elif key == '--grid_id':
                print(" --grid_id flag is OBSOLETE, use --jobid");
                self.fGridIDList = val.split(',')
            elif key == '--use-running-dir':
                self.fUseRunningDir = int(val)
            elif key == '--verbose':
                self.fVerbose = int(val)

        self.fRunningDir   = 'tmp/'+self.fProject+'/grid_job_status';
        self.fCompletedDir = 'tmp/'+self.fProject+'/completed_jobs'

        self.Print(name,1,'Done')
        return 0

#------------------------------------------------------------------------------
# check if segment completed successfuly, return: 0 if OK, non-zero if not OK
# so far, a placeholder
#------------------------------------------------------------------------------
    def check_segment(self,subdirectory):
        return 0;

#------------------------------------------------------------------------------
# 'job': of grid_job.GridJob type 
#---v--------------------------------------------------------------------------
    def copy_log_files(self,job):
        name = 'copy_log_files'

        topdir = job.grid_output_dir();
        odir   = job.log_dir()

        if (job.fileset()):
            odir=odir+'/'+job.fileset()

        if (not os.path.exists(odir)): os.makedirs(odir,exist_ok=True);

        print('odir:',odir)
#------------------------------------------------------------------------------
# file_types is either 'log' (default) or 'log,fcl' etc
# fcl file are no longer copied - they are source into the log files
#-------v----------------------------------------------------------------------
        file_types = self.fFileTypes.split(',');
        for ext in file_types:

            # oodir = odir+'/'+ext;
            oodir = odir;
            if (not os.path.exists(oodir)): os.makedirs(oodir,exist_ok=True)

            list_of_dirs = glob.glob(topdir+'/*')
            list_of_dirs.sort()

            self.Print(name,1,'list_of_dirs:%s'%format(list_of_dirs));

            for sd1 in list_of_dirs:
                print('sd1:',sd1)
                ld1 = glob.glob(sd1+'/*')
                ld1.sort()
                for sd2 in ld1 :
                    self.Print(name,1,'sd2=%s'%sd2);
#------------------------------------------------------------------------------
# skip subdirectories like 00148.915da673
#-------------------v----------------------------------------------------------
                    dbn = os.path.basename(sd2);
                    if (len(dbn.split('.')) == 1) :
#------------------------------------------------------------------------------
# at this point, need to check whether the segment has completed successfully
# do not copy files for failed segments
# 'rc' is the return code, 0 if evethything is fine 
#-----------------------v------------------------------------------------------
                        rc = self.check_segment(sd2);
                        if (rc == 0):
                            for fn in glob.glob(sd2+'/*.'+ext) : 
                                dst = oodir+'/'+os.path.basename(fn);
                                self.Print(name,1,'fn, dst : %s %s'%(fn,dst))
                                shutil.copyfile(fn, dst)
                        else:
                            print('skip failed segment , subdirectory:',sd2)
                    else:
                        print('ERROR: wrong subdirectory name dbn=%s. Incomplete transfer ?'%dbn)
#------------------------------------------------------------------------------
# done, update the job status
#-------v----------------------------------------------------------------------
        job.fStatus |= grid_job.kLogsCopiedBit;

#------------------------------------------------------------------------------
# main program, just make a GridSubmit instance and call its methods
#------------------------------------------------------------------------------
if (__name__ == '__main__'):

    x = CopyLogFiles()
    x.ParseParameters()

    for item in x.fGridIDList:

        grid_id = item.split('@')[0]

        # read job status file
        if (x.fUseRunningDir == 1): fn = x.fRunningDir  +'/'+grid_id;
        else                      : fn = x.fCompletedDir+'/'+grid_id;

        job   = grid_job.GridJob(fn);

        doit = True;
        if (job.fStatus & grid_job.kLogsCopiedBit):
            # check if still want to proceed
            print('>>> log files of job grid_id=',grid_id,' have already been copied, do you want to proceed ? [y/n]')
            s = str(input())
            if (s[0] != 'y'): 
                doit = False;
            
        if (doit): 
            x.copy_log_files(job)
            #------------------------------------------------------------------------------
            # done, update job status file with updated status
            #------------------------------------------------------------------------------
            fn_new = fn+'.tmp'
            rc     = job.write_status_file(fn_new);
            if (rc == 0): os.replace(fn_new,fn);

    sys.exit(0);
