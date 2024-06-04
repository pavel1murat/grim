#!/usr/bin/bash 

root.exe << EOF
.L grim/scripts/jobsub_gui.C
jobsub_gui("su2020","crv01")
EOF
