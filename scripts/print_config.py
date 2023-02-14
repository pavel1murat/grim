#!/usr/bin/env python
#-------------------------------------------------------------------------------------------------
# print project configuration for a given family
# 
# setup Mu2e offline before calling
#
# call: grim/scripts/print_config.py --project=su2020 --fid=bmum3 
#   project  : project name
#   fid      : dataset family ID
#   dsid     : obsolete for [dataset family ID]
#-------------------------------------------------------------------------------------------------

import subprocess, shutil, glob, random, json
import sys, string, getopt, glob, os, time, re, array

#------------------------------------------------------------------------------
class PrintConfig:

    def __init__(self):
        self.fProject       = None
        self.fProjectDir    = None
        self.fFamilyID      = 'xxx_xxxx' # just to make up 
        self.fJob           = None       # task to be executed
        self.fStage         = None
        self.fStageName     = None
        self.fJType         = None
        self.fFirstSubrun   = None;
        self.fMinSubrun     = None
        self.fMaxSubrun     = None
        self.fUser          = os.getenv('USER')
        self.fRescover       = None;
        self.fFileset       = None;
        self.fConfig        = {}
        self.fIDsID         = None;
        self.fNotar         = None

        self.fOwner         = os.getenv('USER');
        if (self.fOwner == 'mu2epro'): self.fOwner = 'mu2e';
        
        self.fVerbose       = 0

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
    def ParseParameters(self):
        name = 'ParseParameters'
        
        try:
            optlist, args = getopt.getopt(sys.argv[1:], '',
                     ['project=', 'dsid=', 'fid=', 'verbose=' ] )
 
        except getopt.GetoptError:
            self.Print(name,0,'%s' % sys.argv)
            self.Print(name,0,'Errors arguments did not parse')
            return 110

        for key, val in optlist:
            # print('key,val = ',key,val)

            if key == '--project':
                self.fProject = val
            elif key == '--dsid':
                self.fFamilyID = val
                print('"--dsid" is obsolete, use "--fid" instead\n');
            elif key == '--fid':
                self.fFamilyID = val
            elif key == '--verbose':
                self.fVerbose = int(val)

        self.fProjectDir = self.fProject+'/datasets/'+self.fFamilyID;

        if (self.fVerbose > 0): 
            print(sys.version)
            self.Print(name,1, '%s' % sys.argv)

        self.Print(name,1,'Job        = %s' % self.fJob    )
        self.Print(name,1,'Project    = %s' % self.fProject)
        self.Print(name,1,'StageName  = %s' % self.fStageName)
        self.Print(name,1,'Verbose    = %s' % self.fVerbose)
        self.Print(name,1,'Dsid       = %s' % self.fFamilyID)
        self.Print(name,1,'ProjectDir = %s' % self.fProjectDir)

        if (self.fProject == None) :
            self.Print(name,0,'Error: Project not defined - exiting!')
            sys.exit(1)


        # self.Print(name,1,'Done')
        return 0

#------------------------------------------------------------------------------
    def InitProject(self):
        name = 'InitProject'

        #------------------------------------------------------------------------------
        # define directory from where to load the init_project and perform initialization
        #------------------------------------------------------------------------------
        sys.path.append(self.fProjectDir) ; 
        self.Print (name,1,'self.fProjectDir = %s'%self.fProjectDir);
        import init_project
        self.fConfig = init_project.Project(); 
        # at this point the project is initializad and one may want to print it
        
#------------------------------------------------------------------------------
# print family 
#------------------------------------------------------------------------------
    def print_config(self):
        name = 'print_family'

        line = '----------------------------------------------------------------------------------------------------------';
        line += '----------------------------------------------------------'
        print(line)
        print('stage  input DSID       job                   N(seg) N(outputs) ',end='');
        print('   output DSID        outputFnPattern                   base FCL');
        print(line)
        for k in self.fConfig.fStage.keys():
            s = self.fConfig.fStage[k]
#------------------------------------------------------------------------------
# keys : input datasets
#------------------------------------------------------------------------------
            for idsid in s.fJob.keys():
                for job_name in s.fJob[idsid]:
                    job  = s.fJob[idsid][job_name];
                    nos  = job.n_output_streams();
                    print('%-5s %11s     %-20s %6i %7i'%(s.name(),job.input_dsid(),job.name(),job.n_segments(),nos),end=' ')
                    print('      %10s  %20s  %20s'%(job.output_dsid(0),job.output_fn_pattern(0),job.base_fcl()));
                    if (nos > 1):
                        for os in range(1,nos):
                            print('%67s  %10s %20s'%('',job.output_dsid(os),job.output_fn_pattern(os)));
            print(line);
        return 0;

#------------------------------------------------------------------------------
# main program, just make a PrintConfig instance and call its methods
#------------------------------------------------------------------------------
if (__name__ == '__main__'):

    x = PrintConfig()
    x.ParseParameters()
    x.InitProject()

    rc = x.print_config()

    sys.exit(rc);
