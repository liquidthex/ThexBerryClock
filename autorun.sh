#!/bin/bash
 
gitcmd="git pull --rebase"
success=" is up to date.$"
verbose=0 # Set to 1 if you want to see output
 
# We can't test directly with pipes, so save an output file
# See http://stackoverflow.com/questions/22491988/why-does-git-pull-fail-with-signal-13
 
tmpfile="/tmp/.gitpull.$$"
${gitcmd} 2>&1 > ${tmpfile}
if [ ${verbose} -gt 0 ]; then
  cat ${tmpfile}
fi
test=`grep "${success}" "${tmpfile}"`
rm "${tmpfile}"
 
if [ ! -z "${test}" ]; then   # If there is NOT new code to update...
  exit 0
else # There IS new code to update
  echo "Here is where you would do a kill or something."
  exit 1  # Or just catch this exit code when you call this, and then the script calling this knows the code has been updated.
fi
