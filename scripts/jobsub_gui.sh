#!/usr/bin/bash 

root.exe << EOF
.L su2020/scripts/jobsub_gui.C
jobsub_gui("su2020","crv01")
EOF
