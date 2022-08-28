#!/usr/bin/env python3
#------------------------------------------------------------------------------
# monitor grid jobs for a given project, print a table of running ones
# supposed to be run by cron
# call: grim/scripts/grid_monitor.py --project=project_name [--delete=list] [--verbose]
#------------------------------------------------------------------------------

import configparser, subprocess, shutil, datetime, json
import sys, string, getopt, glob, os, time, re, array

import grid_job
#------------------------------------------------------------------------------
class GridMonitor:

    def __init__(self):
        self.fProject       = None;
        self.fVerbose       = 1
        self.fTmpDir        = None;
        self.fRunningDir    = None;
        self.fDescription   = 'xxxxxxxxxx'
        self.fConfigFile    = '.grid_config'
        self.fFilesToDelete = None

# ---------------------------------------------------------------------
    def Print(self,Name,level,Message):
        if (level > self.fVerbose) : return 0;
        now = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
        message = now+' [ GridMonitor::'+Name+' ] '+Message
        print(message)
        
#----------------------------------------------------------------------
# Parse the command-line parameters.
# the only required one is --project=$Project 
#------------------------------------------------------------------------------
    def parse_command_line(self):
        name = 'ParseParameters'
        
        self.Print(name,2,'Starting')
        self.Print(name,2, '%s' % sys.argv)

        try:
            optlist, args = getopt.getopt(sys.argv[1:], '',
                                          ['project=', 
                                           'delete=', 
                                           'verbose' 
                                          ]
                                         )
 
        except getopt.GetoptError:
            self.Print(name,0,'%s' % sys.argv)
            self.Print(name,0,'Errors arguments did not parse')
            return 110

        for key, val in optlist:

            # print('key,val = ',key,val)

            if key == '--project':
                self.fProject = val
            elif key == '--delete':
                self.fFilesToDelete = val;
            elif key == '--verbose':
                self.fVerbose = 1

        return 0

#------------------------------------------------------------------------------
# can run multiple projects in the same working area, 
# so before parsing the config file need to be fully initialized 
#------------------------------------------------------------------------------
    def init(self):
        name = 'InitProject'

        self.parse_command_line();
#------------------------------------------------------------------------------
# read configuration file
#------------------------------------------------------------------------------
        f = open(self.fConfigFile)

        for line in f.readlines():
            # explicitly skip comment lines 
            if (line[0] == '#') : continue
            words = line.strip().split()
            # safety: don't interpret lines with less than two words
            if (len(words) < 2) : continue
            if (words[0] == self.fProject+'.tmp_dir'):
                self.fTmpDir = words[1]
        
        if (self.fTmpDir == 'none'):
            self.Print('init',0,'ERROR: undefined self.fTmpDir , check .grid_config');
            return -1;

        self.fRunningDir   = self.fTmpDir+'/grid_job_status';
        return 0;

#------------------------------------------------------------------------------
# delete obsolete file in tmp/ (assume a comma-separated list of grid ID's on input)
#------------------------------------------------------------------------------
    def delete_files(self):
        name = 'delete_files'

        running_dir   = self.fTmpDir+'/grid_job_status'

        list = self.fFilesToDelete.split(',');
        for fn in list:
            grid_id = fn.split('@')[0] # allow for full grid job ID
            fn      = running_dir+'/'+grid_id
            os.remove(fn)

#------------------------------------------------------------------------------
# check log files. asume they are copied into the output area
#------------------------------------------------------------------------------
    def monitor(self):
        name = 'CheckOutput'

        jobs = {}
        #------------------------------------------------------------------------------
        # build list of running jobs 
        # 1. list all potentially active jobs
        #------------------------------------------------------------------------------

        running_dir   = self.fTmpDir+'/grid_job_status'
        completed_dir = self.fTmpDir+'/completed_jobs'

        for fn in glob.glob(running_dir+'/*'):
            # each file - a status file
            # print('----------- fn = ',fn)
            job            = grid_job.GridJob(fn)
            id             = job.fGridID;
            jobs[id]       = job;
        
        print('--------------------------------------------------------------------------------------------------------------------------------------------');
        print('         jobID                      job description                   status  NIdle   NHeld NRunning NTotal NSuccess      submission time   ');
        print('--------------------------------------------------------------------------------------------------------------------------------------------');

        #------------------------------------------------------------------------------
        # for each job which was running duting the last check, figure the number of running segments
        #------------------------------------------------------------------------------
        user  = os.getenv('USER');
        lines = os.popen('setup mu2egrid; jobsub_q --user='+user+' | grep -v JOBSUBJOBID').readlines();

        for id in jobs.keys():
            job = jobs[id]

            job.fNRunning = 0;
            for line in lines:
                words = line.strip().split()
                if (len(words) == 0) : continue

                # print('------------ words:',words);
                
                if (words[0].find(str(id)+'.') == 0):
                    server = words[0].split('@')[1];

                    if (job.fServer == ''): 
                        job.fServer = server;

                    if (words[5] == 'R'):
                        # segment running
                        job.fNRunning += 1;
                    elif (words[5] == 'I'):
                        # segment running
                        job.fNIdle += 1;
                    elif (words[5] == 'H'):
                        # segment running
                        job.fNHeld += 1;

        #------------------------------------------------------------------------------
        # loop over all segments again, check status
        for id in jobs.keys():
            job = jobs[id]
            # print('job id:',id,' nrunning = ',job.fNRunning);
            
            if ((job.fStatus == 0) and (job.n_alive_segments() == 0)):
                #------------------------------------------------------------------------------
                # job just finished, status , but don't move it

                job.fStatus = 1;

                fn     = self.fRunningDir+'/'+str(job.id());
                fn_new = self.fRunningDir+'/'+str(job.id())+'.tmp';

                rc     = job.write_status_file(fn_new);
                if (rc == 0): os.replace(fn_new,fn);

            print('%8s@%-20s %-40s  0x%02x %6i %6i %6i %9i'%(id,job.server(),job.description(),job.fStatus,
                                                           job.n_idle_segments(),job.n_held_segments(),
                                                           job.fNRunning,job.fNSegments),end=" ");
            if (job.fNSuccess): print('%8i'%job.fNSuccess,end=" ")
            else:               print('%8s'%""           ,end=" ")
            print('%-20s'%job.fSubmTime)
            
#------------------------------------------------------------------------------
# main program, just make a GridSubmit instance and call its methods
#------------------------------------------------------------------------------
if (__name__ == '__main__'):

    x = GridMonitor()

    x.init()

    if (x.fFilesToDelete) : x.delete_files()
    else                  : x.monitor()

    sys.exit(0);
