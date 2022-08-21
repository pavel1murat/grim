#!/bin/bash
#
# store first 8 characters of the last git commit in ./.base_commit file of the test release
#
git log -1 | grep commit | awk '{print substr($2,0,8)}' >| ./.base_commit
