#!/usr/bin/python2

import sys, os

if len(sys.argv) == 1:
  print "no logfile specified"
  sys.exit()

log_file = sys.argv[1]
print "log_file=" + log_file

# log timestamp
# /run/shm/gps-monitor/gps-monitor-20141007-06.log
#                                  |---------|
log_timestamp = os.path.basename(log_file)[12:23]
print log_timestamp

from datetime import datetime, timedelta
ts_start = datetime.strptime(log_timestamp, '%Y%m%d-%H')
ts_end = ts_start + timedelta(hours=6)
log_timestamp_start = ts_start.strftime("%Y-%m-%d %H:00:00")
log_timestamp_end = ts_end.strftime("%Y-%m-%d %H:00:00")

plot_path = "./data/" + log_timestamp
if len(sys.argv) > 2:
  plot_path = sys.argv[2]
print "plot_path=" + plot_path
os.system("mkdir -p " + plot_path)

plot_title = " (" + log_timestamp + "z)"
if len(sys.argv) > 3:
  plot_title = sys.argv[3]
print "plot_title=" + plot_title

# -----------------

file = open('./gnuplot-map.tmpl', 'r')
plot_template = file.read()
file.close()

plot_template = plot_template.replace("{{LOG_FILE}}", log_file)
plot_template = plot_template.replace("{{PLOT_PATH}}", plot_path)
plot_template = plot_template.replace("{{PLOT_TITLE}}", plot_title)

open("./gnuplot-map.tmp", 'w').write(plot_template)
os.system("cat ./gnuplot-map.tmp | gnuplot")

# -----------------

file = open('./gnuplot-graphs.tmpl', 'r')
plot_template = file.read()
file.close()

plot_template = plot_template.replace("{{LOG_FILE}}", log_file)
plot_template = plot_template.replace("{{PLOT_PATH}}", plot_path)
plot_template = plot_template.replace("{{PLOT_TITLE}}", plot_title)
plot_template = plot_template.replace("{{LOG_TS_START}}", log_timestamp_start)
plot_template = plot_template.replace("{{LOG_TS_END}}", log_timestamp_end)

open("./gnuplot-graphs.tmp", 'w').write(plot_template)
os.system("cat ./gnuplot-graphs.tmp | gnuplot")
