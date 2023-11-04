#!/usr/bin/env python3
#------------------------------------------------------------------------------
# to run, need a valid kerberos ticket
#
# call examples: 
#               grim/scripts/build_tarball.py --project=su2020
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
        self.fDsid          = 'xxx_xxxx'  # just to make it up 
        self.fDoit          = None
        self.fStageName     = "undefined" # stage name
        self.fStage         = None;       # configuraton of the stage
        self.fJob           = None;       # configuration of the job to be run
        self.fUser          = os.getenv('USER')
        self.fMuseStub      = os.getenv('MUSE_STUB')
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
            optlist, args = getopt.getopt(sys.argv[1:], '', ['project=','muse-stub=','verbose='])
 
        except getopt.GetoptError:
            self.Print(name,0,'%s' % sys.argv)
            self.Print(name,0,'Errors arguments did not parse')
            return 110

        for key, val in optlist:

            # print('key,val = ',key,val)

            if key == '--project':
                self.fProject = val
            elif key == '--muse-stub':
                self.fMuseStub = val
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
# build tarball for grid submission
#------------------------------------------------------------------------------
    def build_tarball(self):
        name = 'build_tarball'

        exclude_file = self.fProject+'/AAA_GRIDEXPORT_EXCLUDE.txt';

        # assume we're in a muse work area , figure the Offline git tag
        last_offline_git_commit = os.popen('cd Offline; git log -p -1 | head -n 1; cd ..').readlines()[0].split()[1][0:8]

        # qual should be either 'debug' or 'prof'
        qual = self.fMuseStub.split('-')[1];

        cmd  = 'source /cvmfs/mu2e.opensciencegrid.org/setupmu2e-art.sh ; '
        cmd += 'setup muse -q '+qual+'; '

        cmd += 'muse tarball -x '+exclude_file;

        # cmd='echo A; echo B'
        print(sys.version);

        self.Print(name,1,'executing: %s'%cmd);

        # p = subprocess.run(cmd,shell=True,capture_output=True,universal_newlines=True) # python 3

        p = subprocess.Popen(cmd,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)  # pytoh 3.6.8
        
        output, rc = p.communicate()

        self.Print(name,1,"done executing, return code:%i"%p.returncode);

        if (p.returncode == 0):
            # parse output of 'muse tarball' - first line looks as follows
            # 'Tarball: /mu2e/data/users/murat/museTarball/tmp.y5joX2M67W/Code.tar.bz2'

            lines       = output.decode('ascii').split('\n')
            # for i in range(len(lines)):
            #     print('i, line: ',i, lines[i])

            word        = lines[0].split();
            tarball     = word[1]
            tmp_dir     = os.path.dirname(tarball)

            if (os.getenv('USER') == 'mu2epro'):
                self.Print(name,0,"ERROR: building as mu2epro, may overwrite smbdy elses tarball. Exiting");
                return;

            tarball_bn  = self.fProject+'.code.'+os.getenv('USER')+'.'+last_offline_git_commit+'.tbz';

            pattern         = self.fProject+'.code_tarball_dir'

            cmd = 'cat .grid_config | grep -v \'^#\' | grep '+pattern+' | awk \'{print $2}\''
            p = subprocess.run(cmd,shell=True,capture_output=True,universal_newlines=True)

            src_tarball_dir = None;
            if (p.returncode == 0): 
                src_tarball_dir = p.stdout.strip()
            else: 
                self.Print(name,0,"ERROR: can\'t parse .grid_config for code_tarball_dir. Exiting");
                return;

            if (src_tarball_dir == ''): src_tarball_dir = '/mu2e/data/users/'+self.fUser+'/grid';

            src_tarball_dir     = src_tarball_dir+'/'+self.fProject

            if (not os.path.exists(src_tarball_dir)): os.mkdir(src_tarball_dir)
            
            grid_tarball = src_tarball_dir+'/'+tarball_bn;

            self.Print(name,1,"grid_tarball: "+grid_tarball);

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

    x.build_tarball()

    sys.exit(0);
