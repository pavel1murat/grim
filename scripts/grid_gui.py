#!/usr/bin/env python
#
# Form implementation generated from reading ui file 'qt4_untitled_v01.ui'
#
# Created: Thu Jul 16 10:59:28 2020
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 

import sys, string, getopt, glob, os, time, re, array
import argparse, subprocess, shutil, glob, random, re

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        print('EMOE: Attribute Error')
        return QtGui.QApplication.translate(context, text, disambig)

#------------------------------------------------------------------------------
# my TAB class
#------------------------------------------------------------------------------
class MyTab :

    def __init__(self,mother,stage,job):

        self.fStage  = stage;
        self.fJob    = job;

        tab = QtGui.QWidget()
        tab.setObjectName(stage.name())
        mother.addTab(tab,"")

        name = stage.name()+':'+job.name()
        mother.setTabText(mother.indexOf(tab), name)
#------------------------------------------------------------------------------
# first group box: GRID
#------------------------------------------------------------------------------
        gb1 = QtGui.QGroupBox(tab)
        gb1.setGeometry(QtCore.QRect(10, 20, 300, 260))
        gb1.setObjectName("groupBox")
        gb1.setTitle("GRID")

        self.lbl_fileset = QtGui.QLabel(gb1)
        self.lbl_fileset.setText("fileset")
        self.lbl_fileset.setGeometry(QtCore.QRect(20,  20, 80, 25))

        self.fileset = QtGui.QLineEdit(gb1)
        self.fileset.setGeometry(QtCore.QRect(110, 20, 100, 25))
        self.fileset.setObjectName("fileset")

        # if (job
        # self.fileset.setText("")

        self.lbl_dsid = QtGui.QLabel(gb1)
        self.lbl_dsid.setText("dsid")
        self.lbl_dsid.setGeometry(QtCore.QRect(20,  50, 80, 25))

        self.dsid = QtGui.QLineEdit(gb1)
        self.dsid.setGeometry    (QtCore.QRect(110, 50, 100, 25))
        self.dsid.setObjectName("lineEdit")
        self.dsid.setText(job.input_dsid())

        self.lbl_grid_id = QtGui.QLabel(gb1)
        self.lbl_grid_id.setText("grid ID")
        self.lbl_grid_id.setGeometry(QtCore.QRect( 20, 80, 80, 25))

        self.grid_id = QtGui.QLineEdit(gb1)
        self.grid_id.setGeometry(QtCore.QRect    (110, 80, 100, 25))
        self.grid_id.setObjectName("lineEdit")
        self.grid_id.setText("")
#------------------------------------------------------------------------------
# second group box: SAM
#------------------------------------------------------------------------------
        gb2 = QtGui.QGroupBox(tab)
        gb2.setGeometry(QtCore.QRect(320, 20, 300, 260))
        gb2.setObjectName("groupBox2")
        gb2.setTitle("SAM")
 
        self.lbl_defname = QtGui.QLabel(gb2)
        self.lbl_defname.setText("defname")
        self.lbl_defname.setGeometry(QtCore.QRect(20, 20, 80, 25))

        self.defname = QtGui.QLineEdit(gb2)
        self.defname.setGeometry(QtCore.QRect    (110, 20, 150, 25))
        self.defname.setObjectName("lineEdit")
        self.defname.setText("")

        self.lbl_filename = QtGui.QLabel(gb2)
        self.lbl_filename.setText("filename")
        self.lbl_filename.setGeometry(QtCore.QRect(20, 50, 80, 25))

        self.filename = QtGui.QLineEdit(gb2)
        self.filename.setGeometry(QtCore.QRect    (110, 50, 150, 25))
        self.filename.setObjectName("lineEdit")
        self.filename.setText("")

#------------------------------------------------------------------------------
# output window ?
#------------------------------------------------------------------------------
#        txtEdit = QtGui.QPlainTextEdit(gb2)
#        txtEdit.setGeometry(QtCore.QRect(30, 200, 171, 31))
#        txtEdit.setObjectName("plainTextEdit")
#------------------------------------------------------------------------------
class GridWindow(QWidget):

    def __init__(self, *args): 

        
        QWidget.__init__(self)

        self.cmd         = None
        self.clb         = {} # buttons
        self.fListOfTabs = []
        self.fActiveTab  = None;
        self.fConfig     = args[0];

#------------------------------------------------------------------------------
# window itself : 890x650
#------------------------------------------------------------------------------
        self.setObjectName(_fromUtf8("su2020:ele00"))
        self.resize(920, 670)
        title = self.fConfig.fProject+':'+self.fConfig.fDsid;
        self.setWindowTitle(_translate("Form", title, None))
#------------------------------------------------------------------------------
# place command buttons on the right side of the main window
#------------------------------------------------------------------------------
        self.create_command_link_button(self,'gen_fcl'          ,  700,  30, 200, 30, self.gen_fcl          )
        self.create_command_link_button(self,'list_pnfs_output' ,  700,  62, 200, 30, self.list_pnfs_output )
        self.create_command_link_button(self,'submit_job'       ,  700,  94, 200, 30, self.submit_job       )
        self.create_command_link_button(self,'grid_monitor'     ,  700, 126, 200, 30, self.grid_monitor     )
        self.create_command_link_button(self,'catalog_stntuples',  700, 158, 200, 30, self.catalog_stntuples)

        self.create_command_link_button(self,'sam get-metadata' ,  700, 190, 200, 30, self.samweb_get_metadata )
        self.create_command_link_button(self,'sam list-files'   ,  700, 222, 200, 30, self.samweb_list_files   )
        self.create_command_link_button(self,'samweb --help'    ,  700, 254, 200, 30, self.samweb_help         )
        self.create_command_link_button(self,'build_tarball'    ,  700, 286, 200, 30, self.build_tarball       )
        self.create_command_link_button(self,'quit'             ,  700, 318, 200, 30, self.close               )

        self.checkBox = QtGui.QCheckBox(self)
        self.checkBox.setGeometry(QtCore.QRect(700, 350, 200, 30))
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.checkBox.setText("Grid/local")
#------------------------------------------------------------------------------
# create tab widget keeping all tabs
#------------------------------------------------------------------------------
        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setGeometry(QtCore.QRect(20, 10, 640, 335))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
#------------------------------------------------------------------------------
# text browser
#------------------------------------------------------------------------------
        self.tb = QtGui.QTextBrowser(self)
        self.tb.setGeometry(QtCore.QRect(10, 390, 900, 290))
        self.tb.setObjectName("textBrowser")

#------------------------------------------------------------------------------
    def create_command_link_button(self, mother,name,x0,y0,dx,dy,func):
        b = QtGui.QCommandLinkButton(self);
        b.setGeometry(QtCore.QRect(x0, y0, dx, dy))
        b.setObjectName('b['+name+']')
        b.setText(name)
        b.clicked.connect(func)
      
        self.clb[name] = b;


    def set_curent_tab(self):
      tab = self.sender()
      print(tab.text())

#------------------------------------------------------------------------------
    def addNewTab(self, tab_widget,stage,job):

        tab = MyTab(tab_widget,stage,job); 
        self.fListOfTabs.append(tab)


#------------------------------------------------------------------------------
    def button_clicked(self):
        b = self.sender()
        print ("clicked button is ",b.text())

#------------------------------------------------------------------------------
    def catalog_stntuples(self):
        b = self.sender()
        print ("CATALOG_STNTUPLEs: ",b.text())

#------------------------------------------------------------------------------
    def samweb_list_files(self):
        b = self.sender()
        print ("SAMWEB_LIST_FILEs: ",b.text())

#------------------------------------------------------------------------------
    def samweb_get_metadata(self):
        b = self.sender()
        print ("SAMWEB_GET_METADATA: ",b.text())

#------------------------------------------------------------------------------
    def samweb_help(self):
        b = self.sender()
        print ("SAMWEB_HELP: ",b.text())

#------------------------------------------------------------------------------
    def list_pnfs_output(self):
        b = self.sender()

        index   = self.tabWidget.currentIndex();  # hopefully, current tab
        tab     = self.fListOfTabs[index];

        fileset = str(tab.fileset.text())
        grid_id = str(tab.grid_id.text())


        print('tab.fileset.text:',fileset, 'grid_id:',grid_id)

        cmd   = ['su2020/scripts/list_pnfs_output.py', '--grid_id=',grid_id, '--verbose=','1'];


        if (fileset != ''):
            cmd.append(' --fileset=%03i'%int(fileset))
            
        print ("LIST_PNFS_OUTPUT: ",cmd, tab.fStage.name(), tab.fJob.name())

        print('checkBox:', self.checkBox.isChecked())

        print_only=1
        self.execute_command(cmd,print_only)
        print ("LIST_PNFS_OUTPUT: ",b.text())

#------------------------------------------------------------------------------
    def submit_job(self):
        b = self.sender()
        print ("SUBMIT_JOB: ",b.text())

#------------------------------------------------------------------------------
    def build_tarball(self):
        b = self.sender()

        index = self.tabWidget.currentIndex();  # hopefully, current tab

        tab = self.fListOfTabs[index];

        cmd = ['su2020/scripts/build_tarball.py', '--project',self.fConfig.fProject,'--verbose','1'];

        txt = str(tab.fileset.text())
        print('tab.fileset.text:',txt)
        if (txt != ''):
            cmd.append(' --fileset=%03i'%int(txt))
            
        print ("BUILD_TARBALL: ",cmd, tab.fStage.name(), tab.fJob.name())

        print_only=0
        self.execute_command(cmd,print_only)

#------------------------------------------------------------------------------
    def gen_fcl(self):
        b = self.sender()

        index = self.tabWidget.currentIndex();  # hopefully, current tab

        tab = self.fListOfTabs[index];

        cmd = ['setup python v3_7_2; su2020/scripts/gen_fcl.py --project='+self.fConfig.fProject,
               ' --dsid='+self.fConfig.fDsid,' --stage='+tab.fStage.name(),
               ' --job='+tab.fJob.name(),' --verbose=1']
        
        txt = str(tab.fileset.text())
        print('tab.fileset.text:',txt)
        if (txt != ''):
            cmd.append(' --fileset='+'03i'%int(txt))
            
 #       print ("GEN_FCL: ",cmd, tab.fStage.name(), tab.fJob.name())

        print_only=0
        self.execute_command(cmd,print_only)

#------------------------------------------------------------------------------
    def grid_monitor(self):
        b = self.sender()
        print ("GRID_MONITOR: ",b.text())

        index = self.tabWidget.currentIndex();  # hopefully, current tab

        tab = self.fListOfTabs[index];

        cmd = ['su2020/scripts/grid_monitor.py','--project='+self.fConfig.fProject]

        print ("GRID_MONITOR: ",cmd)

        print_only=0
        self.execute_command(cmd,print_only)


#------------------------------------------------------------------------------
    def execute_command(self,cmd,print_only):
        
        line = format("# %s : --------- GridGui::ExecuteCommand : %s"%(time.ctime(),cmd))
        self.tb.append(line)

        if (print_only == 0):

#           process = subprocess.run(parms, capture_output=True, universal_newlines=True)  # python 3
#           print('process.return_code: ',process.returncode);
#           submission_record = process.stdout.split('\n')
#           print(submission_record)

            cmdd = ''.join(cmd);
            p = subprocess.Popen(cmdd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)  # python 2

            output, err = p.communicate(b"input data that is passed to subprocess' stdin")

            print('process.return_code: ',p.returncode);

            for line in output.split('\n'):
                print(line)

            if (err):
                print('ERROR:')
                for line in err.split('\n'):
                    print(line)

            self.tb.append(output)
       
        line = format("# %s : --------- GridGui::ExecuteCommand : DONE"%time.ctime());
        self.tb.append(line)


#------------------------------------------------------------------------------
class Tab:
    def __init__(self,window,name):
         x=0

#------------------------------------------------------------------------------
class GridGui:

    def __init__(self):
        self.fProject       = None
        self.fProjectDir    = None
        self.fDsid          = 'xxx_xxxx' # just to make up 
        self.fJob           = None       # task to be executed
        self.fStageName     = None
        self.fJType         = None
        self.fMinSubrun     = None
        self.fMaxSubrun     = None
        self.fUser          = os.getenv('USER')
        self.fRecoveryStep  = None;
        self.fFileset       = None;
        self.fConfig        = {}
        self.fIDsID         = None;
        self.fTab           = {}

        self.fOwner         = os.getenv('USER');
        if (self.fOwner == 'mu2epro'): self.fOwner = 'mu2e';
        
        self.fVerbose       = 0
        self.fWindow        = None;

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
        
        # self.Print(name,2,'Starting')
        # self.Print(name,2, '%s' % sys.argv)


        parser = argparse.ArgumentParser(description='Videos to images')

        parser.add_argument('--project' , type=str, help='project name'  , default = None)
        parser.add_argument('--dsid'    , type=str, help='dataset family', default = None)
        parser.add_argument('--job'     , type=str, help='job name'      , default = 's1')
        parser.add_argument('--stage'   , type=str, help='stage'         , default = 's1')
        parser.add_argument('--doit'    , type=str, help='unused'        , default = 's1')
        parser.add_argument('--fileset' , type=str, help='unused'        , default = 's1')
        parser.add_argument('--lumi'    , type=str, help='b1 or b2'      , default = None)
        parser.add_argument('--recover', type=str, help='unused'        , default = None)
        parser.add_argument('--subruns' , type=str, help='unused'        , default = None)
        parser.add_argument('--verbose' , type=int, help='verbose'       , default = 0   )

        args = parser.parse_args()


        self.fProject      = args.project
        self.fDsid         = args.dsid
        self.fJType        = args.job
        self.fFileset      = args.fileset
        self.fLumi         = args.lumi
        self.fRecoveryStep = args.recover
        self.fVerbose      = args.verbose
        self.fStageName    = args.stage

        if (args.subruns):
            self.fMinSubrun = args.subruns.split(':')[0]
            self.fMaxSubrun = args.subruns.split(':')[1]
        
        self.fProjectDir = self.fProject+'/'+self.fDsid[0:5];

        self.Print(name,1,'Job        = %s' % self.fJob    )
        self.Print(name,1,'Project    = %s' % self.fProject)
        self.Print(name,1,'Lumi       = %s' % self.fLumi   )
        self.Print(name,1,'Verbose    = %s' % self.fVerbose)
        self.Print(name,1,'Dsid       = %s' % self.fDsid      )
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

        # step 1: need to generate fcl files 
        projectName         = self.fProject;
        dsid                = self.fDsid;
        
        self.Print(name,1,'projectName   = %s' % projectName)
        self.Print(name,1,'dsid          = %s' % dsid)
        self.Print(name,1,'stage         = %s' % self.fStageName)
        #        self.Print(name,1,'job           = %s' % self.fJob.name())


#------------------------------------------------------------------------------
    def initGui(self):
        name = 'initGui'

        config = self.fConfig;

        self.fWindow = GridWindow(self,config)

        for sname in sorted(config.fStage.keys()):
            stage = config.fStage[sname]
            print ('stage: ',sname)

            for jname in sorted(stage.fJob.keys()):
                job = stage.job(jname);
                ok = 1;
                if (self.fLumi):
                    ok = 0
                    pattern='_'+self.fLumi+'$';        # like '_b1' in the end of job name
                    print('pattern,jname:',pattern,jname)
                    if (re.search(pattern,jname) != None): 
                        ok = 1
                print('ok: ',ok)
                if (ok):
                    name = stage.name()+':'+job.name()
                    self.fTab[name] = Tab(self.fWindow,name)
                    self.fWindow.addNewTab(self.fWindow.tabWidget,stage,job)
        #------------------------------------------------------------------------------
        # set index of the current tab - starting form 0 ? 

        self.fWindow.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self.fWindow)

#------------------------------------------------------------------------------
# main program, just make a GridGui instance and call its methods
#------------------------------------------------------------------------------
if (__name__ == '__main__'):

    app = QtGui.QApplication(sys.argv)

    x  = GridGui()

    x.ParseParameters()
    x.InitProject()
    x.initGui()

    x.fWindow.show();

    sys.exit(app.exec_())


