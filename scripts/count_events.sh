#!/usr/bin/bash
# count_events.sh project stage job idsid stream [fileset]

project=$1
  stage=$2
    job=$3
  idsid=$4
 stream=$5
fileset=$6

dir=/exp/mu2e/data/projects/$project/log/$idsid.${stage}_${job}
if [ ".$fileset" != "." ] ; then
    dir=$dir/$fileset
fi

for f in `ls $dir/*.log` ; do
    echo $f ;
done | wc

for f in `ls $dir/*.log` ; do
    cat $f | awk -v stream=$stream '{if (($1 == "TrigReport") && ($5 == stream)) print $2}'
done | awk '{n += $1} END{print n}'
