#!/bin/bash

for i in {1..15}
do
	echo $i
	timeout -s SIGINT 150s python3 run.py assignment_Michal.py
	exit_status=$?
	if [[ $exit_status -eq 124 ]]; then
		echo "Fail" >> MichalProgramTime.txt
	fi
done
