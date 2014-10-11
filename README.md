GPS monitor
--
A simple attempt to detect effects of CME impacts on Earth's ionosphere by monitoring GPS signals – for starters, just the wandering around of the reported position. Later individual GPS satellite signal monitoring might be added as well.  
Sample data – http://x-f.lv/dev/gps-monitor/  

Launch with `./start-monitor.sh`  
Add to crontab: `0 */6 * * * /home/x-f/sw/gps-monitor/start-monitor.sh`

`/run/shm` is a RAMdisk, it needs to be created by user. Alternatively, logging can be done on the regular filesystem. RAMdisk was chosen to reduce the wear of the SD card.  
This has been tested on a MK808 "minipc" (A9 dual core ARM CPU), however it should run equally well on the RaspberryPi. CPU usage is less than 3% with 1 Hz updates, 10-15% with 5 Hz, but there's likely no gain in that many position reports.

Requirements:
  * python2
  * py-serial
  * Gnuplot
  * GPS (setup commands are for Ublox GPS modules, but can be adapted for SiRF and others, there's nothing that important anyway)

TODO:
  * write a service and a log file rotator, to have the monitor running constantly and restart on failures
  * detect serial port change, if by any reason it has happened
  * web page
