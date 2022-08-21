#!/usr/bin/bash
#------------------------------------------------------------------------------
# given a dataset definition, count total number of events in it
#
# call format: 
#                      sam_count_events defname
# parameters:
# -----------
# defname: SAM dataset definition
#------------------------------------------------------------------------------
dataset=$1  # SAM dataset definition

for f in `samweb list-file-locations --defname=$dataset | awk '{print $2}'` ; do
    #    echo $f
    samweb get-metadata $f | grep 'Event Count:' | awk '{print $3}'
done | awk '{n +=$1} END{print n}'
