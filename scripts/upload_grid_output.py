#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
# I think, this script is not finished yet
# call: upload_grid_output.py --project=su2020 --dsid=760_3000 --stage=ts1 --output_stream=mubeamout --grid_id=35469055
#-------------------------------------------------------------------------------------------------

import configparser, subprocess, shutil, json
import sys, string, getopt, glob, os, time, re, array

#------------------------------------------------------------------------------
class UploadGridOutput:

    def __init__(self):
        self.fProject       = None
        self.fProjectDir    = None
        self.fDsid          = 'xxx_xxxx' # just to make up 
        self.fDoit          = 1
        self.fFileTypes     = ['art']    # by default, upload only .art files
        self.fJob           = None       # task to be executed
        self.fStageName     = None
        self.fStage         = None
        self.fJType         = None
        self.fIStage        = None;
        self.fIStream       = None;
        self.fUser          = os.getenv('USER')
        self.fGridJobID     = None;
        self.fRecoveryStep  = None;
        self.fFileset       = None;    # output fileset
        self.fConfig        = None

        self.fOutputPath    = {}
        self.fOutputStreams = None

        self.fVerbose       = 0

# ---------------------------------------------------------------------
    def Print(self,Name,level,Message):
        if(level>self.fVerbose): return 0;
        now = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
        message = now+' [ UploadGridOutput::'+Name+' ] '+Message
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
                     ['doit=', 'dsid=', 'fileset=', 'ftypes=', 'grid_id=', 'job=', 'project=', 'stage=', 'verbose=' ] )
 
        except getopt.GetoptError:
            self.Print(name,0,'%s' % sys.argv)
            self.Print(name,0,'Errors arguments did not parse')
            return 110

        for key, val in optlist:

            # print('key,val = ',key,val)

            if key == '--project':
                self.fProject = val
            elif key == '--doit':
                self.fDoit = int(val)
            elif key == '--fileset':
                self.fFileset = val
            elif key == '--file-types':
                self.fFileTypes = val.split(':')
            elif key == '--job':
                self.fJType = val
            elif key == '--grid_id':
                self.fGridJobID = val
            elif key == '--dsid':
                self.fDsid = val
            elif key == '--stage':
                self.fStage = val
            elif key == '--verbose':
                self.fVerbose = int(val)

        fn              = 'tmp/su2020/grid_job_status/'+self.fGridJobID;
        dict            = json.loads(open(fn).read())

        self.fProject   = dict['project']
        self.fDsid      = dict['idsid'][0:5]
        self.fStageName = dict['stage']
        self.fJType     = dict['job_name']
        self.fFileset   = dict['fileset']

        self.Print(name,1,'Job        = %s' % self.fJob    )
        self.Print(name,1,'Project    = %s' % self.fProject)
        self.Print(name,1,'Verbose    = %s' % self.fVerbose)
        self.Print(name,1,'Doit       = %s' % self.fDoit)
        self.Print(name,1,'Dsid       = %s' % self.fDsid)
        self.Print(name,1,'ProjectDir = %s' % self.fProjectDir)

        if (self.fProject == None) :
            self.Print(name,0,'Error: Project not defined - exiting!')
            sys.exit(1)


        self.Print(name,1,'Done')
        return 0

#------------------------------------------------------------------------------
    def InitProject(self):
        name = 'InitProject'

        self.fProjectDir = self.fProject+'/datasets/'+self.fDsid[0:5];

        sys.path.append(self.fProject+'/datasets/mixing') ; 
        sys.path.append(self.fProjectDir) ; print ('self.fProjectDir = '+self.fProjectDir);
        import init_project
#------------------------------------------------------------------------------
# read project config file
#------------------------------------------------------------------------------
        self.fConfig = init_project.Project(); # init_project.init(self.fConfig)

        self.fStage  = self.fConfig.fStage[self.fStageName];
        self.fJob    = self.fStage.fJob[self.fJType];

        # step 1: need to generate fcl files 
        projectName         = self.fProject;
        dsid                = self.fDsid;
        
        self.Print(name,1,'projectName   = %s' % projectName)
        self.Print(name,1,'dsid          = %s' % projectName)
        self.Print(name,1,'self.fIStage  = %s' % self.fIStage)
        self.Print(name,1,'self.fIStream = %s' % self.fIStream)
        self.Print(name,1,'self.fStage   = %s' % self.fStage)
        self.Print(name,1,'self.fJType   = %s' % self.fJType)

        #  read grid config, if it exists

        config_dir = os.getcwd()+'/tmp/'+self.fProject+'/grid_job_status'
        name_stub  = self.fProject+'.'+self.fDsid+'.'+self.fStage.name()+'_'+self.fJob.name();

        fn1        = config_dir+'/'+name_stub+'.jobid';

        id = self.fJob.grid_id() 

        if (not self.fGridJobID):
            self.fGridJobID = 'XXXXXXXX';
        
            if (id): 
                self.fGridJobID = id;

        else:
            # use the command line definition
            self.fJob.fGridJobID = self.fGridJobID;
                
        self.Print(name,1,'self.fGridJobID = %s' % self.fGridJobID)
        return;

#------------------------------------------------------------------------------
# generate fcl 
#------------------------------------------------------------------------------
    def upload_grid_output(self,stage,job):
        name = 'list_pnfs_files'

        topdir     = job.grid_output_dir();
        print('topdir:',topdir)

        catalog_dir  = self.fProjectDir+'/catalog'
        if (not os.path.exists(catalog_dir)):
            os.mkdir(catalog_dir);

        ns = len(job.fOutputStream)

        self.Print(name,1,'ns=%i'%ns)

        for i in range(0,ns):
            odsid       = job.fOutputDsID[i];
            
            # maintain backward compatibility
            if (self.fFileset):
                catalog_fn  = catalog_dir+'/'+job.fOutputFnPattern[i]+'.'+self.fProject+'.art.files'+'.'+self.fFileset
            else:
                catalog_fn  = catalog_dir+'/'+job.fOutputFnPattern[i]+'.'+self.fProject+'.art.files'

            print('i, odsid, catalog_fn=',i,odsid,catalog_fn)

            if (os.path.exists(catalog_fn)): 
                print('WARNING : catalog file %s exists, recreate!'%catalog_fn);
                os.remove(catalog_fn);

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
                        for fn in glob.glob(sd2+'/*.art') : 
                            base = os.path.basename(fn);
                            od   = base.split('.')[2]
                            self.Print(name,1,'base, od, odsid: %s %s %s'%(base,od,odsid))
                            if (od == odsid) : 
                                list_of_files.append(fn)
            #------------------------------------------------------------------------------
            # catalog file for a given stream

            self.Print(name,1,'>>> list_of_files:%s'%format(list_of_files));

            f = open(catalog_fn,'w')
            list_of_files.sort()
            for fn in list_of_files:
                f.write(fn+'\n');
            f.close();
            #-------------------------------------------------------------------------------------
            # print catalog, just for debugging
            print('close catalog_fn:',catalog_fn)
            
#------------------------------------------------------------------------------
# main program, just make a GridSubmit instance and call its methods
#------------------------------------------------------------------------------
if (__name__ == '__main__'):

    x = UploadGridOutput()
    x.ParseParameters()
    x.InitProject()

    stage = x.fStage;
    job   = stage.fJob[x.fJType];

    x.list_pnfs_files(stage,job)


#    gs.PrintConfFile(1)
#    gs.CheckForNewFiles()
#    gs.UpdateJobStatus()
#    gs.SubmitNewJobs()
#    gs.PrintConfFile(1)
#    gs.CatExit(0)
    sys.exit(0);
