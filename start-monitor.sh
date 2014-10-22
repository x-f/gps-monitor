#!/bin/bash

GPSMONITOR_DIR=/home/pi/sw/gps-monitor
LOGFILE_DIR=/run/shm/gps-monitor

#GPSMONITOR_DIR=/sw/gps-mon
#LOGFILE_DIR=$GPSMONITOR_DIR/tmplogs
#export TZ="UTC"

cd $GPSMONITOR_DIR

PREVIOUS_PID=`cat $GPSMONITOR_DIR/monitor.pid`
#echo -n "PREVIOUS_PID="
#echo $PREVIOUS_PID
if [ ! -z $PREVIOUS_PID ]; then
  kill -SIGINT $PREVIOUS_PID #1>/dev/null 2>&1
  sleep 1
fi

mkdir -p $LOGFILE_DIR


TS_hours=`date +%H`
TS_tmp=$TS_hours
if [ $TS_tmp -lt 24 ]; then
  TS_hours="18"
fi
if [ $TS_tmp -lt 18 ]; then
  TS_hours="12"
fi
if [ $TS_tmp -lt 12 ]; then
  TS_hours="06"
fi
if [ $TS_tmp -lt 6 ]; then
  TS_hours="00"
fi

# TS=`date +%Y%m%d-%H`
TS=`date +%Y%m%d`
TS="$TS-$TS_hours"

LOGFILENAME="gps-monitor-${TS}.log"
LOGFILE="$LOGFILE_DIR/$LOGFILENAME"
# echo -n "ts="
# echo $TS
# echo -n "fn="
# echo $LOGFILENAME
echo -n "lf="
echo $LOGFILE

echo `date +%T`
python $GPSMONITOR_DIR/gps-monitor.py $LOGFILE # > /dev/null
# echo -n "" > $GPSMONITOR_DIR/monitor.pid
echo -n `date +%T`
echo "monitor stopped"

gzip -c $LOGFILE > $LOGFILE.gz
mkdir -p ./data/$TS
mv $LOGFILE.gz ./data/$TS/log.gz

# plot $LOGFILE
python $GPSMONITOR_DIR/generate-plots.py $LOGFILE
sleep 1

# rm $LOGFILE
# mv $LOGFILE $LOGFILE.rm

echo -n `date +%T`
echo " script exited"
