#!/bin/bash

      d0=$1        # output directory, ie /pnfs/mu2e/scratch/users/murat/workflow/su2020.bmum0s00b0.s1_sim_e9/outstage/51726408/00/00000
old_dsid=$2        # old (wrong) DSID
new_dsid=$3        # new DSID
    doit=$4        # set to smth if want to execute

prefix="echo $LINENO: " ; if [ ".$4" != "." ] ; then prefix='' ; fi

pushd $d0  # cd to $d0, remember pwd in stack

for sd in `ls $d0`  ; do
# for sd in 00000 ; do
    d1=$d0/$sd
    echo "--- processing $d1, step 1: rename files"
    for f in `ls $sd/* | grep $old_dsid` ; do 
	f1=`echo $f | sed "s/$old_dsid/$new_dsid/g"`
	${prefix}mv $f $f1
    done

    echo "                    step 2: handle json files" 
    for f in `ls $sd/*.json | grep $old_dsid` ; do 
	f1=$f.tmp
	cat $f | sed "s/$old_dsid/$new_dsid/g" >| $f1
	${prefix}mv -f $f.tmp $f
    done
done

popd  # back to old pwd
