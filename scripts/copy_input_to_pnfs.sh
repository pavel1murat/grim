#!/usr/bin/bash
#------------------------------------------------------------------------------
# copy_input_to_pnfs.sh project idsid
#------------------------------------------------------------------------------
project=$1
  idsid=$2

   idir=/exp/mu2e/data/projects/$project/datasets/$idsid
   odir=/pnfs/mu2e/scratch/users/$USER/datasets/$project

rsync -vrutlog $idir $odir
