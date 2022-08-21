#!/usr/bin/env python3
#------------------------------------------------------------------------------
# to run, need a valid kerberos ticket
#
# call examples: 
#               su2020/scripts/build_tarball.py --project=su2020
# comments:
# ---------
# - in python 2.7,  subprocess has a different interface
#------------------------------------------------------------------------------

import subprocess, shutil, datetime 
import sys, string, getopt, glob, os, time, re, array

#------------------------------------------------------------------------------
class Tool:

    def __init__(self):
        self.fProject       = None
        self.fProjectDir    = None
        self.fDsid          = 'xxx_xxxx'  # just to make it up 
        self.fDoit          = None
        self.fStageName     = "undefined" # stage name
        self.fStage         = None;       # configuraton of the stage
        self.fJob           = None;       # configuration of the job to be run
        self.fUser          = os.getenv('USER')
        self.fGridJobID     = None;
        self.fConfig        = {}

        self.fOutputPath    = {}
        self.fOutputStreams = None

        self.fVerbose       = 1

# ---------------------------------------------------------------------
    def Print(self,Name,level,Message):
        if(level>self.fVerbose): return 0;
        now = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
        message = now+' [ build_tarball::'+Name+' ] '+Message
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
            optlist, args = getopt.getopt(sys.argv[1:], '', ['project=','verbose='])
 
        except getopt.GetoptError:
            self.Print(name,0,'%s' % sys.argv)
            self.Print(name,0,'Errors arguments did not parse')
            return 110

        for key, val in optlist:

            # print('key,val = ',key,val)

            if key == '--project':
                self.fProject = val
            elif key == '--verbose':
                self.fVerbose = int(val)

        self.Print(name,1,'Project    = %s' % self.fProject)
        self.Print(name,1,'Verbose    = %s' % self.fVerbose)

        if (self.fProject == None) :
            self.Print(name,0,'Error: Project not defined - exiting!')
            sys.exit(1)

        self.Print(name,1,'Done')
        return 0

#------------------------------------------------------------------------------
    def InitProject(self):
        name = 'InitProject'

#        sys.path.append(self.fProjectDir)
#        import init_project

        #------------------------------------------------------------------------------
        # read project config file
#        self.fConfig = init_project.Project(); # init_project.init(self.fConfig)

#        self.fStage         = self.fConfig.fStage[self.fStageName]
#        self.fJob           = self.fStage.fJob[self.fJType]

#------------------------------------------------------------------------------
# build tarball for grid submission
#------------------------------------------------------------------------------
    def build_tarball(self):
        name = 'build_tarball'

        last_offline_git_commit = os.popen('git log -p -1 | head -n 1').readlines()[0].split()[1][0:8]

        exclude_file = self.fProject+'/AAA_GRIDEXPORT_EXCLUDE.txt';


        cmd  = 'source /cvmfs/mu2e.opensciencegrid.org/setupmu2e-art.sh ; '
        cmd += 'source ./setup.sh ; '
        cmd += 'setup gridexport ; gridexport -E '+os.getenv('PWD')+'/grid_export -A '+exclude_file;

        # cmd='echo A; echo B'
        print(sys.version);

        self.Print(name,1,'executing: %s'%cmd);

        # p = subprocess.run(cmd,shell=True,capture_output=True,universal_newlines=True) # python 3

        p = subprocess.Popen(cmd,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)  # pytoh 3.6.8
        
        output, rc = p.communicate()

        self.Print(name,1,"done executing, return code:%i"%p.returncode);

        if (p.returncode == 0):
            lines       = output.decode('ascii').split('\n')
            for line in lines: print(line)

            word        = lines[2].split();
            tarball     = word[4]
            tmp_dir     = os.path.dirname(tarball)

            if (os.getenv('USER') == 'mu2epro'):
                self.Print(name,0,"ERROR: building as mu2epro, may overwrite smbdy elses tarball. Exiting");
                return;

            tarball_bn  = self.fProject+'.code.'+os.getenv('USER')+'.'+last_offline_git_commit+'.tbz';

            grid_dir     = '/pnfs/mu2e/resilient/users/'+self.fUser+'/'+self.fProject

            if (not os.path.exists(grid_dir)): os.mkdir(grid_dir)
            
            grid_tarball = grid_dir+'/'+tarball_bn;

            if os.path.exists(grid_tarball): os.remove(grid_tarball);
            
            shutil.copy(tarball,grid_tarball);

            # remove tarball and temporary directory
            os.remove(tarball);
            os.rmdir(tmp_dir);

            print(">>> [BuildTarball] : done copying the tarball to ",grid_tarball);
        else:
            # error:
            print('>>>> ERROR:',p.returncode)
            for line in output.decode('ascii').split('\n'): print(line)
#------------------------------------------------------------------------------
# main program, just make a GridSubmit instance and call its methods
#------------------------------------------------------------------------------
if (__name__ == '__main__'):

    x = Tool()

    x.ParseParameters()

    x.InitProject()

    x.build_tarball()

    sys.exit(0);
