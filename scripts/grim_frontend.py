#!/usr/bin/env python
#------------------------------------------------------------------------------
# PM: GRIM Midas frontend : 
# frontend name : grim_fe
# with transition to spack, no longer need to update the PYTHONPATH
#------------------------------------------------------------------------------
import  ctypes, os, sys, datetime, random, time, traceback, subprocess
import  xmlrpc.client
import  inspect

import  midas
import  midas.frontend 
import  midas.event

import  TRACE
TRACE_NAME = "grim_fe"

# import grim.rc.control.farm_manager as farm_manager

# sys.path.append(os.environ["FRONTENDS_DIR"])
# from frontends.utils.runinfodb import RuninfoDB

#------------------------------------------------------------------------------
# GRIM 'equipment' is just a placeholder
# 'client' is the Midas frontend client which connects to ODB
#------------------------------------------------------------------------------
class GrimEquipment(midas.frontend.EquipmentBase):
    def __init__(self, client):
        TRACE.TRACE(TRACE.TLVL_DBG,"-- START",TRACE_NAME)
#------------------------------------------------------------------------------
# Define the "common" settings of a frontend. These will appear in
# /Equipment/MyPeriodicEquipment/Common. 
#
# Note: The values set here are only used the very first time this frontend/equipment 
#       runs; after that the ODB settings are used.
# You MUST call midas.frontend.EquipmentBase.__init__ in your equipment's __init__ method!
#------------------------------------------------------------------------------
        settings              = midas.frontend.InitialEquipmentCommon()
        settings.equip_type   = midas.EQ_PERIODIC
        settings.buffer_name  = "SYSTEM"
        settings.trigger_mask = 0
        settings.event_id     = 1
        settings.period_ms    = 10000
        settings.read_when    = midas.RO_RUNNING
        settings.log_history  = 1

        equip_name            = "grim_eq"
        midas.frontend.EquipmentBase.__init__(self, client, equip_name, settings)
#------------------------------------------------------------------------------
# set the status of the equipment (appears in the midas status page)
#------------------------------------------------------------------------------
        self.set_status("Initialized")
        TRACE.TRACE(TRACE.TLVL_LOG,":002: --- END equipment initialized",TRACE_NAME)
        return;

#-------^----------------------------------------------------------------------
# For a periodic equipment, this function will be called periodically
# (every 10 s in this case - see period_ms above). It should return either a `midas.event.Event`
# or None (if we do not write an event).
#------------------------------------------------------------------------------
    def readout_func(self):
        TRACE.TRACE(TRACE.TLVL_DBG+1,":001: -- START",TRACE_NAME)
        # In this example, we just make a simple event with one bank.

        # event = midas.event.Event()

        # Create a bank (called "MYBK") which in this case will store 8 ints.
        # data can be a list, a tuple or a numpy array.
        # data = [1,2,3,4,5,6,TRACE.TLVL_LOG,8]
        # event.create_bank("MYBK", midas.TID_INT, data)

        TRACE.TRACE(TRACE.TLVL_DBG+1,"-- END",TRACE_NAME)
        return None;        # event

#------------------------------------------------------------------------------
# FE name : 'grim_fe', to distinguish from the C++ frontend
#    A frontend contains a collection of equipment.
#    You can access self.client to access the ODB etc (see `midas.client.MidasClient`).
#------------------------------------------------------------------------------
class GrimFrontend(midas.frontend.FrontendBase):
#------------------------------------------------------------------------------
# define needed env variables
#------------------------------------------------------------------------------
    def __init__(self):
        TRACE.TRACE(TRACE.TLVL_LOG,"0010: START")
        midas.frontend.FrontendBase.__init__(self, "grim_fe")
        TRACE.TRACE(TRACE.TLVL_LOG,"0011: FrontendBase initialized")
#------------------------------------------------------------------------------
# determine active configuration
#------------------------------------------------------------------------------
        self._stop_run               = False;

        top_path                     = 'Mu2e/Offline/murat/grim_projects/pbar2m'
        self.output_dir              = os.path.expandvars(self.client.odb_get(top_path+'/TmpDir'));
        self.config_name             = 'pbar2m'
        self.cmd_top_path            = "/Mu2e/Commands/Grim"
        self.grim_odb_path           = "/Mu2e/Offline/murat/Grim"
#------------------------------------------------------------------------------
# redefine STDOUT
#------------------------------------------------------------------------------
        TRACE.TRACE(TRACE.TLVL_LOG,"0016: after get_logfile")
#------------------------------------------------------------------------------
# You can add equipment at any time before you call `run()`, but doing
# it in __init__() seems logical.
#-------v----------------------------------------------------------------------
        self.add_equipment(GrimEquipment(self.client))

#        TRACE.TRACE(TRACE.TLVL_LOG,"004: grim instantiated, self.use_runinfo_db=%i"%(self.use_runinfo_db))

        cmd=f"cat {os.getenv('MIDAS_EXPTAB')} | awk -v expt={os.getenv('MIDAS_EXPT_NAME')} '{{if ($1==expt) {{print $2}} }}'"
        process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        stdout, stderr = process.communicate();
        self.message_fn = stdout.decode('utf-8').split()[0]+'/grim.log';
#------------------------------------------------------------------------------
# GRIM frontend starts after the DTC-ctl frontends but before the cfo_emu_frontend(520)
#-----------------------------------------------------------------------------
        self.client.set_transition_sequence(midas.TR_START,510)
#------------------------------------------------------------------------------
# register hotlink
# try to change priority by re-registering the same callback
#------------------------------------------------------------------------------
        self.client.odb_watch(self.cmd_top_path+'/Run', self.process_command)
        # self.client.register_transition_callback(midas.TR_START, 502, self._tr_start_callback)

        return;

#------------------------------------------------------------------------------
# on exit, also kill the tail logfile process
#------------------------------------------------------------------------------
    def __del__(self):
        TRACE.TRACE(TRACE.TLVL_LOG,"001: destructor START",TRACE_NAME)

        TRACE.TRACE(TRACE.TLVL_LOG,"002: destructor END",TRACE_NAME)

#------------------------------------------------------------------------------
# This function will be called at the beginning of the run.
# You don't have to define it, but you probably should.
# You can access individual equipment classes through the `self.equipment`
# dict if needed.
#------------------------------------------------------------------------------
    def begin_of_run(self, run_number):

        self.set_all_equipment_status("Run starting", "yellow")

        TRACE.TRACE(TRACE.TLVL_LOG,"001:BEGIN_OF_RUN")

       
        self.set_all_equipment_status("Running", "greenLight")

        return midas.status_codes["SUCCESS"]

#------------------------------------------------------------------------------
#
#---v--------------------------------------------------------------------------
    def end_of_run(self, run_number):
        TRACE.TRACE(TRACE.TLVL_DBG,f'-- START: self.use_runinfo_db:{self.use_runinfo_db}')

        self.set_all_equipment_status("Finished", "greenLight")
        self.client.msg("Frontend has seen end of run number %d" % run_number)

        TRACE.TRACE(TRACE.TLVL_DBG,"-- END")
        return midas.status_codes["SUCCESS"]

#------------------------------------------------------------------------------
#        Most people won't need to define this function, but you can use
#        it for final cleanup if needed.
# need to break the loop of GrimFrontend::run
#---v--------------------------------------------------------------------------
    def frontend_exit(self):
        # breakpoint()
        TRACE.TRACE(TRACE.TLVL_LOG,"001:START : set self._stop_run = True")
        self._stop_run = True;
        TRACE.TRACE(TRACE.TLVL_LOG,"002: DONE")

    def send_message(self, message, message_type = midas.MT_INFO, facility="midas"):
        """
        Send a message into the midas message log.
        
        These messages are stored in a text file, and are visible on the the
        "messages" webpage.
        
        Args:
            * message (str) - The actual message.
            * is_error (bool) - Whether this message is informational or an 
                error message. Error messages are highlighted in red on the
                message page.
            * facility (str) - The log file to write to. Vast majority of
                messages are written to the "midas" facility.
        """
        
        # Find out where this function was called from. We go up
        # 1 frame in the stack to get to the lowest-level user
        # function that called us.
        # 0. fn_A()
        # 1. fn_B() # <--- Get this function
        # 2. midas.client.msg()
        caller     = inspect.getframeinfo(inspect.stack()[1][0])
        filename   = ctypes.create_string_buffer(bytes(caller.filename, "utf-8"))
        line       = ctypes.c_int(caller.lineno)
        routine    = ctypes.create_string_buffer(bytes(caller.function, "utf-8"))
        c_facility = ctypes.create_string_buffer(bytes(facility, "utf-8"))
        c_msg      = ctypes.create_string_buffer(bytes(message, "utf-8"))
        msg_type   = ctypes.c_int(message_type)
    
        self.client.lib.c_cm_msg(msg_type, filename, line, c_facility, routine, c_msg)


#------------------------------------------------------------------------------
    def process_cmd_configure(self,parameter_path):
        rc = 0;
        return rc;

#------------------------------------------------------------------------------
    def process_cmd_reset_output(self,parameter_path):
        file = open(self.message_fn, 'w');
        file.close();
        return 0;

#------------------------------------------------------------------------------
# TODO: handle parameters
# given that GRIM is a data member, no real need to send messages
# so this is just an exercise
#------------------------------------------------------------------------------
    def process_cmd_get_state(self,parameter_path):
        rc = 0;
        
        grim_url = f'http://mu2edaq22-ctrl.fnal.gov:{rpc_port}';   ## TODO - fix URL
        s   = xmlrpc.client.ServerProxy(grim_url)
        res = s.get_state("daqint")
        
        TRACE.TRACE(TRACE.TLVL_LOG,f'res:{res}',TRACE_NAME);
#-------^----------------------------------------------------------------------
# the remaining part - print output to the proper message stream ,
# reverting the line order
#-------v----------------------------------------------------------------------
        message = "";
        lines  = res.splitlines();
        for line in reversed(lines):
            message = message+line;

#        self.send_message(message,midas.MT_DEBUG,"grim");
        self.client.msg(message,0,"grim");
        return rc;
    
#------------------------------------------------------------------------------
# host    = 'all' : generate FCL's for all hosts
# process = 'all' : generate FCLs for all processes
#------------------------------------------------------------------------------
    def process_cmd_generate_fcl(self,parameter_path):
        rc = 0;
        
        TRACE.TRACE(TRACE.TLVL_INFO,f'-- START: parameter_path:{parameter_path}',TRACE_NAME);

        ppath          = parameter_path+'/generate_fcl'
        par            = self.client.odb_get(ppath);
        run_conf       = par["run_conf"];
        host           = par["host"    ];
        diag_level     = par["print_level"];

        cmd=os.getenv('MU2E_DAQ_DIR')+f'/config/scripts/generate_fcl.py --run_conf={run_conf} --host={host} --process={artdaq_process} --diag_level={diag_level}';
        p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,text=True)
        stdout, stderr = p.communicate();
#------------------------------------------------------------------------------
# write output
#------------------------------------------------------------------------------
        lines = stdout.split('\n');
        with open(self.message_fn,"a") as logfile:
            for line in reversed(lines):
                    logfile.write(line+'\n')
#------------------------------------------------------------------------------
# write error output, if any
#------------------------------------------------------------------------------
        if (stderr != ''):
            lines = stderr.split('\n');
            with open(self.message_fn,"a") as logfile:
                for line in reversed(lines):
                    logfile.write(line+"\n")

        TRACE.TRACE(TRACE.TLVL_INFO,f'-- END: run_conf:{run_conf} host:{host} ',TRACE_NAME);
        return rc;
    
#------------------------------------------------------------------------------
# FCL file is defined by the run configuration and the process, host is not needed
# usual steps:
# 1. set state to BUSY  (1:yellow)
# 2. print fcl file to grim.log
# 3. set state to READY (0:green)
#------------------------------------------------------------------------------
    def process_cmd_print_fcl(self,parameter_path):
        rc = 0;
        
        TRACE.TRACE(TRACE.TLVL_INFO,f'-- START: parameter_path:{parameter_path}',TRACE_NAME);

        ppath    = parameter_path+'/print_fcl'
        par      = self.client.odb_get(ppath);
        run_conf = par["run_conf"];
        host     = par["host"    ];
        process  = par["process" ];

        fcl_file = os.getenv("MU2E_DAQ_DIR")+f'/config/{run_conf}/{process}.fcl'
        
        TRACE.TRACE(TRACE.TLVL_DEBUG,f'fcl_file:{fcl_file} logfile:{self.message_fn}',TRACE_NAME);
#------------------------------------------------------------------------------
# remember that MIDAS displays the logfile in the reverse order
#------------------------------------------------------------------------------
        with open(fcl_file) as f:
            lines = f.readlines();
            with open(self.message_fn,"a") as logfile:
                for line in reversed(lines):
                    logfile.write(line)


        TRACE.TRACE(TRACE.TLVL_INFO,f'-- END',TRACE_NAME);
        return rc;
    
#-------v-----------------------------------------------------------------------
# process_command is called when odb['/Mu2e/Commands/DAQ/Grim/Run'] = 1
# in the end, it should set is back to zero
# a caller chould be first checking id Doit == 0 
#---v--------------------------------------------------------------------------
    def process_command(self, client, path, new_value):
        """
        callback : 
        """
        run      = self.client.odb_get(self.cmd_top_path+'/Run' )
        cmd_name = self.client.odb_get(self.cmd_top_path+'/Name')
        
        TRACE.TRACE(TRACE.TLVL_DEBUG,f'path:{path} cmd_name:{cmd_name} run:{run}',TRACE_NAME);
        if (run != 1):
#-------^----------------------------------------------------------------------
# likely, self-resetting the request
#------------------------------------------------------------------------------
            TRACE.TRACE(TRACE.TLVL_WARNING,f'{self.cmd_top_path}/Run:{run}, BAIL OUT',TRACE_NAME);
            return
#-------v----------------------------------------------------------------------
        parameter_path = self.client.odb_get(self.cmd_top_path+'/ParameterPath')
#------------------------------------------------------------------------------
# mark GRIM as busy
#------------------------------------------------------------------------------
        self.client.odb_set(self.grim_odb_path+'/Status',1)

        rc = 0;
        if   (cmd_name.upper() == 'INIT_PROJECT'):
            rc = self.process_cmd_configure(parameter_path);
        elif (cmd_name.upper() == 'GEN_FCL'):
            rc = self.client.stop_run(True);
        elif (cmd_name.upper() == 'SUBMIT_JOB'):
            rc = self.process_cmd_get_state(parameter_path);
        elif (cmd_name.upper() == 'PRINT_FCL'):
            rc = self.process_cmd_print_fcl(parameter_path);
        elif (cmd_name.upper() == 'RESET_OUTPUT'):
            rc = self.process_cmd_reset_output(parameter_path);
#------------------------------------------------------------------------------
# when done, set state to READY
#------------------------------------------------------------------------------
        self.client.odb_set(self.grim_odb_path+'/Status',0)

        return
    


if __name__ == "__main__":
#------------------------------------------------------------------------------
# The main executable is very simple:
# just create the frontend object, and call run() on it.
#---v--------------------------------------------------------------------------
    TRACE.Instance = "grim_fe".encode();

    TRACE.TRACE(TRACE.TLVL_LOG,"000: TRACE.Instance : %s"%TRACE.Instance,TRACE_NAME)
    with GrimFrontend() as fe:
        TRACE.TRACE(TRACE.TLVL_LOG,"001: in the loop",TRACE_NAME)
        fe.run()
        TRACE.TRACE(TRACE.TLVL_LOG,"002: after frontend::run",TRACE_NAME)
        

    TRACE.TRACE(TRACE.TLVL_LOG,"003: DONE, exiting")

        
