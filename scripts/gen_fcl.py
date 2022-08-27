#!/usr/bin/env python
#-------------------------------------------------------------------------------------------------
# interface to Andrei's generate_fcl
# 
# setup Mu2e offline before calling
#
# call: pmgrid/scripts/gen_fcl.py --project=su2020 --dsid=bmum3 --stage=s2  --job=sim [--recover=grid_id] [--fileset=xxxx]
#   project  : project name
#   idsid    : input dataset id
#   stage    : stage of the job (sometimes Mu2e uses multi-stage generation)
#   job      : 'sim' or 'stn' , more coming
#   recover  : text string labeling the recovery step
#              it is appended to the FCL tarball and the directory containing the FCL files for recovery jobs 
#              that directory is supposed to contain only FCL files for segments to be resubmitted
#-------------------------------------------------------------------------------------------------

import subprocess, shutil, glob, random, json
import sys, string, getopt, glob, os, time, re, array

#------------------------------------------------------------------------------
class Tool:

    def __init__(self):
        self.fProject       = None
        self.fProjectDir    = None
        self.fDsid          = 'xxx_xxxx' # just to make up 
        self.fJob           = None       # task to be executed
        self.fStage         = None
        self.fStageName     = None
        self.fJType         = None
        self.fFirstSubrun   = None;
        self.fMinSubrun     = None
        self.fMaxSubrun     = None
        self.fUser          = os.getenv('USER')
        self.fRecover       = None;
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
                     ['project=', 'verbose=', 'job=', 'notar', 'dsid=', 'fileset=', 'first-subrun=', 'stage=', 'recover=' ] )
 
        except getopt.GetoptError:
            self.Print(name,0,'%s' % sys.argv)
            self.Print(name,0,'Errors arguments did not parse')
            return 110

        for key, val in optlist:

            # print('key,val = ',key,val)

            if key == '--project':
                self.fProject = val
            elif key == '--dsid':
                self.fDsid = val
            elif key == '--fileset':
                self.fFileset = val
            elif key == '--first-subrun':
                self.fFirstSubrun = int(val)
            elif key == '--job':
                self.fJType = val
            elif key == '--notar':
                self.fNotar = 1
            elif key == '--recover':
                self.fRecover = val
            elif key == '--subruns':
                self.fMinSubrun = val.split(':')[0]
                self.fMaxSubrun = val.split(':')[1]
            elif key == '--stage':
                self.fStageName = val
            elif key == '--verbose':
                self.fVerbose = int(val)

        # read job status file

        if (self.fRecover):
            self.fGridID    = self.fRecover;
            fn              = 'tmp/'+self.fProject+'/grid_job_status/'+self.fGridID;
            dict            = json.loads(open(fn).read())

            self.fProject   = dict['project' ]
            self.fDsid      = dict['idsid'   ][0:5]
            self.fStageName = dict['stage'   ]
            self.fJType     = dict['job_name']
            self.fFileset   = dict['fileset' ]


        self.fProjectDir = self.fProject+'/datasets/'+self.fDsid;

        if (self.fVerbose > 0): 
            print(sys.version)
            self.Print(name,1, '%s' % sys.argv)

        self.Print(name,1,'Job        = %s' % self.fJob    )
        self.Print(name,1,'Project    = %s' % self.fProject)
        self.Print(name,1,'StageName  = %s' % self.fStageName)
        self.Print(name,1,'Verbose    = %s' % self.fVerbose)
        self.Print(name,1,'Dsid       = %s' % self.fDsid)
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
        # efine directory from where to load the init_project and perform initialization
        #------------------------------------------------------------------------------
        sys.path.append(self.fProjectDir) ; 
        self.Print (name,1,'self.fProjectDir = %s'%self.fProjectDir);
        import init_project
        self.fConfig = init_project.Project(); # init_project.init(self.fConfig)

        self.fStage  = self.fConfig.fStage[self.fStageName];
        self.fJob    = self.fStage.fJob[self.fJType];

        self.fIDsID  = self.fJob.input_dataset().id();
        if (self.fIDsID == None) : self.fIDsID = self.fDsid;

        # step 1: need to generate fcl files 
        projectName         = self.fProject;
        dsid                = self.fDsid;
        
        self.Print(name,1,'projectName   = %s' % projectName)
        self.Print(name,1,'dsid          = %s' % dsid)
        self.Print(name,1,'stage         = %s' % self.fStage.name())
        self.Print(name,1,'job           = %s' % self.fJob.name())

#------------------------------------------------------------------------------
# make FCL tarball 
#------------------------------------------------------------------------------
    def make_fcl_tarball(self,fcldir,tarball):
        name = 'make_fcl_tarbal';

        # print('>>> [make_fcl_tarball] fcldir:',fcldir,' tarball: ',tarball);

        # cmd     = ['su2020/scripts/make_fcl_tarball',fcldir,tarball]

        cmd     = 'cd '+fcldir+'; tar -cjf '+tarball+' *.fcl';

        process = subprocess.run(cmd,shell=True,capture_output=True,universal_newlines=True);
        
        self.Print(name,1,"tarball created");

        if (process.returncode != 0):
            print(" ------------ gen_fcl.py in trouble 003! ")
            print(process.stderr.split('\n'));
#------------------------------------------------------------------------------
# move tarball with the fcl files for the simulation jobs to PNFS
#------------------------------------------------------------------------------
      
        tar_on_pnfs = '/pnfs/mu2e/resilient/users/'+os.getenv('USER')+'/'+self.fProject+'/'+os.path.basename(tarball)

        if (os.path.exists(tar_on_pnfs)):
            print('WARNING: '+tar_on_pnfs+' already exists, OVERWRITING !')
            os.remove(tar_on_pnfs);

        self.Print(name,1,'copy %s  to %s'%(tarball,tar_on_pnfs));
        shutil.copyfile(tarball,tar_on_pnfs);

        self.Print(name,1,'DONE copying tarball')

#------------------------------------------------------------------------------
# post-process directory with FCL files 
# 
#------------------------------------------------------------------------------
    def postprocess_fcl_directory(self,fcldir,index):
        name = 'postprocess_fcl_directory'

        self.Print(name,1,'START')
#------------------------------------------------------------------------------
# remove all .json files - don't need them for fcl's
#------------------------------------------------------------------------------
        cmd = 'rm '+fcldir+'/*.json'
        os.system(cmd);

        list_of_fcls = glob.glob(fcldir+'/*.fcl');
        list_of_fcls.sort();
        nfiles       = len(list_of_fcls)

        for i in range(0,nfiles):
            fcl_fn     = list_of_fcls[i]
            self.Print(name,1,"i : %i, fcl_fn:%s"%(i,fcl_fn))

            #------------------------------------------------------------------------------
            # form STNTUPLE filename
            bn         = os.path.basename(fcl_fn);

            fields     = bn.split('.');
            sfields    = fields.copy()

            sfields[0] = 'nts'
            sfields[2] = job.output_dsid(0)
            sfields[5] = 'stn'
            stn_fn     = '.'.join(sfields)

            fields[4]  = "%05i_"%i+fields[4]
            new_bn     = '.'.join(fields)

            self.Print(name,1,"bn:%s, new_bn:%s:"%(bn,new_bn))

            new_fn     = new_bn

            if (fcldir != ''): 
                new_fn = fcldir+'/'+new_bn

            os.rename(fcl_fn,new_fn);
#------------------------------------------------------------------------------
# re-read the FCL file and correct some things
#------------------------------------------------------------------------------
            f    = open(new_fn)
            fn1  = new_fn+'.tmp'
            f1   = open(fn1,'w')

            for line in f.readlines():
                # process Andrei's templa
                if ('MU2EGRIDDSOWNER' in line): line = line.replace('MU2EGRIDDSOWNER',self.fOwner)
                if ('MU2EGRIDDSCONF'  in line): line = line.replace('MU2EGRIDDSCONF' ,self.fProject)

                words = line.split(':')
                key   = words[0].strip();
                kfields = key.split('.')
                # print(' kfields : ',kfields);
                #------------------------------------------------------------------------------
                # define STNTUPLE filename
                #------------------------------------------------------------------------------
                if (key == 'physics.analyzers.InitStntuple.histFileName'): 
                    line  = 'physics.analyzers.InitStntuple.histFileName : \"'+stn_fn+'"\n'

                if ((len(kfields) == 3) and kfields[0] == 'outputs') and (kfields[2] == 'fileName'):
                    #------------------------------------------------------------------------------
                    # make sure that the output DS name is defiend by init_project.py
                    #------------------------------------------------------------------------------
                    dsn        = words[1]
                    nstreams   = self.fJob.n_output_streams();
                    dsn_fields = []
                    self.Print(name,1,'nstreams:%i kfields[1]:%s line        :%s'%(nstreams,kfields[1],line.strip()))
                    for i in range(0,nstreams):
                        if (self.fJob.output_stream(i) == kfields[1]):
                            # redefine the dataset ID
                            dsn_fields    = dsn.split('.');
                            dsn_fields[2] = self.fJob.output_dsid(i)
                            # print('1: dsn_fields:',dsn_fields)
                            break

                    # print('2: dsn_fields:',dsn_fields)
                    line          = words[0]+":"+".".join(dsn_fields)
                    self.Print(name,1,'updated line:%s'%line)

                f1.write(line)     # substitute

            f.close()
            f1.close()
            # replace old file with the new one
            shutil.move(fn1,new_fn)
#------------------------------------------------------------------------------
# remake metadata (.json file)
#------------------------------------------------------------------------------
#        family='phy-etc'
#        if (self.fOwner != 'mu2e'): 
#            family = 'usr-etc'

#        cmd = 'setup dhtools; cd '+fcldir+'; for f in `ls *.fcl` ; do jsonMaker -f '+family+' -x $f ; done';
#        self.Print(name,1,'executing cmd:%s'%cmd)

#        process = subprocess.run(cmd,shell=True,capture_output=True,universal_newlines=True);

#        if (process.returncode != 0):
#            self.Print(name,0,"ERROR rc=%i in jsonMaker"%process.returncode)
#            print (process.stderr)
#            return -1;

        if ( not self.fNotar ):
#------------------------------------------------------------------------------
# create tarball: name the tarball according to Mu2e naming . self.fFileset
#------------------------------------------------------------------------------
            fcltop  = os.getcwd()+'/tmp/'+self.fProject+'/fcl'

            name_stub = fcltop+'/'+'cnf.'+self.fOwner +'.'+self.fIDsID+'.'+stage.name()+'_'+job.name()+'.'+self.fProject ;

            if (self.fFileset):
                tarfile = name_stub+'.%s.fcl.tbz'%self.fFileset;
            else:
                tarfile = name_stub+'.fcl.tbz';

            if (index >= 0): 
                tarfile = name_stub+".%03i.fcl.tbz"%index

            self.make_fcl_tarball(fcldir,tarfile);

        self.Print(name,1,'END')
        return 0;

#------------------------------------------------------------------------------
# generate fcl 
#------------------------------------------------------------------------------
    def gen_fcl(self,stage,job):
        name = 'gen_fcl'

        grid_dsid  = self.fProject+'.'+self.fIDsID+'_'+stage.name()+'_'+job.name();
        topdir     = '/pnfs/mu2e/scratch/users/'+self.fUser+'/workflow/'+grid_dsid+'/outstage/';

        if (self.fRecover):
            # in case of recovery, only need to tar up a bunch of FCL files 
            fcltop  = os.getcwd()+'/tmp/'+self.fProject+'/fcl'
            fcldir  = fcltop+'/'+self.fIDsID+'.'+stage.name()+'_'+job.name()+'.'+self.fRecover;
            tarfile = fcltop+'/cnf.'+self.fOwner+'.'+self.fIDsID+'.'+stage.name()+'_'+job.name()+'.'+self.fProject+'.'+self.fRecover+'.fcl.tbz'
            self.make_fcl_tarball(fcldir,tarfile);
            return

        #------------------------------------------------------------------------------
        # initial submission:
        # calculate the total number of segments and the number of jobs to be submitted 
        nsegments       = job.fNInputFiles/job.fMaxInputFilesPerSegment;
        if (nsegments*job.fMaxInputFilesPerSegment < job.fNInputFiles):
            nsegments   = nsegments+1

        njobs           = int(nsegments-1/job.fMaxSegments) + 1;
        #-----------------------------------------------------------------------------------------
        # check if a subdirectory named '000' exist locally, if it does, rename it, 
        # as generate_fcl creates and uses subdirectory with the name of '000'
        #-----------------------------------------------------------------------------------------
        for i in range(0,njobs):
            dname="%03i"%i
            if (os.path.exists(dname)): 
                letters = string.ascii_lowercase
                rs8  = ''.join(random.choice(letters) for i in range(8));
                shutil.move(dname,dname+'.'+rs8)

        #------------------------------------------------------------------------------
        # prepare and run generate_fcl
        stage      = self.fStage;                     # stage name  (s1, s2, s3 etc)
        jtype      = self.fJType;                     # job   name  (sim, stn)
        
        base_fcl   = job.fBaseFcl;
        run_number = job.fRunNumber;

        desc       = self.fIDsID+'_'+stage.name()+'_'+job.name();
        # dsconf     = self.fIDsID+'_'+stage.name()+'_'+job.name();
        dsconf     = self.fProject;

        input_file_list        = None;
        delete_input_file_list = None;
        nfiles                 = 0;
        ids                    = job.input_dataset()

        if (ids.defname() != 'generator'):
            if (ids.catalog() == 'local'):

                if (self.fFileset == None):
                    input_file_list = self.fProjectDir+'/catalog/'+ids.defname()+'.files';
                else:
                    input_file_list = self.fProjectDir+'/catalog/'+ids.defname()+'.files.'+self.fFileset;
                    
            else:
                if (self.fFileset == None):
                    sam_dimensions = 'dh.dataset '+ids.defname();
                else:
                    fileset        = ids.fileset(self.fFileset)
                    sam_dimensions = fileset.dimensions()

                if (self.fMinSubrun):
                    sam_dimensions +=' AND dh.first_subrun >= '+self.fMinSubrun+' AND dh.first_subrun < '+self.fMaxSubrun;

                cmd  = 'setup mu2efiletools; mu2eDatasetFileList '+ids.defname();

                self.Print(name,1,'executing : %s'%cmd);

                list = os.popen(cmd);
                # write temp file
                input_file_list = '/tmp/list_of_files.txt.'+'%i'%os.getpid()
                fout = open(input_file_list,'w')

                for line in list.readlines():
                    fout.write(line)

                fout.close()
                delete_input_file_list = 1

            f = open(input_file_list);
            for line in f.readlines():
                if (line[0] != '#'): nfiles = nfiles+1;

            self.Print(name,1,'n_input_files : %i'%nfiles);

        else:
            #------------------------------------------------------------------------------
            # generator , gen_fcl seems to be capable to generate multiple filesets
            #------------------------------------------------------------------------------
            nfiles = job.fNInputFiles

            if (self.fFileset):
                if (not self.fFirstSubrun):
                    # fileset is defined, the first subrun - is not
                    # so far, an assumptions that the fileset number is an integer works.
                    self.fFirstSubrun = job.fNInputFiles*int(self.fFileset)
            
        #------------------------------------------------------------------------------
        # define generate_fcl call parameters
        #------------------------------------------------------------------------------
        # cmd = 'setup mu2etools v3_05_00; export FHICL_FILE_PATH=$MU2E_BASE_RELEASE; ' 
        cmd = 'setup mu2etools; export FHICL_FILE_PATH=$MUSE_WORK_DIR; ' 
        cmd = cmd+'generate_fcl --description='+desc+' --dsconf='+dsconf+' --embed '+base_fcl;
        cmd = cmd+' --max-seed=50'

        if (self.fFirstSubrun): cmd = cmd+' --first-subrun=%i'%self.fFirstSubrun;

        if (job.fResample == 'no'):

            if (ids.defname() != 'generator'):
                cmd = cmd+' --merge=%i'%job.fMaxInputFilesPerSegment;  # integer
                cmd = cmd+' --inputs='+input_file_list;
            else:
                cmd = cmd+' --events=%i'%job.fNEventsPerSegment;
                cmd = cmd+' --njobs=%i'%nsegments;
                if (run_number) : cmd = cmd + ' --run-number=%i'%run_number;
        else:
            #------------------------------------------------------------------------------
            # case of resampling: assume 1 file per segment to resample
            # if fileset is defined, assume 1000 segments per fileset and define first subrun
            #------------------------------------------------------------------------------
            # nsegments=`cat $inputs | wc -l`
            
            if (run_number) : cmd = cmd+' --run-number='+'%i'%run_number;
            
            if (self.fFirstSubrun):
                cmd = cmd+' --first-subrun=%i'%self.fFirstSubrun

            cmd = cmd+' --events=%i'%job.fNEventsPerSegment;
            cmd = cmd+' --njobs=%i'%nfiles;
            cmd = cmd+' --auxinput=1:physics.filters.resamplingMixer.fileNames:'+input_file_list;

        if (job.fAuxInputs):
            #------------------------------------------------------------------------------
            # mixing
            #------------------------------------------------------------------------------
            
            for key in job.fAuxInputs.keys():
                # print ('key=',key)
                var                = job.fAuxInputs[key][0];
                dataset            = job.fAuxInputs[key][1];
                nfiles_per_segment = job.fAuxInputs[key][2];
                # now: get filelist - start from assuming a local list
                filelist = self.fProject+'/'+dataset.dsid_stub()+'/catalog/'+dataset.defname()+'.files'
                cmd = cmd+' --auxinput='+'%i'%nfiles_per_segment+':'+var+':'+filelist ;
           
        self.Print(name,1,"executing :%s"%cmd);

        process = subprocess.run(cmd,shell=True,capture_output=True,universal_newlines=True);

        self.Print(name,1,"generate_fcl DONE, return code = %i"%process.returncode);

        if (process.returncode != 0):
            self.Print(name,0,"ERROR rc=%i in generate_fcl"%process.returncode)
            print (process.stderr)
        else:
            if (delete_input_file_list): os.remove(input_file_list)

        #------------------------------------------------------------------------------
        # handle quirk of generate_fcl

        pattern='seeds.'+self.fOwner+'.'+desc+'.'+dsconf+'.*.txt'
        self.Print(name,1,'seed file pattern:%s'%pattern);

        seeds = glob.glob(pattern)

        # move seeds file into the first directory
        self.Print(name,1,'seeds file:%s'%seeds);

        shutil.move('./'+seeds[0],'000/'+seeds[0]);
        
        self.Print(name,1,"move_seeds DONE");
        #------------------------------------------------------------------------------
        # move fcl into a temporary FCL working firectory 
        # make sure we're not overwriting the existing directory
        #------------------------------------------------------------------------------
        istub=ids.id();
        if (job.fInputFileset): istub=istub+'_'+job.fInputFileset;

        fcldir=os.getcwd()+'/tmp/'+self.fProject+'/fcl/'+self.fIDsID+'.'+stage.name()+'_'+job.name();

        if (self.fFileset):
            fcldir=os.getcwd()+'/tmp/'+self.fProject+'/fcl/'+self.fIDsID+'.'+stage.name()+'_'+job.name()+'.'+self.fFileset;

        # Andrei stores up to 1000 segments per directory

        ndir = int((nsegments-1)/1000) + 1; 

        self.Print (name,1,'local temp directory: %s ndir:%i'%(fcldir,ndir));

        if (ndir == 1):

            if (os.path.exists(fcldir)):
                print(' WARNING: directory '+fcldir+' already exists, REMOVING and RECREATING !');
                shutil.rmtree(fcldir)

            shutil.move('000',fcldir)

            rc = self.postprocess_fcl_directory(fcldir,-1);
            if (rc < 0): 
                return rc

        else:
            # create more than one directory
            for idir in range(0,ndir):
                fcldir=os.getcwd()+'/tmp/'+self.fProject+'/fcl/'+self.fIDsID+'.'+stage.name()+'_'+job.name()+".%03i"%idir;

                if (os.path.exists(fcldir)):
                    print(' WARNING: directory '+fcldir+' already exists, REMOVING and RECREATING !');
                    shutil.rmtree(fcldir)

                shutil.move("%03i"%idir,fcldir)

                rc = self.postprocess_fcl_directory(fcldir,idir);
                if (rc != 0): 
                    return rc

#------------------------------------------------------------------------------
# main program, just make a GridSubmit instance and call its methods
#------------------------------------------------------------------------------
if (__name__ == '__main__'):

    x = Tool()
    x.ParseParameters()
    x.InitProject()

    stage = x.fStage;
    job   = stage.fJob[x.fJType];
    rc    = x.gen_fcl(stage,job)

    sys.exit(rc);
