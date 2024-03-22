#!/usr/bin/env python
# creates local list of output files produced by the job , places it into su2020/$dsid/catalog area
# call: grim/scripts/list_pnfs_files.py --project=su2020 --grid_id=35469055
# it is assumed that the current directory has a ".grid_status" file in it
# see 
#-------------------------------------------------------------------------------------------------

import configparser, subprocess, shutil, json
import sys, string, getopt, glob, os, time, re, array

import grid_job
#------------------------------------------------------------------------------
class ListPnfsFiles:

    def __init__(self):
        self.fProject       = None
        self.fProjectDir    = None
        self.fDsid          = 'xxx_xxxx' # just to make up 
        self.fAppend        = None
        self.fDoit          = 1
        self.fJob           = None       # task to be executed
        self.fUser          = os.getenv('USER')
        self.fRunningDir    = None;
        self.fCompletedDir  = None;
        self.fGridID        = None;
        self.fRecoveryStep  = None;
        self.fFileset       = None;    # output fileset
        self.fConfig        = None

        self.fOutputPath    = {}
        self.fOutputStreams = None

        self.fUseRunningDir = 1

        self.fVerbose       = 0

# ---------------------------------------------------------------------
    def Print(self,Name,level,Message):
        if(level>self.fVerbose): return 0;
        now = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
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
                                          ['append=', 'project=', 'verbose=', 
                                           'grid_id=', 'use-running-dir=' ] )
 
        except getopt.GetoptError:
            self.Print(name,0,'%s' % sys.argv)
            self.Print(name,0,'Errors arguments did not parse')
            return 110

        for key, val in optlist:

            # print('key,val = ',key,val)

            if key == '--project':
                self.fProject = val
            elif key == '--append':
                self.fAppend = 1
            elif key == '--grid_id':
                self.fGridID = val
                self.Print(name,1,'self.fGridID=%s'%self.fGridID)
            elif key == '--use-running-dir':
                self.fUseRunningDir = int(val)
            elif key == '--verbose':
                self.fVerbose = int(val)

        self.fRunningDir   = 'tmp/'+self.fProject+'/grid_job_status';
        self.fCompletedDir = 'tmp/'+self.fProject+'/completed_jobs'

        self.Print(name,1,'Done')
        return 0

#------------------------------------------------------------------------------
# job is of a GridJob type
#------------------------------------------------------------------------------
    def InitProject(self,job):
        name = 'InitProject'
        
        self.fProjectDir = job.project_name()+'/datasets/'+job.family_id();

        sys.path.append(self.fProject+'/datasets/mixing') ; 
        sys.path.append(self.fProjectDir) ; ## print ('self.fProjectDir = '+self.fProjectDir);
        import init_project
#------------------------------------------------------------------------------
# read project config file and cache project/state/job configuration
#------------------------------------------------------------------------------
        job.fProjectConfig = init_project.Project(job.input_dsid());
        job.fStageConfig   = job.fProjectConfig.fStage[job.stage_name()];
        job.fConfig        = job.fStageConfig.job(job.input_dsid(),job.name());
#------------------------------------------------------------------------------
# list pnfs files
#------------------------------------------------------------------------------
    def list_pnfs_files(self,job):
        name = 'list_pnfs_files'

        topdir     = job.grid_output_dir();
        self.Print(name,1,'topdir=%s'%topdir)

        # self.fProjectDir   = self.fProject+'/'+job.family_id();
        catalog_dir        = self.fProjectDir+'/catalog'

        if (not os.path.exists(catalog_dir)):
            os.mkdir(catalog_dir);
        #------------------------------------------------------------------------------
        # number of output streams
        ns = len(job.fConfig.fOutputStream)

        self.Print(name,1,'ns=%i'%ns)
        #------------------------------------------------------------------------------
        # loop over output streams
        for i in range(0,ns):
            odsid       = job.fConfig.fOutputDsID[i];
            self.Print(name,1,'i=%i,odsid=%s'%(i,odsid))
            # for each stream determine list of file extensions to be written
            extensions = job.fConfig.fOutputFormat[i].split(':')
            # loop over extensions
            for ext in extensions:
                # maintain backward compatibility
                # 'fileset' catalogs have '#{fileset_name}' appended (use Ruby notations :))
                # catalog_fn  = catalog_dir+'/'+job.fConfig.fOutputFnPattern[i]+'.'+self.fProject+'.'+ext+'.files'

                self.Print(name,1,'ext=%s job.fConfig.fOutputFnPattern[i]:%s'%(ext,job.fConfig.fOutputFnPattern[i]))
                
                catalog_fn  = catalog_dir+'/'+job.fConfig.fOutputFnPattern[i]+'.'+job.fProjectConfig.name()+'.'+ext+'.files'
                self.Print(name,1,'ext=%s catalog_fn:%s'%(ext,catalog_fn))
                if (job.fileset()): catalog_fn  = catalog_fn+'.'+job.fileset();
    
                print('i, odsid, catalog_fn=',i,odsid,catalog_fn)
    
                list_of_files = []
                list_of_dirs = glob.glob(topdir+'/*')
    
                self.Print(name,1,'list_of_dirs:%s'%format(list_of_dirs));
    
                for sd1 in list_of_dirs:
    
                    list_d1 = glob.glob(sd1+'/*')
    
                    for sd2 in list_d1 :
                        self.Print(name,1,'sd2=%s'%sd2);
                        #------------------------------------------------------------------------------
                        # skip subdirectories like 00148.915da673
                        dbn = os.path.basename(sd2);
                        if (len(dbn.split('.')) == 1) :
                            for fn in glob.glob(sd2+'/*.'+ext) : 
                                base = os.path.basename(fn);
                                od   = base.split('.')[2]
                                self.Print(name,1,'base, od, odsid: %s %s %s'%(base,od,odsid))
                                if (od == odsid) : 
                                    list_of_files.append(fn)
                #------------------------------------------------------------------------------
                # catalog file for a given stream
    
                self.Print(name,1,'>>> list_of_files:%s'%format(list_of_files));
    
                if (os.path.exists(catalog_fn)): 
                    if (self.fAppend == None):
                        print('WARNING : catalog file %s exists, RECREATE!'%catalog_fn);
                        os.remove(catalog_fn);
                        f = open(catalog_fn,'w')
                    else:
                        print('WARNING : catalog file %s exists, APPEND!'%catalog_fn);
                        f = open(catalog_fn,'a')
                else:
                    f = open(catalog_fn,'w')

                list_of_files.sort()
                for fn in list_of_files:
                    f.write(fn+'\n');
                f.close();
                #-------------------------------------------------------------------------------------
                # print catalog, just for debugging
                print('close catalog_fn:',catalog_fn)

        #------------------------------------------------------------------------------
        # done, update the job status
        #------------------------------------------------------------------------------
        job.fStatus |= grid_job.kListPnfsFilesBit;
                
#------------------------------------------------------------------------------
# main program, just make a GridSubmit instance and call its methods
#------------------------------------------------------------------------------
if (__name__ == '__main__'):

    x = ListPnfsFiles()
    x.ParseParameters()
    
    grid_id = x.fGridID.split('@')[0];
    # read job status file

    if (x.fUseRunningDir == 1): fn = x.fRunningDir   + '/'+grid_id;
    else                      : fn = x.fCompletedDir + '/'+grid_id;

    job   = grid_job.GridJob(fn);

    x.InitProject(job)

    x.list_pnfs_files(job)
    # print ('job.completed():',job.completed());
    if (job.completed()):
        #------------------------------------------------------------------------------
        # job completed, move status file to 'completed' (archival) directory
        #------------------------------------------------------------------------------
        fn_new = x.fCompletedDir+'/'+str(job.id());
        # print('job completed, fn_new = ',fn_new);
        rc     = job.write_status_file(fn_new);
        if (rc == 0): os.remove(fn);
    else:
        #------------------------------------------------------------------------------
        # job is not completed yet, keep ists status file in 'active' directory
        #------------------------------------------------------------------------------
        fn_new = fn+'.tmp'
        # print('job not completed, fn_new = ',fn_new);
        rc     = job.write_status_file(fn_new);
        if (rc == 0): os.replace(fn_new,fn);
        
    sys.exit(0);
