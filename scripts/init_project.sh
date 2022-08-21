#!/usr/bin/bash
#------------------------------------------------------------------------------
# initialize project subdirectories
#------------------------------------------------------------------------------
project=$1

if [ ! -d ./tmp/$project ] ; then mkdir ./tmp/$project ; fi

if [ ! -d ./tmp/$project/fcl             ] ; then mkdir ./tmp/$project/fcl             ; fi
if [ ! -d ./tmp/$project/grid_job_status ] ; then mkdir ./tmp/$project/grid_job_status ; fi
if [ ! -d ./tmp/$project/completed_jobs  ] ; then mkdir ./tmp/$project/completed_jobs  ; fi


# this should be it
