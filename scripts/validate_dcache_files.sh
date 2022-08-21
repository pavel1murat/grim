#!/usr/bin/bash
#------------------------------------------------------------------------------
# validates input files , assumed to be located in DCACHE, defined in a given fcl file
#
# call format:  validate_dcache_files.sh  fcl_file
# parameters :
#              fcl_file : FCL file name fully qualified with the path
#
# reads input files defined in 'fcl_file' and copies them to /dev/null 
# using 'ifdh cp' to make sure they are readable
#-------------------------------------------------------------------------------
fcl_file=$1

setup ifdhc

export IFDH_GRIDFTP_EXTRA="-st 5"
export IFDH_CP_MAXRETRIES=1

for f in `cat $fcl_file | grep -v ^# | grep -v xroot: | grep /pnfs | sed 's/"//g' | sed 's/,//g'` ; do 
# for f in `cat $dir/$fcl_file | grep -v ^# | grep -v xroot: | grep /pnfs | sed 's#"/pnfs##g' | sed 's/"//g' | sed 's/,//g'` ; do 
#     fdcap="dcap://fndca1.fnal.gov:24136"$f
    echo $f
    ifdh cp $f /dev/null 
done
