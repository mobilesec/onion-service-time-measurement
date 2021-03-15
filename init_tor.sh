##!/bin/bash

# get parameter
while getopts ":v:t:i:" opt; do
  case $opt in
    v) version="$OPTARG"
    ;;
    t) timeout="$OPTARG"
    ;;
    i) num_intro="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

if [ -z ${version} ] || [ -z ${timeout} ] || [ -z  ${num_intro} ];
then
        echo -e "\t\nUsage:\nbash init_tor.sh -v VERSION -t TIMEOUT -i NUM_INTRO_POINTS\n"
        echo -e "\t3: Ephemeral Onion Service Version 3\n"
        echo -e "\t3NE: Non-ephemeral Onion Service Version 3\n"
        echo -e "\t3VN: Ephemeral Onion Service with Vanguards Version 3\n"
        echo -e "\t2: Ephermeral Onion Service Version 2\n"
	echo -e "\tTIMEOUT: Timout in seconds\n"
	echo -e "\tNUM_INTRO_POINTS: Number of Introduction Points used\n"
        exit 1
else
   # start tor
   tor -f /etc/tor/torrc --quiet &

   export PYTHONPATH="/home/timing-analysis"
   case "$version" in
        3)      python3 /home/timing-analysis/analysis/startAnalysis.py 3 "True" ${timeout} ${num_intro}
        ;; 
        3NE)    python3 /home/timing-analysis/analysis/startAnalysis.py 3 "False" ${timeout} ${num_intro}
        ;;
        3VN)    vanguards --config /etc/tor/vanguards.conf &
                python3 /home/timing-analysis/analysis/startAnalysis.py 3 "True" ${timeout} ${num_intro}
        ;;
        2)      python3 /home/timing-analysis/analysis/startAnalysis.py 2 "False" ${timeout} ${num_intro}
        ;; 
        *)      echo -e "Version can only be [2]|[3]|[3NE]|[3VN]"
                exit 1
        ;;
        esac
   # copy result file
   cp /tmp/provisioning_time* /results
fi
