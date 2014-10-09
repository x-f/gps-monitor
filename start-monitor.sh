#!/bin/bash

GPSMONITOR_DIR=/home/x-f/sw/gps-monitor
LOGFILE_DIR=/run/shm/gps-monitor

#GPSMONITOR_DIR=/sw/gps-mon
#LOGFILE_DIR=$GPSMONITOR_DIR/tmplogs
#export TZ="UTC"

cd $GPSMONITOR_DIR

PREVIOUS_PID=`cat ./monitor.pid`
if [ ! -z $PREVIOUS_PID ]; then
  echo -n "PREVIOUS_PID="
  echo $PREVIOUS_PID
  kill -SIGINT $PREVIOUS_PID
  sleep 2
  kill -9 $PREVIOUS_PID
else
  echo "no PREVIOUS_PID"
fi

mkdir -p $LOGFILE_DIR

TS=`date +%Y%m%d-%H`
LOGFILENAME="gps-monitor-${TS}.log"
LOGFILE="$LOGFILE_DIR/$LOGFILENAME"
# echo -n "ts="
# echo $TS
# echo -n "fn="
# echo $LOGFILENAME
echo -n "lf="
echo $LOGFILE

echo `date +%T`
python ./gps-monitor.py $LOGFILE # > /dev/null
echo -n "" > "./monitor.pid"
echo -n `date +%T`
echo "monitor stopped"

gzip -k $LOGFILE
mkdir -p ./data/$TS
mv $LOGFILE.gz ./data/$TS/log.gz

# plot $LOGFILE
python ./generate-plots.py $LOGFILE
sleep 10

# rm $LOGFILE
mv $LOGFILE $LOGFILE.rm

echo -n `date +%T`
echo "script exited"
