#!/usr/bin/bash
#------------------------------------------------------------------------------
# process output of a grid job
# call format:
#              upload_grid_output.sh project idsid stage:job gridid1[,gridid2[,...] :art[:log]
#
# to archive everything in one go: 
#
#             upload_grid_output.sh project idsid stage:job grid_job_id :art:log
# 
# comment : we're not archiving the log files any more, instead, they are copied to 
#           /mu2e/data/users/$USER/$project area
#------------------------------------------------------------------------------

setup dhtools
setup mu2etools
setup mu2efiletools

project=$1
idsid=$2
stage=`echo $3 | awk -F : '{print $1}'`
jtype=`echo $3 | awk -F : '{print $2}'`

job_type=${stage}_${jtype}

gridjobid=$4 

ftypes=$5

rc=0

if [ $USER == "mu2epro" ] ; then dcache="persistent" ; else dcache="scratch" ; fi
				 
# echo ftypes=$ftypes
#------------------------------------------------------------------------------
# build names of the input directory (the one with the GRID job output)
# and the output directory - the one to copy the files over
#------------------------------------------------------------------------------
idir=/pnfs/mu2e/$dcache/users/$USER/workflow/$project.$idsid.$job_type/outstage/$gridjobid
odir=/mu2e/data/users/$USER/$project/$idsid.$job_type
if [ .`echo $ftypes | grep :log`  != "." ] ; then
#------------------------------------------------------------------------------
# saving log and fcl
# a) check that the log tarball has not been yet declared
#------------------------------------------------------------------------------
    tarball=log.mu2e.${idsid}_$job_type.$project.log.tbz
#------------------------------------------------------------------------------
# a_ copy fcl files
#------------------------------------------------------------------------------
    echo ----- copying fcl files
    
    if [ ! -d $odir/fcl ] ; then mkdir -p $odir/fcl ; fi
    
    for f in `ls $idir/00/*/* | grep .fcl$` ; do
	bn=`basename $f`
	cp $f $odir/fcl/$bn
    done
#------------------------------------------------------------------------------
# copy log files
#------------------------------------------------------------------------------
    echo ----- copying log files
    if [ ! -d $odir/log ] ; then mkdir -p $odir/log ; fi
    for f in `ls $idir/00/*/* | grep .log$` ; do
	bn=`basename $f`
	cp $f $odir/log/$bn
    done
#------------------------------------------------------------------------------
# make a single tarfile with the log and FCL and upload it , call it log
#------------------------------------------------------------------------------
    echo ----- making $tarball

    cd /mu2e/data/users/$USER
    
    tar -cjf $tarball $project/$idsid.$job_type/*
    
#    jsonMaker -f phy-etc -x $tarball
    printJson --no-parents $tarball  >| $tarball.json

    samweb get-metadata $tarball > /dev/null 2>&1
    rc=$?
    if [ $rc == "0" ] ; then
	echo ERROR: $tarball already have metadata declared to SAM, exit
	exit $rc
    fi

    echo $tarball.json | mu2eFileDeclare
    echo $tarball      | mu2eFileUpload --ifdh --tape
fi
#------------------------------------------------------------------------------
# ART files: 1) copy art.json files, strip "parents": [ .... ],
# $4(gridjobid) is a comma-separated list of grid job IDs
# handles correctly only one defname
#------------------------------------------------------------------------------
if [ .`echo $ftypes | grep :art`  != "." ] ; then

    for grid_id in `echo $gridjobid | sed 's/,/ /g'` ; do 

	idir=/pnfs/mu2e/$dcache/users/$USER/workflow/$project.$idsid.$job_type/outstage/$grid_id

	#     echo ----- processing art.json  files
	odd=$odir/art
	if [ ! -d $odd ] ; then mkdir -p $odd ; fi

	# loop over .art.json files, strip "parents": [ .... ],
	# ideally, at this point would like to skip failed segments
	# so far, do it by hand

	for f in `ls $idir/00/*/* | grep .art.json$` ; do
	    bn=`basename $f`
	    cat $f | awk '
BEGIN            {doit = 1} 
/"parents":/     {doit = 0}  
                 {if (doit == 1) {print $0}} 
/],/             {if (doit == 0) {doit = 1}}' >| $odd/$bn
	done

# MC files could be named either 'sim.' , or 'dig.' or 'mcs.'

	fn=`ls -l $odd | tail -n 1 | awk '{print $9}'`

	tier=`echo $fn | awk -F . '{print $1}'`
	owner=`echo $fn | awk -F . '{print $2}'`
	dsid=`echo $fn | awk -F . '{print $3}'`
	project=`echo $fn | awk -F . '{print $4}'`
	ftype=`echo $fn | awk -F . '{print $6g}'`

	defname=$tier.$owner.$dsid.$project.$ftype
	echo defname=$defname

	ls $odd/*.json | mu2eFileDeclare

	mu2eClusterFileList --dsname=$defname $idir | mu2eFileUpload --ifdh --tape
    done
fi
#------------------------------------------------------------------------------
# STNTUPLE files : declare them to disk
#------------------------------------------------------------------------------
if [ .`echo $ftypes | grep :stn`  != "." ] ; then
    echo ----- processing STNTUPLE  files
    odd=$odir/stn
    if [ ! -d $odd ] ; then mkdir -p $odd ; fi
    for f in `ls $idir/00/*/* | grep .stn$` ; do
	python su2020/scripts/jsonMakerPM.py -f phy-nts -x $f

	bn=`basename $f`

	   tier=`echo $bn | awk -F . '{print $1}'`
	  owner=`echo $bn | awk -F . '{print $2}'`
	   dsid=`echo $bn | awk -F . '{print $3}'`
	project=`echo $bn | awk -F . '{print $4}'`
	  ftype=`echo $bn | awk -F . '{print $6}'`

	defname=$tier.$owner.$dsid.$project.$ftype
	echo defname=$defname

	# ls $bn.json | mu2eFileDeclare

	echo $f | mu2eFileUpload --ifdh --disk
    done
fi
