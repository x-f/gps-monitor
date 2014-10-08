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
log_timestamp = os.path.basename(log_file)[12:][:-4]

plot_path = "./data/" + log_timestamp
if len(sys.argv) > 2:
  plot_path = sys.argv[2]
print "plot_path=" + plot_path
os.system("mkdir -p " + plot_path)

plot_title = " (" + log_timestamp + "z)"
if len(sys.argv) > 3:
  plot_title = sys.argv[3]
print "plot_title=" + plot_title


file = open('./gnuplot-map.tmpl', 'r')
plot_template = file.read()
file.close()

plot_template = plot_template.replace("{{LOG_FILE}}", log_file)
plot_template = plot_template.replace("{{PLOT_PATH}}", plot_path)
plot_template = plot_template.replace("{{PLOT_TITLE}}", plot_title)

#print plot_template
open("./gnuplot-map.tmp", 'w').write(plot_template)

os.system("cat ./gnuplot-map.tmp | gnuplot >> ./gnuplot.out")
# -----------------
file = open('./gnuplot-graphs.tmpl', 'r')
plot_template = file.read()
file.close()

plot_template = plot_template.replace("{{LOG_FILE}}", log_file)
plot_template = plot_template.replace("{{PLOT_PATH}}", plot_path)
plot_template = plot_template.replace("{{PLOT_TITLE}}", plot_title)

open("./gnuplot-graphs.tmp", 'w').write(plot_template)

os.system("cat ./gnuplot-graphs.tmp | gnuplot >> ./gnuplot.out")
