#!/usr/bin/env ruby
#------------------------------------------------------------------------------
# parse log files and create an ascii file with the GRID job timing data 
# to be processed by su2020/scripts/grid_time_ana.C
#
# example: 
# --------
# grim/scripts/parse_grid_logs.rb -p ts_warm_bore -d 711_1010 -s s1 -j job [ --fileset=000] 
#
# output os stored in the xxx/timing_data subdirectory , at the same level as xxx/log
#
# comment: a bit kludgy, at this point, but works
#------------------------------------------------------------------------------
# puts "starting---"

require 'find'
require 'fileutils'
require 'getoptlong'

# puts " emoe"
#-----------------------------------------------------------------------
def usage
  puts "usage: parse_grid_logs -d dsid [-v] "
  exit(-1)
end
#------------------------------------------------------------------------------
# specify defaults for the global variables and parse command line options
#------------------------------------------------------------------------------

opts = GetoptLong.new(
  [ "--dsid"          , "-d",     GetoptLong::REQUIRED_ARGUMENT ],
  [ "--fileset"       , "-f",     GetoptLong::REQUIRED_ARGUMENT ],
  [ "--job"           , "-j",     GetoptLong::REQUIRED_ARGUMENT ],
  [ "--project"       , "-p",     GetoptLong::REQUIRED_ARGUMENT ],
  [ "--stage"         , "-s",     GetoptLong::REQUIRED_ARGUMENT ],
  [ "--verbose"       , "-v",     GetoptLong::NO_ARGUMENT       ]
)
#----------------------------- defaults
$dsid    = nil
$fileset = nil
$job     = nil
$project = nil
$stage   = nil
$verbose = 0

opts.each do |opt, arg|
  if    (opt == "--dsid"          ) ; $dsid     = arg
  elsif (opt == "--fileset"       ) ; $fileset  = arg
  elsif (opt == "--job"           ) ; $job      = arg
  elsif (opt == "--project"       ) ; $project  = arg
  elsif (opt == "--stage"         ) ; $stage    = arg
  elsif (opt == "--verbose"       ) ; $verbose  = 1
  end

  if ($verbose != 0) ; puts "Option: #{opt}, arg #{arg.inspect}" ; end
end

#------------------------------------------------------------------------------
def run(dsid)

  dir = "/mu2e/data/users/"+ENV["USER"]+"/"+$project+"/"+$dsid+"."+$stage+'_'+$job ;
  if ($fileset) then dir = dir + '/' + $fileset; end
  puts "dir = #{dir}"
#------------------------------------------------------------------------------
# oen output file
#------------------------------------------------------------------------------
  odir = dir+'/timing_data'
  if (not File.exist?(odir)) then FileUtils.mkdir_p(odir) ; end 

  ofn = dir+'/timing_data/'+$project+'.'+$dsid+'.'+$stage+'_'+$job+'.txt';
  of  = File.open(ofn,'w');
#------------------------------------------------------------------------------
# write ntuple format string
#------------------------------------------------------------------------------
  of.printf ("jobid/I:node_name/C:cpu_id/C:bogomips/F:dsid/C:vmpeak/F:vmhwm/F:tstage/I:totcpu/I:totwall/I:tfull/F:tistn/F:tkffpar/F:tkffdar/F\n");

  for fn in Dir.glob("#{dir}/log/*.log") do
    #    puts "-----------------"+fn

    f = File.open(fn);

    start_time    = ""  ;
    wall_time     = -1  ;
    cpu_time      = -1  ;
    stage_in_time = -1  ;
    full_evt_time = -1.0;
    kffpar_time   = -1.0;
    kffdar_time   = -1.0;
    init_stn_time = -1.0;

    job_id        = -1          ;
    vendor_id     = "undefined" ;
    bogomips      = -1          ;
    node_name     = "undefined" ;

    vmpeak        = -1.0;
    vmhwm         = -1.0;

    f.each_line { |line|
      if (line.index("Starting on host ")) then
        # puts line
        words = line.strip.split(" ");
        start_time = words[19]+" "+words[20]+" "+words[21]+" "+words[22]+" "+words[23];
      elsif line.index("# Total stage-in time:") then
        words         = line.strip.split(" ");
        stage_in_time = words[10].to_i;
      elsif line.index("TimeReport CPU =") then
        words     = line.strip.split(" ");
        cpu_time  = words[3].to_f;
        wall_time = words[6].to_f;
      elsif line.index("MemReport  VmPeak =") then
        words   = line.strip.split(" ");
        vmpeak  = words[3].to_f;
        vmhwm   = words[6].to_f;
      elsif line.index("Full event  ") then
        full_evt_time = line.strip.split(" ")[3].to_f;
      elsif line.index("p2:InitStntuple:InitStntuple") then
        init_stn_time = line.strip.split(" ")[2].to_f;
      elsif line.index("p2:KFFDeMHPar:KalFinalFit") then
        kffpar_time = line.strip.split(" ")[2].to_f;
      elsif line.index("p2:KFFDeMHDar:KalFinalFit") then
        kffdar_time = line.strip.split(" ")[2].to_f;
      elsif (line.index("poms_data") == 0) then
#------------------------------------------------------------------------------
# grid job information
# ["campaign_id:", "task_definition_id:", "task_id:", "job_id:", "batch_id:15514434.0@jobsub02.fnal.gov", \
#  "host_site:", "bogomips:4599.37", "node_name:murat-15514434-0-fnpc7008.fnal.gov", "vendor_id:AuthenticAMD"]
#------------------------------------------------------------------------------
        ww = line.split('=')[1].gsub('"','').gsub('{','').gsub('}','').split(',');
        for w in ww do
          w1 = w.split(':');
          if    (w1[0] == "batch_id" ) then job_id    = w1[1].split('.')[0];
          elsif (w1[0] == "bogomips" ) then bogomips  = w1[1];
          elsif (w1[0] == "node_name") then node_name = w1[1].split('-')[3];
          elsif (w1[0] == "vendor_id") then vendor_id = w1[1].strip;
          end
        end
      end
    }

#    puts "stage_in_time: #{stage_in_time}", cpu_time, wall_time, full_evt_time, kffpar_time, kffdar_time, init_stn_time;

    of.printf(" %11s %-19s %-12s %8s %9s %9.3f %9.3f %6i %8.0f %8.0f %8.4f %8.4f %8.4f %8.4f\n",
              job_id, node_name, vendor_id, bogomips, dsid, 
              vmpeak, vmhwm, 
              stage_in_time, cpu_time, wall_time, full_evt_time, init_stn_time, kffpar_time, kffdar_time );

    f.close
  end

  of.close();
end


run($dsid);

exit(0)
